from hvac import exceptions
from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin

try:
    import hcl

    has_hcl_parser = True
except ImportError:
    has_hcl_parser = False


class Policy(SystemBackendMixin):
    def list_policies(self):
        """GET /sys/policy

        :return: List of configured policies.
        :rtype: list
        """
        list_policies_response = self._adapter.get('/v1/sys/policy').json()
        policies = list_policies_response['data']['policies']
        return policies

    def get_policy(self, name, parse=False):
        """GET /sys/policy/<name>

        :param name:
        :type name:
        :param parse:
        :type parse:
        :return:
        :rtype:
        """
        try:
            get_policy_response = self._adapter.get('/v1/sys/policy/{0}'.format(name)).json()
            if get_policy_response.get('rules'):
                policy = get_policy_response.get('rules')
            else:
                policy = get_policy_response['data'].get('rules')
            if parse:
                if not has_hcl_parser:
                    raise ImportError('pyhcl is required for policy parsing')

                policy = hcl.loads(policy)

            return policy
        except exceptions.InvalidPath:
            return None

    def set_policy(self, name, rules):
        """PUT /sys/policy/<name>

        :param name:
        :type name:
        :param rules:
        :type rules:
        :return:
        :rtype:
        """

        if isinstance(rules, dict):
            rules = json.dumps(rules)

        params = {
            'rules': rules,
        }

        self._adapter.put('/v1/sys/policy/{0}'.format(name), json=params)

    def delete_policy(self, name):
        """DELETE /sys/policy/<name>

        :param name:
        :type name:
        :return:
        :rtype:
        """
        self._adapter.delete('/v1/sys/policy/{0}'.format(name))
