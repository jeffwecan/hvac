from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Lease(SystemBackendMixin):
    def read_lease(self, lease_id):
        """PUT /sys/leases/lookup

        :param lease_id: Specifies the ID of the lease to lookup.
        :type lease_id: str.
        :return: Parsed JSON response from the leases PUT request
        :rtype: dict.
        """
        params = {
            'lease_id': lease_id
        }
        return self._adapter.put('/v1/sys/leases/lookup', json=params).json()

    def renew_secret(self, lease_id, increment=None):
        """PUT /sys/leases/renew

        :param lease_id:
        :type lease_id:
        :param increment:
        :type increment:
        :return:
        :rtype:
        """
        params = {
            'lease_id': lease_id,
            'increment': increment,
        }
        return self._adapter.put('/v1/sys/leases/renew', json=params).json()

    def revoke_secret(self, lease_id):
        """PUT /sys/revoke/<lease id>

        :param lease_id:
        :type lease_id:
        :return:
        :rtype:
        """
        self._adapter.put('/v1/sys/revoke/{0}'.format(lease_id))

    def revoke_secret_prefix(self, path_prefix):
        """PUT /sys/revoke-prefix/<path prefix>

        :param path_prefix:
        :type path_prefix:
        :return:
        :rtype:
        """
        self._adapter.put('/v1/sys/revoke-prefix/{0}'.format(path_prefix))

    def revoke_self_token(self):
        """PUT /auth/token/revoke-self

        :return:
        :rtype:
        """
        self._adapter.put('/v1/auth/token/revoke-self')

