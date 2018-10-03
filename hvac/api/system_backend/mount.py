from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Mount(SystemBackendMixin):
    def list_secret_backends(self):
        """GET /sys/mounts

        :return: List of all the mounted secrets engines.
        :rtype: dict
        """
        list_secret_backends_response = self._adapter.get('/v1/sys/mounts').json()
        secret_backends = list_secret_backends_response['data']
        return secret_backends

    def enable_secret_backend(self, backend_type, description=None, mount_point=None, config=None, options=None):
        """POST /sys/mounts/<mount point>

        :param backend_type:
        :type backend_type:
        :param description:
        :type description:
        :param mount_point:
        :type mount_point:
        :param config:
        :type config:
        :param options:
        :type options:
        :return:
        :rtype:
        """
        if not mount_point:
            mount_point = backend_type

        params = {
            'type': backend_type,
            'description': description,
            'config': config,
            'options': options,
        }

        self._adapter.post('/v1/sys/mounts/{0}'.format(mount_point), json=params)

    def tune_secret_backend(self, backend_type, mount_point=None, default_lease_ttl=None, max_lease_ttl=None, description=None,
                            audit_non_hmac_request_keys=None, audit_non_hmac_response_keys=None, listing_visibility=None,
                            passthrough_request_headers=None):
        """POST /sys/mounts/<mount point>/tune

        :param backend_type: Type of the secret backend to modify
        :type backend_type: str
        :param mount_point: The path the associated secret backend is mounted
        :type mount_point: str
        :param description: Specifies the description of the mount. This overrides the current stored value, if any.
        :type description: str
        :param default_lease_ttl: Default time-to-live. This overrides the global default. A value of 0 is equivalent to
            the system default TTL
        :type default_lease_ttl: int
        :param max_lease_ttl: Maximum time-to-live. This overrides the global default. A value of 0 are equivalent and
            set to the system max TTL.
        :type max_lease_ttl: int
        :param audit_non_hmac_request_keys: Specifies the comma-separated list of keys that will not be HMAC'd by audit
            devices in the request data object.
        :type audit_non_hmac_request_keys: list
        :param audit_non_hmac_response_keys: Specifies the comma-separated list of keys that will not be HMAC'd by audit
            devices in the response data object.
        :type audit_non_hmac_response_keys: list
        :param listing_visibility: Speficies whether to show this mount in the UI-specific listing endpoint. Valid
            values are "unauth" or "".
        :type listing_visibility: str
        :param passthrough_request_headers: Comma-separated list of headers to whitelist and pass from the request
            to the backend.
        :type passthrough_request_headers: str

        :return: The response from Vault
        :rtype: request.Response
        """

        if not mount_point:
            mount_point = backend_type
        # All parameters are optional for this method. Until/unless we include input validation, we simply loop over the
        # parameters and add which parameters are set.
        optional_parameters = [
            'default_lease_ttl',
            'max_lease_ttl',
            'description',
            'audit_non_hmac_request_keys',
            'audit_non_hmac_response_keys',
            'listing_visibility',
            'passthrough_request_headers',
        ]
        params = {}
        for optional_parameter in optional_parameters:
            if locals().get(optional_parameter) is not None:
                params[optional_parameter] = locals().get(optional_parameter)
        return self._adapter.post('/v1/sys/mounts/{0}/tune'.format(mount_point), json=params)

    def get_secret_backend_tuning(self, backend_type, mount_point=None):
        """GET /sys/mounts/<mount point>/tune

        :param backend_type: Name of the secret engine. E.g. "aws".
        :type backend_type: str | unicode
        :param mount_point: Alternate argument for backend_type.
        :type mount_point: str | unicode
        :return: The specified mount's configuration.
        :rtype: dict
        """
        if not mount_point:
            mount_point = backend_type

        read_config_response = self._adapter.get('/v1/sys/mounts/{0}/tune'.format(mount_point)).json()
        return read_config_response['data']

    def disable_secret_backend(self, mount_point):
        """DELETE /sys/mounts/<mount point>

        :param mount_point:
        :type mount_point:
        :return:
        :rtype:
        """
        self._adapter.delete('/v1/sys/mounts/{0}'.format(mount_point))

    def remount_secret_backend(self, from_mount_point, to_mount_point):
        """POST /sys/remount

        :param from_mount_point:
        :type from_mount_point:
        :param to_mount_point:
        :type to_mount_point:
        :return:
        :rtype:
        """
        params = {
            'from': from_mount_point,
            'to': to_mount_point,
        }

        self._adapter.post('/v1/sys/remount', json=params)
