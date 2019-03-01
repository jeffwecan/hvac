#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
import logging
from requests_mock.mocker import Mocker

from tests import utils as test_utils
from tests.utils.server_manager import ServerManager

logger = logging.getLogger(__name__)


class DoctestRequestMocker:
    request_mocker = None

    def __init__(self):
        if DoctestRequestMocker.request_mocker is None:
            DoctestRequestMocker.request_mocker = Mocker(real_http=True)

    def start(self):
        if self.request_mocker._last_send:
            try:
                self.request_mocker.start()
            except RuntimeError:
                logger.exception('Error calling DoctestRequestMocker.start()')

    def __getattr__(self, name):
        return getattr(self.request_mocker, name)


def mock_login_response(path, client_token):
    mock_url = 'https://127.0.0.1:8200/v1/auth/{path}'.format(path=path)
    mock_response = {
        "auth": {
            "client_token": client_token,
            "accessor": "0e9e354a-520f-df04-6867-ee81cae3d42d",
            "policies": ['default'],
            "lease_duration": 2764800,
            "renewable": True,
        },
    }
    logger.error('mock_login_response URI: %s' % mock_url)
    DoctestRequestMocker().register_uri(
        method='POST',
        url=mock_url,
        json=mock_response,
    )


def mfa_auth_test_setup(client):
    mock_login_response(
        path='some-userpass/login/someuser',
        client_token=client.token,
    )

    # mocker = Mocker(real_http=True)
    #DoctestRequestMocker.start()

    mock_url = 'https://127.0.0.1:8200/v1/auth/{mount_point}/duo/access'.format(
        mount_point='some-userpass',
    )
    DoctestRequestMocker().register_uri(
        method='POST',
        url=mock_url,
    )

    test_userpass_password = 'some password'

    from mock import patch
    getpass_patcher = patch('getpass.getpass')
    mock_getpass = getpass_patcher.start()
    mock_getpass.return_value = test_userpass_password

    userpass_auth_path = 'some-userpass'
    # Reset state of our test userpass auth method under path: some-userpass
    client.sys.disable_auth_method(
        path=userpass_auth_path,
    )
    client.sys.enable_auth_method(
        method_type='userpass',
        path=userpass_auth_path,
    )
    client.create_userpass(
        username='someuser',
        password=test_userpass_password,
        policies=['default'],
        mount_point=userpass_auth_path,
    )


def azure_auth_test_setup(token):
    request_mocker = DoctestRequestMocker()
    mock_login_response(
        path='azure/login',
        client_token=token,
    )

    mock_url = 'https://127.0.0.1:8200/v1/{mount_point}/roles/{name}'.format(
        mount_point='azure',
        name='hvac',
    )
    request_mocker.register_uri(
        method='POST',
        url=mock_url,
    )
    mock_url = 'https://127.0.0.1:8200/v1/{mount_point}/roles'.format(
        mount_point='azure',
    )
    mock_response = {
        'data': {
            'keys': ['hvac'],
        },
    }
    request_mocker.register_uri(
        method='LIST',
        url=mock_url,
        json=mock_response,
    )
    mock_response = {
        'data': {
            'client_id': 'some_client_id',
            'client_secret': 'some_client_secret',
        },
    }
    mock_url = 'https://127.0.0.1:8200/v1/{mount_point}/creds/{name}'.format(
        mount_point='azure',
        name='hvac',
    )
    request_mocker.register_uri(
        method='GET',
        url=mock_url,
        json=mock_response,
    )

def aws_auth_test_setup(token):


    from datetime import datetime, timedelta
    from tests.doctest import mock_login_response, DoctestRequestMocker
    request_mocker = DoctestRequestMocker()
    utc_timestamp = datetime.utcnow()
    datetime_format = '%Y-%m-%dT%H:%M:%SZ%z'
    last_updated = utc_timestamp - timedelta(hours=4)
    expiration = utc_timestamp + timedelta(hours=4)
    mock_response = {
        "Code": "Success",
        "LastUpdated": last_updated.strftime(datetime_format),
        "Type": "AWS-HMAC",
        "AccessKeyId": "foobar_key",
        "SecretAccessKey": "foobar_secret",
        "Token": "foobar_token",
        "Expiration": expiration.strftime(datetime_format),
    }
    mock_url = 'http://169.254.169.254/latest/meta-data/iam/security-credentials/some-instance-role'
    request_mocker.register_uri(
        method='GET',
        url=mock_url,
        json=mock_response
    )
    mock_response = 'some_pkcs7_string'
    mock_url = 'http://169.254.169.254/latest/dynamic/instance-identity/pkcs7'
    request_mocker.register_uri(
        method='GET',
        url=mock_url,
        json=mock_response
    )

    mock_response = {
      "data": {
        "access_key": "AKIA..."
      }
    }
    mock_url = 'https://127.0.0.1:8200/v1/{mount_point}/config/rotate-root'.format(
        mount_point='aws',
    )
    request_mocker.register_uri(
        method='POST',
        url=mock_url,
        json=mock_response,
    )
    mock_response = {
      "data": {
        "access_key": "AKIA...",
        "secret_key": "xlCs...",
        "security_token": None
      }
    }
    mock_url = 'https://127.0.0.1:8200/v1/{mount_point}/creds/{role_name}'.format(
        mount_point='aws',
        role_name='hvac-role',
    )
    request_mocker.register_uri(
        method='GET',
        url=mock_url,
        json=mock_response,
    )
    mock_login_response(
        path='aws/login',
        client_token=token,
    )
    os.environ['AWS_LAMBDA_FUNCTION_NAME'] = 'hvac-lambda'
    # "Mock" the AWS credentials as they can't be mocked in Botocore currently
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "foobar_key")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "foobar_secret")
    os.environ.setdefault("VAULT_HEADER_VALUE", "some_header_value")



def doctest_global_setup():
    # DoctestRequestMocker.start()
    client = test_utils.create_client()
    manager = ServerManager(
        config_paths=[test_utils.get_config_file_path('vault-doctest.hcl')],
        client=client,
    )
    manager.start()
    manager.initialize()
    manager.unseal()

    client.token = manager.root_token
    os.environ['VAULT_TOKEN'] = manager.root_token
    os.environ['REQUESTS_CA_BUNDLE'] = test_utils.get_config_file_path('server-cert.pem')
    os.environ.setdefault("VAULT_ADDR", "https://127.0.0.1:8200")

    DoctestRequestMocker().start()
    # DoctestRequestMocker.start()

    return manager
