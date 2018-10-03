import logging
from unittest import TestCase
from unittest import skipIf

from parameterized import parameterized, param

from hvac import exceptions
from hvac.tests import utils


class TestAudit(utils.HvacIntegrationTestCase, TestCase):

    # def setUp(self):
    #     super(TestAudit, self).setUp()
    #     if '%s/' % self.TEST_MOUNT_POINT not in self.client.list_auth_backends():
    #         self.client.enable_auth_backend(
    #             backend_type='azure',
    #             mount_point=self.TEST_MOUNT_POINT,
    #         )
    #
    # def tearDown(self):
    #     super(TestAudit, self).tearDown()
    #     self.client.disable_auth_backend(
    #         mount_point=self.TEST_MOUNT_POINT,
    #     )

    @parameterized.expand([
        param(
            'success',
        ),
    ])
    def test_enable_audit_backend(self, label, raises=None, exception_message=''):
        options = {
            'path': '/tmp/vault.audit.log'
        }

        if raises:
            with self.assertRaises(raises) as cm:
                self.client.sys.enable_audit_backend(
                    backend_type='file',
                    options=options,
                )
            self.assertIn(
                member=exception_message,
                container=str(cm.exception),
            )
        else:
            enable_response = self.client.sys.enable_audit_backend(
                backend_type='file',
                options=options,
            )
            logging.debug('enable_response: %s' % enable_response)
            self.assertEqual(
                first=enable_response.status_code,
                second=204,
            )

    def test_audit_backend_manipulation(self):
        self.assertNotIn('tmpfile/', self.client.sys.list_audit_backends())

        options = {
            'path': '/tmp/vault.audit.log'
        }

        self.client.sys.enable_audit_backend('file', options=options, name='tmpfile')
        self.assertIn('tmpfile/', self.client.sys.list_audit_backends())

        self.client.token = self.manager.root_token
        self.client.sys.disable_audit_backend('tmpfile')
        self.assertNotIn('tmpfile/', self.client.sys.list_audit_backends())

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
        self.client.sys.disable_audit_backend('tmpfile')
        if enable_first:
            options = {
                'path': '/tmp/vault.audit.log'
            }
            self.client.sys.enable_audit_backend('file', options=options, name=audit_backend_path)

        if raises:
            with self.assertRaises(raises) as cm:
                self.client.sys.audit_hash(
                    name=audit_backend_path,
                    input=test_input
                )
            if exception_message is not None:
                self.assertIn(
                    member=exception_message,
                    container=str(cm.exception),
                )
        else:
            audit_hash_response = self.client.sys.audit_hash(
                name=audit_backend_path,
                input=test_input,
            )
            logging.debug('audit_hash_response: %s' % audit_hash_response)
            self.assertIn(
                member='hmac-sha256:',
                container=audit_hash_response['hash'],
            )
        self.client.sys.disable_audit_backend('tmpfile')
