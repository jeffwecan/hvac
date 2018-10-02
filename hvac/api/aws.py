"""AWS auth method and secret backend methods module."""
import json
from base64 import b64encode

from hvac import aws_utils, exceptions
from hvac.api import base


class AWS(base.Endpoint):
    """Class containing methods for the AWS auth method and AWS secret backend API routes.
    Reference: https://www.vaultproject.io/api/auth/aws/index.html

    """
    def auth_aws_iam(self, access_key, secret_key, session_token=None, header_value=None, mount_point='aws', role='', use_token=True):
        """POST /auth/<mount point>/login

        :param access_key: AWS IAM access key ID
        :type access_key: str | unicode
        :param secret_key: AWS IAM secret access key
        :type secret_key: str | unicode
        :param session_token: Optional AWS IAM session token retrieved via a GetSessionToken AWS API request.
            see: https://docs.aws.amazon.com/STS/latest/APIReference/API_GetSessionToken.html
        :type session_token: str | unicode
        :param header_value: Vault allows you to require an additional header, X-Vault-AWS-IAM-Server-ID, to be present
            to mitigate against different types of replay attacks. Depending on the configuration of the AWS auth
            backend, providing a argument to this optional parameter may be required.
        :type header_value: str | unicode
        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :param role: Name of the role against which the login is being attempted. If role is not specified, then the
            login endpoint looks for a role bearing the name of the AMI ID of the EC2 instance that is trying to login
            if using the ec2 auth method, or the "friendly name" (i.e., role name or username) of the IAM principal
            authenticated. If a matching role is not found, login fails.
        :type role: str | unicode
        :param use_token: If True, uses the token in the response received from the auth request to set the "token"
            attribute on the current Client class instance.
        :type use_token: bool.
        :return: The response from the AWS IAM login request attempt.
        :rtype: requests.Response
        """
        request = aws_utils.generate_sigv4_auth_request(header_value=header_value)

        auth = aws_utils.SigV4Auth(access_key, secret_key, session_token)
        auth.add_auth(request)

        # https://github.com/hashicorp/vault/blob/master/builtin/credential/aws/cli.go
        headers = json.dumps({k: [request.headers[k]] for k in request.headers})
        params = {
            'iam_http_request_method': request.method,
            'iam_request_url': b64encode(request.url.encode('utf-8')).decode('utf-8'),
            'iam_request_headers': b64encode(headers.encode('utf-8')).decode('utf-8'),
            'iam_request_body': b64encode(request.body.encode('utf-8')).decode('utf-8'),
            'role': role,
        }

        return self._adapter.auth('/v1/auth/{0}/login'.format(mount_point), json=params, use_token=use_token)

    def auth_ec2(self, pkcs7, nonce=None, role=None, use_token=True, mount_point='aws-ec2'):
        """POST /auth/<mount point>/login

        :param pkcs7: PKCS#7 version of an AWS Instance Identity Document from the EC2 Metadata Service.
        :type pkcs7: str | unicode
        :param nonce: Optional nonce returned as part of the original authentication request. Not required if the backend
            has "allow_instance_migration" or "disallow_reauthentication" options turned on.
        :type nonce: str | unicode
        :param role: Identifier for the AWS auth backend role being requested.
        :type role: str | unicode
        :param use_token: If True, uses the token in the response received from the auth request to set the "token"
            attribute on the current Client class instance.
        :type use_token: bool.
        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: parsed JSON response from the auth POST request
        :rtype: dict.

        """
        params = {'pkcs7': pkcs7}
        if nonce:
            params['nonce'] = nonce
        if role:
            params['role'] = role

        return self._adapter.auth('/v1/auth/{0}/login'.format(mount_point), json=params, use_token=use_token)

    def create_vault_ec2_client_configuration(self, access_key, secret_key, endpoint=None, mount_point='aws-ec2'):
        """POST /auth/<mount_point>/config/client Reference: https://www.vaultproject.io/api/auth/aws/index.html#configure-client

        :param access_key: AWS Access key with permissions to query AWS APIs. The permissions required depend on the
            specific configurations. If using the iam auth method without inferencing, then no credentials are
            necessary. If using the ec2 auth method or using the iam auth method with inferencing, then these
            credentials need access to ec2:DescribeInstances. If additionally a bound_iam_role is specified,
            then these credentials also need access to iam:GetInstanceProfile. If, however, an alternate sts
            configuration is set for the target account, then the credentials must be permissioned to call
            sts:AssumeRole on the configured role, and that role must have the permissions described here.
        :type access_key: str | unicode
        :param secret_key: AWS Secret key with permissions to query AWS APIs.
        :type secret_key: str | unicode
        :param endpoint: URL to override the default generated endpoint for making AWS EC2 API calls.
        :type endpoint: str | unicode
        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the configure client request.
        :rtype: requests.Response
        """
        params = {
            'access_key': access_key,
            'secret_key': secret_key
        }
        if endpoint is not None:
            params['endpoint'] = endpoint

        return self._adapter.post('/v1/auth/{0}/config/client'.format(mount_point), json=params)

    def get_vault_ec2_client_configuration(self, mount_point='aws-ec2'):
        """GET /auth/<mount_point>/config/client. Reference: https://www.vaultproject.io/api/auth/aws/index.html#read-config

        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the read config request.
        :rtype: requests.Response
        """
        return self._adapter.get('/v1/auth/{0}/config/client'.format(mount_point)).json()

    def delete_vault_ec2_client_configuration(self, mount_point='aws-ec2'):
        """DELETE /auth/<mount_point>/config/client Reference: https://www.vaultproject.io/api/auth/aws/index.html#delete-config

        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the read config request. Successful responses return a 204 with no body.
        :rtype: requests.Response
        """
        return self._adapter.delete('/v1/auth/{0}/config/client'.format(mount_point))

    def create_vault_ec2_certificate_configuration(self, cert_name, aws_public_cert, mount_point='aws-ec2'):
        """POST /auth/<mount_point>/config/certificate/<cert_name> Reference: https://www.vaultproject.io/api/auth/aws/index.html#create-certificate-configuration

        :param cert_name: Name of the certificate.
        :type cert_name: str | unicode
        :param aws_public_cert:  Base64 encoded AWS Public key required to verify PKCS7 signature of the EC2 instance
            metadata.
        :type aws_public_cert: str | unicode
        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the create certificate configuration request.
        :rtype: requests.Response
        """
        # TODO: implement type parameter: https://www.vaultproject.io/api/auth/aws/index.html#type
        params = {
            'cert_name': cert_name,
            'aws_public_cert': aws_public_cert
        }
        return self._adapter.post('/v1/auth/{0}/config/certificate/{1}'.format(mount_point, cert_name), json=params)

    def get_vault_ec2_certificate_configuration(self, cert_name, mount_point='aws-ec2'):
        """GET /auth/<mount_point>/config/certificate/<cert_name> Reference: https://www.vaultproject.io/api/auth/aws/index.html#read-certificate-configuration

        :param cert_name: Name of the certificate.
        :type cert_name: str | unicode
        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the read certificate configuration request.
        :rtype: requests.Response
        """
        return self._adapter.get('/v1/auth/{0}/config/certificate/{1}'.format(mount_point, cert_name)).json()

    def list_vault_ec2_certificate_configurations(self, mount_point='aws-ec2'):
        """GET /auth/<mount_point>/config/certificates?list=true Reference: https://www.vaultproject.io/api/auth/aws/index.html#list-certificate-configurations

        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the list certificate configurations request.
        :rtype: requests.Response
        """
        params = {'list': True}
        return self._adapter.get('/v1/auth/{0}/config/certificates'.format(mount_point), params=params).json()

    def create_ec2_role(self, role, bound_ami_id=None, bound_account_id=None, bound_iam_role_arn=None,
                        bound_iam_instance_profile_arn=None, bound_ec2_instance_id=None, bound_region=None,
                        bound_vpc_id=None, bound_subnet_id=None, role_tag=None,  ttl=None, max_ttl=None, period=None,
                        policies=None, allow_instance_migration=False, disallow_reauthentication=False,
                        resolve_aws_unique_ids=None, mount_point='aws-ec2'):
        """
        POST /auth/<mount_point>/role/<role> Reference: https://www.vaultproject.io/api/auth/aws/index.html#create-role

        :param role: Name of the role.
        :type role: str | unicode
        :param bound_ami_id: If set, defines a constraint on the EC2 instances that they should be using one of the AMI
            ID specified by this parameter. This constraint is checked during ec2 auth as well as the iam auth method
            only when inferring an EC2 instance. This is a comma-separated string or JSON array.
        :type bound_ami_id: list
        :param bound_account_id: If set, defines a constraint on the EC2 instances that the account ID in its identity
            document to match one of the ones specified by this parameter. This constraint is checked during ec2 auth as
            well as the iam auth method only when inferring an EC2 instance. This is a comma-separated string or JSON
            array.
        :type bound_account_id: list
        :param bound_iam_role_arn: If set, defines a constraint on the authenticating EC2 instance that it must match
            one of the IAM role ARNs specified by this parameter. Wildcards are supported at the end of the ARN to allow
            for prefix matching. The configured IAM user or EC2 instance role must be allowed to execute the
            iam:GetInstanceProfile action if this is specified. This constraint is checked by the ec2 auth method as
            well as the iam auth method only when inferring an EC2 instance. This is a comma-separated string or a JSON
            array.
        :type bound_iam_role_arn: list
        :param bound_iam_instance_profile_arn: If set, defines a constraint on the EC2 instances to be associated with
            an IAM instance profile ARN. Wildcards are supported at the end of the ARN to allow for prefix matching.
            This constraint is checked by the ec2 auth method as well as the iam auth method only when inferring an ec2
            instance. This is a comma-separated string or a JSON array.
        :type bound_iam_instance_profile_arn: list
        :param bound_ec2_instance_id: If set, defines a constraint on the EC2 instances to have one of these instance
            IDs. This constraint is checked by the ec2 auth method as well as the iam auth method only when inferring an
            ec2 instance. This is a comma-separated string or a JSON array.
        :type bound_ec2_instance_id: list
        :param bound_region: If set, defines a constraint on the EC2 instances that the region in its identity document
            must match one of the regions specified by this parameter. This constraint is only checked by the ec2 auth
            method as well as the iam auth method only when inferring an ec2 instance. This is a comma-separated string
            or JSON array.
        :type bound_region: list
        :param bound_vpc_id: If set, defines a constraint on the EC2 instance to be associated with a VPC ID that
            matches one of the values specified by this parameter. This constraint is only checked by the ec2 auth
            method as well as the iam auth method only when inferring an ec2 instance. This is a comma-separated string
            or JSON array.
        :type bound_vpc_id: list
        :param bound_subnet_id: If set, defines a constraint on the EC2 instance to be associated with a subnet ID that
            matches one of the values specified by this parameter. This constraint is only checked by the ec2 auth
            method as well as the iam auth method only when inferring an ec2 instance. This is a comma-separated string
            or a JSON array.
        :type bound_subnet_id: list
        :param role_tag: If set, enables the role tags for this role. The value set for this field should be the 'key'
            of the tag on the EC2 instance. The 'value' of the tag should be generated using role/<role>/tag endpoint.
            Defaults to an empty string, meaning that role tags are disabled. This constraint is valid only with the ec2
            auth method and is not allowed when auth_type is iam.
        :type role_tag: str | unicode
        :param ttl: The TTL period of tokens issued using this role, provided as "1h", where hour is the largest suffix.
        :type ttl: str | unicode
        :param max_ttl: The maximum allowed lifetime of tokens issued using this role.
        :type max_ttl: str | unicode
        :param period: If set, indicates that the token generated using this role should never expire. The token should
            be renewed within the duration specified by this value. At each renewal, the token's TTL will be set to the
            value of this parameter.
        :type period: str | unicode
        :param policies: Policies to be set on tokens issued using this role.
        :type policies: list
        :param allow_instance_migration: If set, allows migration of the underlying instance where the client resides.
            This keys off of pendingTime in the metadata document, so essentially, this disables the client nonce check
            whenever the instance is migrated to a new host and pendingTime is newer than the previously-remembered
            time. Use with caution. This only applies to authentications via the ec2 auth method. This is mutually
            exclusive with disallow_reauthentication.
        :type allow_instance_migration: bool
        :param disallow_reauthentication: If set, only allows a single token to be granted per instance ID. In order to
            perform a fresh login, the entry in whitelist for the instance ID needs to be cleared using
            'auth/aws/identity-whitelist/' endpoint. Defaults to 'false'. This only applies to authentications via the
            ec2 auth method. This is mutually exclusive with allow_instance_migration.
        :type disallow_reauthentication: bool
        :param resolve_aws_unique_ids: When set, resolves the bound_iam_principal_arn to the AWS Unique ID for the bound
            principal ARN. This field is ignored when bound_iam_principal_arn ends with a wildcard character. This
            requires Vault to be able to call iam:GetUser or iam:GetRole on the bound_iam_principal_arn that is being
            bound. Resolving to internal AWS IDs more closely mimics the behavior of AWS services in that if an IAM user
            or role is deleted and a new one is recreated with the same name, those new users or roles won't get access
            to roles in Vault that were permissioned to the prior principals of the same name. The default value for new
            roles is true, while the default value for roles that existed prior to this option existing is false (you
            can check the value for a given role using the GET method on the role). Any authentication tokens created
            prior to this being supported won't verify the unique ID upon token renewal. When this is changed from false
            to true on an existing role, Vault will attempt to resolve the role's bound IAM ARN to the unique ID and, if
            unable to do so, will fail to enable this option. Changing this from true to false is not supported; if
            absolutely necessary, you would need to delete the role and recreate it explicitly setting it to false.
            However; the instances in which you would want to do this should be rare. If the role creation (or upgrading
            to use this) succeed, then Vault has already been able to resolve internal IDs, and it doesn't need any
            further IAM permissions to authenticate users. If a role has been deleted and recreated, and Vault has cached
            the old unique ID, you should just call this endpoint specifying the same bound_iam_principal_arn and, as
            long as Vault still has the necessary IAM permissions to resolve the unique ID, Vault will update the
            unique ID. (If it does not have the necessary permissions to resolve the unique ID, then it will fail to
            update.) If this option is set to false, then you MUST leave out the path component in
            bound_iam_principal_arn for roles that do not specify a wildcard at the end, but not IAM users or role
            bindings that have a wildcard. That is, if your IAM role ARN is of the form
            arn:aws:iam::123456789012:role/some/path/to/MyRoleName, and resolve_aws_unique_ids is false, you must
            specify a bound_iam_principal_arn of arn:aws:iam::123456789012:role/MyRoleName for authentication to work.
        :type resolve_aws_unique_ids: bool
        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the list certificate configurations request.
        :rtype: requests.Response
        """
        params = {
            'role': role,
            'auth_type': 'ec2',
            'disallow_reauthentication': disallow_reauthentication,
            'allow_instance_migration': allow_instance_migration
        }

        if bound_ami_id is not None:
            params['bound_ami_id'] = bound_ami_id
        if bound_account_id is not None:
            params['bound_account_id'] = bound_account_id
        if bound_iam_role_arn is not None:
            params['bound_iam_role_arn'] = bound_iam_role_arn
        if bound_ec2_instance_id is not None:
            params['bound_iam_instance_profile_arn'] = bound_ec2_instance_id
        if bound_iam_instance_profile_arn is not None:
            params['bound_iam_instance_profile_arn'] = bound_iam_instance_profile_arn
        if bound_region is not None:
            params['bound_region'] = bound_region
        if bound_vpc_id is not None:
            params['bound_vpc_id'] = bound_vpc_id
        if bound_subnet_id is not None:
            params['bound_subnet_id'] = bound_subnet_id
        if role_tag is not None:
            params['role_tag'] = role_tag
        if ttl is not None:
            params['ttl'] = ttl
        else:
            params['ttl'] = 0
        if max_ttl is not None:
            params['max_ttl'] = max_ttl
        else:
            params['max_ttl'] = 0
        if period is not None:
            params['period'] = period
        else:
            params['period'] = 0
        if policies is not None:
            params['policies'] = policies
        if resolve_aws_unique_ids is not None:
            params['resolve_aws_unique_ids'] = resolve_aws_unique_ids

        return self._adapter.post('/v1/auth/{0}/role/{1}'.format(mount_point, role), json=params)

    def get_ec2_role(self, role, mount_point='aws-ec2'):
        """GET /auth/<mount_point>/role/<role> Reference: https://www.vaultproject.io/api/auth/aws/index.html#read-role

        :param role: Name of the role.
        :type role: str | unicode
        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the read role request.
        :rtype: requests.Response
        """
        return self._adapter.get('/v1/auth/{0}/role/{1}'.format(mount_point, role)).json()

    def delete_ec2_role(self, role, mount_point='aws-ec2'):
        """DELETE /auth/<mount_point>/role/<role> Reference: https://www.vaultproject.io/api/auth/aws/index.html#delete-role

        :param role: Name of the role.
        :type role: str | unicode
        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the delete role request.
        :rtype: requests.Response
        """
        return self._adapter.delete('/v1/auth/{0}/role/{1}'.format(mount_point, role))

    def list_ec2_roles(self, mount_point='aws-ec2'):
        """GET /auth/<mount_point>/roles?list=true Reference: https://www.vaultproject.io/api/auth/aws/index.html#list-roles

        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the list roles request.
        :rtype: requests.Response
        """
        try:
            return self._adapter.get('/v1/auth/{0}/roles'.format(mount_point), params={'list': True}).json()
        except exceptions.InvalidPath:
            return None

    def create_ec2_role_tag(self, role, policies=None, max_ttl=None, instance_id=None,
                            disallow_reauthentication=False, allow_instance_migration=False, mount_point='aws-ec2'):
        """POST /auth/<mount_point>/role/<role>/tag Reference: https://www.vaultproject.io/api/auth/aws/index.html#create-role-tags

        :param role: Name of the role.
        :type role: str | unicode
        :param policies: Policies to be associated with the tag. If set, must be a subset of the role's policies. If
            set, but set to an empty value, only the 'default' policy will be given to issued tokens.
        :type policies: list
        :param max_ttl: The maximum allowed lifetime of tokens issued using this role. instance_id (string: "") -
        :type max_ttl: str | unicode
        :param instance_id: Instance ID for which this tag is intended for. If set, the created tag can only be used by the instance with the given ID.
        :type instance_id: str | unicode
        :param disallow_reauthentication: If set, only allows a single token to be granted per instance ID. This can be
            cleared with the auth/aws/identity-whitelist endpoint. Defaults to 'false'. Mutually exclusive with
            allow_instance_migration.
        :type disallow_reauthentication: bool
        :param allow_instance_migration: If set, allows migration of the underlying instance where the client resides.
            This keys off of pendingTime in the metadata document, so essentially, this disables the client nonce check
            whenever the instance is migrated to a new host and pendingTime is newer than the previously-remembered
            time. Use with caution. Defaults to 'false'. Mutually exclusive with disallow_reauthentication.
        :type allow_instance_migration: bool
        :param mount_point: The "path" the AWS auth backend was mounted on. Vault currently defaults to "aws". "aws-ec2"
            is the default argument for backwards comparability within this module.
        :type mount_point: str | unicode
        :return: The response of the create role tags request.
        :rtype: requests.Response
        """
        params = {
            'role': role,
            'disallow_reauthentication': disallow_reauthentication,
            'allow_instance_migration': allow_instance_migration
        }

        if max_ttl is not None:
            params['max_ttl'] = max_ttl
        if policies is not None:
            params['policies'] = policies
        if instance_id is not None:
            params['instance_id'] = instance_id
        return self._adapter.post('/v1/auth/{0}/role/{1}/tag'.format(mount_point, role), json=params)
