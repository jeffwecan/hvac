from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Key(SystemBackendMixin):

    @property
    def generate_root_status(self):
        """GET /sys/generate-root/attempt

        :return:
        :rtype:
        """
        return self._adapter.get('/v1/sys/generate-root/attempt').json()

    def start_generate_root(self, key, otp=False):
        """PUT /sys/generate-root/attempt

        :param key:
        :type key:
        :param otp:
        :type otp:
        :return:
        :rtype:
        """
        params = {}
        if otp:
            params['otp'] = key
        else:
            params['pgp_key'] = key

        return self._adapter.put('/v1/sys/generate-root/attempt', json=params).json()

    def generate_root(self, key, nonce):
        """PUT /sys/generate-root/update

        :param key:
        :type key:
        :param nonce:
        :type nonce:
        :return:
        :rtype:
        """
        params = {
            'key': key,
            'nonce': nonce,
        }

        return self._adapter.put('/v1/sys/generate-root/update', json=params).json()

    def cancel_generate_root(self):
        """DELETE /sys/generate-root/attempt

        :return:
        :rtype:
        """

        return self._adapter.delete('/v1/sys/generate-root/attempt').status_code == 204

    @property
    def key_status(self):
        """GET /sys/key-status

        :return: Information about the current encryption key used by Vault.
        :rtype: dict
        """
        key_status_response = self._adapter.get('/v1/sys/key-status').json()
        key_status = key_status_response['data']
        return key_status

    def rotate(self):
        """PUT /sys/rotate

        :return:
        :rtype:
        """
        self._adapter.put('/v1/sys/rotate')

    @property
    def rekey_status(self):
        """GET /sys/rekey/init

        :return:
        :rtype:
        """
        return self._adapter.get('/v1/sys/rekey/init').json()

    def start_rekey(self, secret_shares=5, secret_threshold=3, pgp_keys=None,
                    backup=False):
        """PUT /sys/rekey/init

        :param secret_shares: Specifies the number of shares to split the master key into.
        :type secret_shares: int
        :param secret_threshold: Specifies the number of shares required to reconstruct the master key. This must be
            less than or equal to secret_shares.
        :type secret_threshold: int
        :param pgp_keys: List of PGP public keys used to encrypt the output unseal keys. Ordering is preserved. The keys
            must be base64-encoded from their original binary representation. The size of this array must be the same as
            secret_shares.
        :type pgp_keys: list
        :param backup: Specifies if using PGP-encrypted keys, whether Vault should also store a plaintext backup of the
            PGP-encrypted keys at core/unseal-keys-backup in the physical storage backend. These can then be retrieved
            and removed via the sys/rekey/backup endpoint.
        :type backup: bool
        :return: The full response object if an empty body is received, otherwise the JSON dict of the response.
        :rtype: dict | request.Response
        """
        params = {
            'secret_shares': secret_shares,
            'secret_threshold': secret_threshold,
        }

        if pgp_keys:
            if len(pgp_keys) != secret_shares:
                raise ValueError('Length of pgp_keys must equal secret shares')

            params['pgp_keys'] = pgp_keys
            params['backup'] = backup

        resp = self._adapter.put('/v1/sys/rekey/init', json=params)
        if resp.text:
            return resp.json()

    def cancel_rekey(self):
        """DELETE /sys/rekey/init

        :return:
        :rtype:
        """
        self._adapter.delete('/v1/sys/rekey/init')

    def rekey(self, key, nonce=None):
        """PUT /sys/rekey/update

        :param key:
        :type key:
        :param nonce:
        :type nonce:
        :return:
        :rtype:
        """
        params = {
            'key': key,
        }

        if nonce:
            params['nonce'] = nonce

        return self._adapter.put('/v1/sys/rekey/update', json=params).json()

    def rekey_multi(self, keys, nonce=None):
        """

        :param keys:
        :type keys:
        :param nonce:
        :type nonce:
        :return:
        :rtype:
        """
        result = None

        for key in keys:
            result = self.rekey(key, nonce=nonce)
            if result.get('complete'):
                break

        return result

    def get_backed_up_keys(self):
        """GET /sys/rekey/backup

        :return:
        :rtype:
        """
        return self._adapter.get('/v1/sys/rekey/backup').json()
