import binascii
import logging
import sys
from base64 import b64decode
from unittest import TestCase
from uuid import UUID

from parameterized import parameterized, param

from hvac import exceptions
from hvac.tests import utils


class TestSystemBackend(utils.HvacIntegrationTestCase, TestCase):

    def test_unseal_multi(self):
        cls = type(self)

        self.client.seal()

        keys = cls.manager.keys

        result = self.client.unseal_multi(keys[0:2])

        self.assertTrue(result['sealed'])
        self.assertEqual(result['progress'], 2)

        result = self.client.unseal_reset()
        self.assertEqual(result['progress'], 0)
        result = self.client.unseal_multi(keys[1:3])
        self.assertTrue(result['sealed'])
        self.assertEqual(result['progress'], 2)
        self.client.unseal_multi(keys[0:1])
        result = self.client.unseal_multi(keys[2:3])
        self.assertFalse(result['sealed'])

    def test_seal_unseal(self):
        cls = type(self)

        self.assertFalse(self.client.is_sealed())

        self.client.seal()

        self.assertTrue(self.client.is_sealed())

        cls.manager.unseal()

        self.assertFalse(self.client.is_sealed())

    def test_ha_status(self):
        self.assertIn('ha_enabled', self.client.ha_status)

    def test_wrap_write(self):
        if 'approle/' not in self.client.list_auth_backends():
            self.client.enable_auth_backend("approle")

        self.client.write("auth/approle/role/testrole")
        result = self.client.write('auth/approle/role/testrole/secret-id', wrap_ttl="10s")
        self.assertIn('token', result['wrap_info'])
        self.client.unwrap(result['wrap_info']['token'])
        self.client.disable_auth_backend("approle")

    def test_auth_backend_manipulation(self):
        self.assertNotIn('github/', self.client.list_auth_backends())

        self.client.enable_auth_backend('github')
        self.assertIn('github/', self.client.list_auth_backends())

        self.client.token = self.manager.root_token
        self.client.disable_auth_backend('github')
        self.assertNotIn('github/', self.client.list_auth_backends())

    def test_secret_backend_manipulation(self):
        self.assertNotIn('test/', self.client.list_secret_backends())

        self.client.enable_secret_backend('generic', mount_point='test')
        self.assertIn('test/', self.client.list_secret_backends())

        secret_backend_tuning = self.client.get_secret_backend_tuning('generic', mount_point='test')
        self.assertEqual(secret_backend_tuning['max_lease_ttl'], 2764800)
        self.assertEqual(secret_backend_tuning['default_lease_ttl'], 2764800)

        self.client.tune_secret_backend('generic', mount_point='test', default_lease_ttl='3600s', max_lease_ttl='8600s')
        secret_backend_tuning = self.client.get_secret_backend_tuning('generic', mount_point='test')

        self.assertIn('max_lease_ttl', secret_backend_tuning)
        self.assertEqual(secret_backend_tuning['max_lease_ttl'], 8600)
        self.assertIn('default_lease_ttl', secret_backend_tuning)
        self.assertEqual(secret_backend_tuning['default_lease_ttl'], 3600)

        self.client.remount_secret_backend('test', 'foobar')
        self.assertNotIn('test/', self.client.list_secret_backends())
        self.assertIn('foobar/', self.client.list_secret_backends())

        self.client.token = self.manager.root_token
        self.client.disable_secret_backend('foobar')
        self.assertNotIn('foobar/', self.client.list_secret_backends())

    def test_audit_backend_manipulation(self):
        self.assertNotIn('tmpfile/', self.client.list_audit_backends())

        options = {
            'path': '/tmp/vault.audit.log'
        }

        self.client.enable_audit_backend('file', options=options, name='tmpfile')
        self.assertIn('tmpfile/', self.client.list_audit_backends())

        self.client.token = self.manager.root_token
        self.client.disable_audit_backend('tmpfile')
        self.assertNotIn('tmpfile/', self.client.list_audit_backends())

    def test_policy_manipulation(self):
        self.assertIn('root', self.client.list_policies())
        self.assertIsNone(self.client.get_policy('test'))
        policy, parsed_policy = self.prep_policy('test')
        self.assertIn('test', self.client.list_policies())
        self.assertEqual(policy, self.client.get_policy('test'))
        self.assertEqual(parsed_policy, self.client.get_policy('test', parse=True))

        self.client.delete_policy('test')
        self.assertNotIn('test', self.client.list_policies())

    def test_json_policy_manipulation(self):
        self.assertIn('root', self.client.list_policies())

        policy = {
            "path": {
                "sys": {
                    "policy": "deny"
                },
                "secret": {
                    "policy": "write"
                }
            }
        }

        self.client.set_policy('test', policy)
        self.assertIn('test', self.client.list_policies())

        self.client.delete_policy('test')
        self.assertNotIn('test', self.client.list_policies())

    def test_cubbyhole_auth(self):
        orig_token = self.client.token

        resp = self.client.create_token(lease='6h', wrap_ttl='1h')
        self.assertEqual(resp['wrap_info']['ttl'], 3600)

        wrapped_token = resp['wrap_info']['token']
        self.client.auth_cubbyhole(wrapped_token)
        self.assertNotEqual(self.client.token, orig_token)
        self.assertNotEqual(self.client.token, wrapped_token)
        self.assertTrue(self.client.is_authenticated())

        self.client.token = orig_token
        self.assertTrue(self.client.is_authenticated())

    def test_rekey_multi(self):
        cls = type(self)

        self.assertFalse(self.client.rekey_status['started'])

        self.client.start_rekey()
        self.assertTrue(self.client.rekey_status['started'])

        self.client.cancel_rekey()
        self.assertFalse(self.client.rekey_status['started'])

        result = self.client.start_rekey()

        keys = cls.manager.keys

        result = self.client.rekey_multi(keys, nonce=result['nonce'])
        self.assertTrue(result['complete'])

        cls.manager.keys = result['keys']
        cls.manager.unseal()

    def test_rotate(self):
        status = self.client.key_status

        self.client.rotate()

        self.assertGreater(self.client.key_status['term'], status['term'])

    def test_wrapped_token_success(self):
        wrap = self.client.create_token(wrap_ttl='1m')

        # Unwrap token
        result = self.client.unwrap(wrap['wrap_info']['token'])
        self.assertTrue(result['auth']['client_token'])

        # Validate token
        lookup = self.client.lookup_token(result['auth']['client_token'])
        self.assertEqual(result['auth']['client_token'], lookup['data']['id'])

    def test_wrapped_token_intercept(self):
        wrap = self.client.create_token(wrap_ttl='1m')

        # Intercept wrapped token
        self.client.unwrap(wrap['wrap_info']['token'])

        # Attempt to retrieve the token after it's been intercepted
        with self.assertRaises(exceptions.InvalidRequest):
            self.client.unwrap(wrap['wrap_info']['token'])

    def test_wrapped_token_cleanup(self):
        wrap = self.client.create_token(wrap_ttl='1m')

        _token = self.client.token
        self.client.unwrap(wrap['wrap_info']['token'])
        self.assertEqual(self.client.token, _token)

    def test_wrapped_token_revoke(self):
        wrap = self.client.create_token(wrap_ttl='1m')

        # Revoke token before it's unwrapped
        self.client.revoke_token(wrap['wrap_info']['wrapped_accessor'], accessor=True)

        # Unwrap token anyway
        result = self.client.unwrap(wrap['wrap_info']['token'])
        self.assertTrue(result['auth']['client_token'])

        # Attempt to validate token
        with self.assertRaises(exceptions.Forbidden):
            self.client.lookup_token(result['auth']['client_token'])

    def test_wrapped_client_token_success(self):
        wrap = self.client.create_token(wrap_ttl='1m')
        self.client.token = wrap['wrap_info']['token']

        # Unwrap token
        result = self.client.unwrap()
        self.assertTrue(result['auth']['client_token'])

        # Validate token
        self.client.token = result['auth']['client_token']
        lookup = self.client.lookup_token(result['auth']['client_token'])
        self.assertEqual(result['auth']['client_token'], lookup['data']['id'])

    def test_wrapped_client_token_intercept(self):
        wrap = self.client.create_token(wrap_ttl='1m')
        self.client.token = wrap['wrap_info']['token']

        # Intercept wrapped token
        self.client.unwrap()

        # Attempt to retrieve the token after it's been intercepted
        with self.assertRaises(exceptions.InvalidRequest):
            self.client.unwrap()

    def test_wrapped_client_token_cleanup(self):
        wrap = self.client.create_token(wrap_ttl='1m')

        _token = self.client.token
        self.client.token = wrap['wrap_info']['token']
        self.client.unwrap()

        self.assertNotEqual(self.client.token, wrap)
        self.assertNotEqual(self.client.token, _token)

    def test_wrapped_client_token_revoke(self):
        wrap = self.client.create_token(wrap_ttl='1m')

        # Revoke token before it's unwrapped
        self.client.revoke_token(wrap['wrap_info']['wrapped_accessor'], accessor=True)

        # Unwrap token anyway
        self.client.token = wrap['wrap_info']['token']
        result = self.client.unwrap()
        self.assertTrue(result['auth']['client_token'])

        # Attempt to validate token
        with self.assertRaises(exceptions.Forbidden):
            self.client.lookup_token(result['auth']['client_token'])

    def test_start_generate_root_with_completion(self):
        test_otp = 'RSMGkAqBH5WnVLrDTbZ+UQ=='

        self.assertFalse(self.client.generate_root_status['started'])
        response = self.client.start_generate_root(
            key=test_otp,
            otp=True,
        )
        self.assertTrue(self.client.generate_root_status['started'])

        nonce = response['nonce']
        for key in self.manager.keys[0:3]:
            response = self.client.generate_root(
                key=key,
                nonce=nonce,
            )
        self.assertFalse(self.client.generate_root_status['started'])

        # Decode the token provided in the last response. Root token decoding logic derived from:
        # https://github.com/hashicorp/vault/blob/284600fbefc32d8ab71b6b9d1d226f2f83b56b1d/command/operator_generate_root.go#L289
        b64decoded_root_token = b64decode(response['encoded_root_token'])
        if sys.version_info > (3, 0):
            # b64decoding + bytes XOR'ing to decode the new root token in python 3.x
            int_encoded_token = int.from_bytes(b64decoded_root_token, sys.byteorder)
            int_otp = int.from_bytes(b64decode(test_otp), sys.byteorder)
            xord_otp_and_token = int_otp ^ int_encoded_token
            token_hex_string = xord_otp_and_token.to_bytes(len(b64decoded_root_token), sys.byteorder).hex()
        else:
            # b64decoding + bytes XOR'ing to decode the new root token in python 2.7
            otp_and_token = zip(b64decode(test_otp), b64decoded_root_token)
            xord_otp_and_token = ''.join(chr(ord(y) ^ ord(x)) for (x, y) in otp_and_token)
            token_hex_string = binascii.hexlify(xord_otp_and_token)

        new_root_token = str(UUID(token_hex_string))

        # Assert our new root token is properly formed and authenticated
        self.client.token = new_root_token
        if self.client.is_authenticated():
            self.manager.root_token = new_root_token
        else:
            # If our new token was unable to authenticate, set the test client's token back to the original value
            self.client.token = self.manager.root_token
            self.fail('Unable to authenticate with the newly generated root token.')

    def test_start_generate_root_then_cancel(self):
        test_otp = 'RSMGkAqBH5WnVLrDTbZ+UQ=='

        self.assertFalse(self.client.generate_root_status['started'])
        self.client.start_generate_root(
            key=test_otp,
            otp=True,
        )
        self.assertTrue(self.client.generate_root_status['started'])

        self.client.cancel_generate_root()
        self.assertFalse(self.client.generate_root_status['started'])

    def test_tune_auth_backend(self):
        test_backend_type = 'approle'
        test_mount_point = 'tune-approle'
        test_description = 'this is a test auth backend'
        test_max_lease_ttl = 12345678
        if '{0}/'.format(test_mount_point) in self.client.list_auth_backends():
            self.client.disable_auth_backend(test_mount_point)
        self.client.enable_auth_backend(
            backend_type='approle',
            mount_point=test_mount_point
        )

        expected_status_code = 204
        response = self.client.tune_auth_backend(
            backend_type=test_backend_type,
            mount_point=test_mount_point,
            description=test_description,
            max_lease_ttl=test_max_lease_ttl,
        )
        self.assertEqual(
            first=expected_status_code,
            second=response.status_code,
        )

        response = self.client.get_auth_backend_tuning(
            backend_type=test_backend_type,
            mount_point=test_mount_point
        )

        self.assertEqual(
            first=test_max_lease_ttl,
            second=response['data']['max_lease_ttl']
        )

        self.client.disable_auth_backend(mount_point=test_mount_point)

    def test_read_lease(self):
        # Set up a test pki backend and issue a cert against some role so we.
        self.configure_test_pki()
        pki_issue_response = self.client.write(
            path='pki/issue/my-role',
            common_name='test.hvac.com',
        )

        # Read the lease of our test cert that was just issued.
        read_lease_response = self.client.read_lease(pki_issue_response['lease_id'])

        # Validate we received the expected lease ID back in our response.
        self.assertEquals(
            first=pki_issue_response['lease_id'],
            second=read_lease_response['data']['id'],
        )

        # Reset integration test state.
        self.disable_test_pki()

    @parameterized.expand([
        param(
            'hash returned',
        ),
        param(
            'audit backend not enabled',
            enable_first=False,
            raises=exceptions.InvalidRequest,
            exception_message='unknown audit backend',
        ),
    ])
    def test_audit_hash(self, label, enable_first=True, test_input='hvac-rox', raises=None, exception_message=''):
        audit_backend_path = 'tmpfile'
        self.client.disable_audit_backend('tmpfile')
        if enable_first:
            options = {
                'path': '/tmp/vault.audit.log'
            }
            self.client.enable_audit_backend('file', options=options, name=audit_backend_path)

        if raises:
            with self.assertRaises(raises) as cm:
                self.client.audit_hash(
                    name=audit_backend_path,
                    input=test_input
                )
            if exception_message is not None:
                self.assertIn(
                    member=exception_message,
                    container=str(cm.exception),
                )
        else:
            audit_hash_response = self.client.audit_hash(
                name=audit_backend_path,
                input=test_input,
            )
            logging.debug('audit_hash_response: %s' % audit_hash_response)
            self.assertIn(
                member='hmac-sha256:',
                container=audit_hash_response['hash'],
            )
        self.client.disable_audit_backend('tmpfile')

    def test_get_secret_backend_tuning(self):
        secret_backend_tuning = self.client.get_secret_backend_tuning('secret')
        self.assertIn(
            member='default_lease_ttl',
            container=secret_backend_tuning,
        )

    def test_get_backed_up_keys(self):
        with self.assertRaises(exceptions.InvalidRequest) as cm:
            self.client.get_backed_up_keys()
            self.assertEqual(
                first='no backed-up keys found',
                second=str(cm.exception),
            )
