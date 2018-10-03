from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Seal(SystemBackendMixin):

    @property
    def seal_status(self):
        """GET /sys/seal-status

        :return:
        :rtype:
        """
        return self._adapter.get('/v1/sys/seal-status').json()

    def seal(self):
        """PUT /sys/seal

        :return:
        :rtype:
        """
        self._adapter.put('/v1/sys/seal')

    def unseal_reset(self):
        """PUT /sys/unseal

        :return:
        :rtype:
        """
        params = {
            'reset': True,
        }
        return self._adapter.put('/v1/sys/unseal', json=params).json()

    def unseal(self, key):
        """PUT /sys/unseal

        :param key:
        :type key:
        :return:
        :rtype:
        """
        params = {
            'key': key,
        }

        return self._adapter.put('/v1/sys/unseal', json=params).json()

    def unseal_multi(self, keys):
        """

        :param keys:
        :type keys:
        :return:
        :rtype:
        """
        result = None

        for key in keys:
            result = self.unseal(key)
            if not result['sealed']:
                break

        return result
