import hmac
from datetime import datetime
from hashlib import sha256
import requests


<<<<<<< Updated upstream
<<<<<<< Updated upstream
class SigV4Auth(object):
    def __init__(self, access_key, secret_key, session_token=None, region='us-east-1'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
        self.region = region

    def add_auth(self, request):
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        request.headers['X-Amz-Date'] = timestamp

        if self.session_token:
            request.headers['X-Amz-Security-Token'] = self.session_token

        # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
        canonical_headers = ''.join('{0}:{1}\n'.format(k.lower(), request.headers[k]) for k in sorted(request.headers))
        signed_headers = ';'.join(k.lower() for k in sorted(request.headers))
        payload_hash = sha256(request.body.encode('utf-8')).hexdigest()
        canonical_request = '\n'.join([request.method, '/', '', canonical_headers, signed_headers, payload_hash])

        # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-string-to-sign.html
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = '/'.join([timestamp[0:8], self.region, 'sts', 'aws4_request'])
        canonical_request_hash = sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = '\n'.join([algorithm, timestamp, credential_scope, canonical_request_hash])

        # https://docs.aws.amazon.com/general/latest/gr/sigv4-calculate-signature.html
        key = 'AWS4{0}'.format(self.secret_key).encode('utf-8')
        key = hmac.new(key, timestamp[0:8].encode('utf-8'), sha256).digest()
        key = hmac.new(key, self.region.encode('utf-8'), sha256).digest()
        key = hmac.new(key, 'sts'.encode('utf-8'), sha256).digest()
        key = hmac.new(key, 'aws4_request'.encode('utf-8'), sha256).digest()
        signature = hmac.new(key, string_to_sign.encode('utf-8'), sha256).hexdigest()

        # https://docs.aws.amazon.com/general/latest/gr/sigv4-add-signature-to-request.html
        authorization = '{0} Credential={1}/{2}, SignedHeaders={3}, Signature={4}'.format(
            algorithm, self.access_key, credential_scope, signed_headers, signature)
        request.headers['Authorization'] = authorization


def generate_sigv4_auth_request(header_value=None):
=======
def generate_sigv4_auth_request(access_key, secret_key, session_token=None, header_value=None):
>>>>>>> Stashed changes
=======
def generate_sigv4_auth_request(access_key, secret_key, session_token=None, header_value=None):
>>>>>>> Stashed changes
    """Helper function to prepare a AWS API request to subsequently generate a "AWS Signature Version 4" header.

    :param access_key: AWS IAM access key ID
    :type access_key: str
    :param secret_key: AWS IAM secret access key
    :type secret_key: str
    :param session_token: Optional AWS IAM session token retrieved via a GetSessionToken AWS API request.
        see: https://docs.aws.amazon.com/STS/latest/APIReference/API_GetSessionToken.html
    :type session_token: str
    :param header_value: Vault allows you to require an additional header, X-Vault-AWS-IAM-Server-ID, to be present
        to mitigate against different types of replay attacks. Depending on the configuration of the AWS auth
        backend, providing a argument to this optional parameter may be required.
    :type header_value: str
    :return: A PreparedRequest instance with matching AWS's "AWS Signature Version 4" specifications. Optionally containing the provided header value under a 'X-Vault-AWS-IAM-Server-ID' header name pointed to AWS's simple token service with action "GetCallerIdentity"
    :rtype: requests.PreparedRequest
    """
    request = requests.Request(
        method='POST',
        url='https://sts.amazonaws.com/',
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8', 'Host': 'sts.amazonaws.com'},
        data='Action=GetCallerIdentity&Version=2011-06-15',
    )

    if header_value:
        request.headers['X-Vault-AWS-IAM-Server-ID'] = header_value

    prepared_request = request.prepare()
    sigv4_auth_request = add_sigv4_headers_to_request(prepared_request, access_key, secret_key, session_token)
    return sigv4_auth_request


def add_sigv4_headers_to_request(request_to_sign, access_key, secret_key, session_token=None):
    """Method to add AWS sigv4 information to a prepared request.

    :param request_to_sign: A prepared request to add sigv4 information to.
    :type request_to_sign: requests.PreparedRequest
    :param access_key: AWS IAM access key ID
    :type access_key: str
    :param secret_key: AWS IAM secret access key
    :type secret_key: str
    :param session_token: Optional AWS IAM session token retrieved via a GetSessionToken AWS API request.
        see: https://docs.aws.amazon.com/STS/latest/APIReference/API_GetSessionToken.html
    :type session_token: str
    :return: The provided "request_to_sign" argument with headers matching "AWS Signature Version 4" specifications.
    :rtype: requests.PreparedRequest
    """
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    request_to_sign.headers['X-Amz-Date'] = timestamp

    if session_token:
        request_to_sign.headers['X-Amz-Security-Token'] = session_token

    # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
    canonical_headers = ''.join('{0}:{1}\n'.format(k.lower(), request_to_sign.headers[k]) for k in sorted(request_to_sign.headers))
    signed_headers = ';'.join(k.lower() for k in sorted(request_to_sign.headers))
    payload_hash = sha256(request_to_sign.body.encode('utf-8')).hexdigest()
    canonical_request = '\n'.join([request_to_sign.method, '/', '', canonical_headers, signed_headers, payload_hash])

    # https://docs.aws.amazon.com/general/latest/gr/sigv4-create-string-to-sign.html
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = '/'.join([timestamp[0:8], 'us-east-1', 'sts', 'aws4_request'])
    canonical_request_hash = sha256(canonical_request.encode('utf-8')).hexdigest()
    string_to_sign = '\n'.join([algorithm, timestamp, credential_scope, canonical_request_hash])


    # https://docs.aws.amazon.com/general/latest/gr/sigv4-calculate-signature.html
    signature = calculate_v4_signature(
        secret_key=secret_key,
        timestamp=timestamp,
        string_to_sign=string_to_sign,
    )

    # https://docs.aws.amazon.com/general/latest/gr/sigv4-add-signature-to-request.html
    authorization = '{0} Credential={1}/{2}, SignedHeaders={3}, Signature={4}'.format(
        algorithm, access_key, credential_scope, signed_headers, signature)
    request_to_sign.headers['Authorization'] = authorization

    return request_to_sign


def create_string_to_sign(timestamp, canonical_request):
    """https://docs.aws.amazon.com/general/latest/gr/sigv4-create-string-to-sign.html

    :param timestamp: A datetime.utcnow() value formatted with the following directives "%Y%m%dT%H%M%SZ"
    :type timestamp: str
    :param canonical_request:
    :type canonical_request:
    :return: "string to sign" for "AWS Signature Version 4"
    :rtype: str
    """

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = '/'.join([timestamp[0:8], 'us-east-1', 'sts', 'aws4_request'])
    canonical_request_hash = sha256(canonical_request.encode('utf-8')).hexdigest()
    string_to_sign = '\n'.join([algorithm, timestamp, credential_scope, canonical_request_hash])
    return string_to_sign


def calculate_v4_signature(secret_key, timestamp, string_to_sign):
    """https://docs.aws.amazon.com/general/latest/gr/sigv4-calculate-signature.html


    :param secret_key: AWS IAM secret access key
    :type secret_key: str
    :param timestamp: A datetime.utcnow() value formatted with the following directives "%Y%m%dT%H%M%SZ"
    :type timestamp: str
    :param string_to_sign: String matching the specifications outlined under https://docs.aws.amazon.com/general/latest/gr/sigv4-create-string-to-sign.html.
    :type string_to_sign: str
    :return: AWS Signature Version 4 "signature"
    :rtype: str
    """
    key = 'AWS4{0}'.format(secret_key).encode('utf-8')
    key = hmac.new(key, timestamp[0:8].encode('utf-8'), sha256).digest()
    key = hmac.new(key, 'us-east-1'.encode('utf-8'), sha256).digest()
    key = hmac.new(key, 'sts'.encode('utf-8'), sha256).digest()
    key = hmac.new(key, 'aws4_request'.encode('utf-8'), sha256).digest()
    signature = hmac.new(key, string_to_sign.encode('utf-8'), sha256).hexdigest()
    return signature
