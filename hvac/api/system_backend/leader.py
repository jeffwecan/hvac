from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Leader(SystemBackendMixin):
    @property
    def ha_status(self):
        """GET /sys/leader

        :return:
        :rtype:
        """
        return self._adapter.get('/v1/sys/leader').json()


