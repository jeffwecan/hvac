from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Init(SystemBackendMixin):
    def is_initialized(self):
        """GET /sys/init

        :return:
        :rtype:
        """
        return self._adapter.get('/v1/sys/init').json()['initialized']

    def initialize(self, secret_shares=5, secret_threshold=3, pgp_keys=None):
        """PUT /sys/init

        :param secret_shares:
        :type secret_shares:
        :param secret_threshold:
        :type secret_threshold:
        :param pgp_keys:
        :type pgp_keys:
        :return:
        :rtype:
        """
        params = {
            'secret_shares': secret_shares,
            'secret_threshold': secret_threshold,
        }

        if pgp_keys:
            if len(pgp_keys) != secret_shares:
                raise ValueError('Length of pgp_keys must equal secret shares')

            params['pgp_keys'] = pgp_keys

        return self._adapter.put('/v1/sys/init', json=params).json()
