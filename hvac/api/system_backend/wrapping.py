from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Wrapping(SystemBackendMixin):
    def unwrap(self, token=None):
        """POST /sys/wrapping/unwrap

        :param token:
        :type token:
        :return:
        :rtype:
        """
        if token:
            payload = {
                'token': token
            }
            return self._adapter.post('/v1/sys/wrapping/unwrap', json=payload).json()
        else:
            return self._adapter.post('/v1/sys/wrapping/unwrap').json()

    # def auth_cubbyhole(self, token):
    #     """POST /v1/sys/wrapping/unwrap
    #
    #     :param token:
    #     :type token:
    #     :return:
    #     :rtype:
    #     """
    #     self.token = token
    #     return self._adapter.auth('/v1/sys/wrapping/unwrap')
