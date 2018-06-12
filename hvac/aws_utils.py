#!/usr/bin/env python
import hmac
from datetime import datetime
from hashlib import sha256

import requests


def generate_sigv4_authorization_request(access_key, secret_key, session_token=None, header_value=None):
    """
    Uses a requests Request object to store headers in line with the process outlined at:
    https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
    :param access_key: str, AWS IAM access key ID
    :param secret_key: str, AWS IAM secret access key
    :param session_token: str, Optional string received from AWS STS when obtaining temporary security credentials
    :param header_value: str, Value corresponding to the AWS auth backend config's iam_server_id_header_value setting
    :return: request.Request, a Request object containing the body and headers needed to provide the
    sigv4 authorization headers
    """
    request = requests.Request(
        method='POST',
        url='https://sts.amazonaws.com/',
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8', 'Host': 'sts.amazonaws.com'},
        data='Action=GetCallerIdentity&Version=2011-06-15',
    )

    if header_value:
        request.headers['X-Vault-AWS-IAM-Server-ID'] = header_value

    request = request.prepare()

    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    request.headers['X-Amz-Date'] = timestamp

    if session_token:
        request.headers['X-Amz-Security-Token'] = session_token

    # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
    canonical_headers = ''.join('{0}:{1}\n'.format(k.lower(), request.headers[k]) for k in sorted(request.headers))
    signed_headers = ';'.join(k.lower() for k in sorted(request.headers))
    payload_hash = sha256(request.body.encode('utf-8')).hexdigest()
    canonical_request = '\n'.join([request.method, '/', '', canonical_headers, signed_headers, payload_hash])

    # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-string-to-sign.html
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = '/'.join([timestamp[0:8], 'us-east-1', 'sts', 'aws4_request'])
    canonical_request_hash = sha256(canonical_request.encode('utf-8')).hexdigest()
    string_to_sign = '\n'.join([algorithm, timestamp, credential_scope, canonical_request_hash])

    # https://docs.aws.amazon.com/general/latest/gr/sigv4-calculate-signature.html
    key = 'AWS4{0}'.format(secret_key).encode('utf-8')
    key = hmac.new(key, timestamp[0:8].encode('utf-8'), sha256).digest()
    key = hmac.new(key, 'us-east-1'.encode('utf-8'), sha256).digest()
    key = hmac.new(key, 'sts'.encode('utf-8'), sha256).digest()
    key = hmac.new(key, 'aws4_request'.encode('utf-8'), sha256).digest()
    signature = hmac.new(key, string_to_sign.encode('utf-8'), sha256).hexdigest()

    # https://docs.aws.amazon.com/general/latest/gr/sigv4-add-signature-to-request.html
    authorization = '{0} Credential={1}/{2}, SignedHeaders={3}, Signature={4}'.format(
        algorithm,
        access_key,
        credential_scope,
        signed_headers,
        signature
    )
    request.headers['Authorization'] = authorization

    return request
