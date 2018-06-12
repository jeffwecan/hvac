from unittest import TestCase

from hvac import aws_utils


class TestAwsUtils(TestCase):

    def test_generate_sigv4_authorization_request(self):
        test_access_key = 'AKIAIUM6GVYK2SUVX53A'
        test_secret_key = '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'

        signed_request = aws_utils.generate_sigv4_authorization_request(
            access_key=test_access_key,
            secret_key=test_secret_key,
        )
        self.assertIn(
            member='Authorization',
            container=signed_request.headers,
        )
