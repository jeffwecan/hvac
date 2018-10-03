from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Audit(SystemBackendMixin):
    def list_audit_backends(self):
        """GET /sys/audit

        List only the enabled audit devices (it does not list all available audit devices). This endpoint requires sudo
            capability in addition to any path-specific capabilities.

        :return: List of enabled audit devices.
        :rtype: dict
        """
        list_audit_devices_response = self._adapter.get('/v1/sys/audit').json()
        return list_audit_devices_response['data']

    def enable_audit_backend(self, backend_type, description=None, options=None, name=None):
        """POST /sys/audit/<name>

        :param backend_type:
        :type backend_type:
        :param description:
        :type description:
        :param options:
        :type options:
        :param name:
        :type name:
        :return:
        :rtype:
        """
        if not name:
            name = backend_type

        params = {
            'type': backend_type,
            'description': description,
            'options': options,
        }

        return self._adapter.post('/v1/sys/audit/{0}'.format(name), json=params)

    def disable_audit_backend(self, name):
        """DELETE /sys/audit/<name>

        :param name:
        :type name:
        :return:
        :rtype:
        """
        self._adapter.delete('/v1/sys/audit/{0}'.format(name))

    def audit_hash(self, name, input):
        """POST /sys/audit-hash

        :param name: Specifies the path of the audit device to generate hashes for. This is part of the request URL.
        :type name: str | unicode
        :param input: Specifies the input string to hash.
        :type input: str | unicode
        :return: Dict containing a key of "hash" and the associated hash value.
        :rtype: dict
        """
        params = {
            'input': input,
        }
        audit_hash_response = self._adapter.post('/v1/sys/audit-hash/{0}'.format(name), json=params).json()
        return audit_hash_response['data']
