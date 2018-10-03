from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Auth(SystemBackendMixin):

    def list_auth_backends(self):
        """GET /sys/auth

        :return: List of all enabled auth methods.
        :rtype: dict
        """
        list_auth_methods_response = self._adapter.get('/v1/sys/auth').json()
        return list_auth_methods_response['data']

    def enable_auth_backend(self, backend_type, description=None, mount_point=None, config=None, plugin_name=None):
        """POST /sys/auth/<mount point>

        :param backend_type:
        :type backend_type:
        :param description:
        :type description:
        :param mount_point:
        :type mount_point:
        :param config:
        :type config:
        :param plugin_name:
        :type plugin_name:
        :return:
        :rtype:
        """
        if not mount_point:
            mount_point = backend_type

        params = {
            'type': backend_type,
            'description': description,
            'config': config,
            'plugin_name': plugin_name,
        }
        return self._adapter.post('/v1/sys/auth/{0}'.format(mount_point), json=params)

    def tune_auth_backend(self, backend_type, mount_point=None, default_lease_ttl=None, max_lease_ttl=None, description=None,
                          audit_non_hmac_request_keys=None, audit_non_hmac_response_keys=None, listing_visibility=None,
                          passthrough_request_headers=None):
        """POST /sys/auth/<mount point>/tune

        :param backend_type: Name of the auth backend to modify (e.g., token, approle, etc.)
        :type backend_type: str.
        :param mount_point: The path the associated auth backend is mounted under.
        :type mount_point: str.
        :param description: Specifies the description of the mount. This overrides the current stored value, if any.
        :type description: str.
        :param default_lease_ttl:
        :type default_lease_ttl: int.
        :param max_lease_ttl:
        :type max_lease_ttl: int.
        :param audit_non_hmac_request_keys: Specifies the comma-separated list of keys that will not be HMAC'd by
            audit devices in the request data object.
        :type audit_non_hmac_request_keys: list.
        :param audit_non_hmac_response_keys: Specifies the comma-separated list of keys that will not be HMAC'd
            by audit devices in the response data object.
        :type audit_non_hmac_response_keys: list.
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint.
            Valid values are "unauth" or "".
        :type listing_visibility: str.
        :param passthrough_request_headers: Comma-separated list of headers to whitelist and pass from the request
            to the backend.
        :type passthrough_request_headers: list.
        :return: The JSON response from Vault
        :rtype: dict.
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
        return self._adapter.post('/v1/sys/auth/{0}/tune'.format(mount_point), json=params)

    def get_auth_backend_tuning(self, backend_type, mount_point=None):
        """GET /sys/auth/<mount point>/tune

        :param backend_type: Name of the auth backend to modify (e.g., token, approle, etc.)
        :type backend_type: str.
        :param mount_point: The path the associated auth backend is mounted under.
        :type mount_point: str.
        :return: The JSON response from Vault
        :rtype: dict.
        """
        if not mount_point:
            mount_point = backend_type

        return self._adapter.get('/v1/sys/auth/{0}/tune'.format(mount_point)).json()

    def disable_auth_backend(self, mount_point):
        """DELETE /sys/auth/<mount point>

        :param mount_point:
        :type mount_point:
        :return:
        :rtype:
        """
        self._adapter.delete('/v1/sys/auth/{0}'.format(mount_point))
