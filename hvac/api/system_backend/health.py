#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Health methods module."""
from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin


class Health(SystemBackendMixin):
    """.

    Reference: https://www.vaultproject.io/api/system/index.html
    """

    def read_information(self, standbyok=False, activecode=200, standbycode=429, drsecondarycode=472,
                         performancestandbycode=473, sealedcode=503, uninitcode=501, method='HEAD'):
        """
        This endpoint returns the health status of Vault. This matches the semantics of
        a Consul HTTP health check and provides a simple way to monitor the health of a
        Vault instance.


        :param standbyok: Specifies if being a standby should still return
            the active status code instead of the standby status code. This is useful when
            Vault is behind a non-configurable load balance that just wants a 200-level
            response.
        :type standbyok: bool
        :param activecode: the status code that should be returned
            for an active node.
        :type activecode: int
        :param standbycode: Specifies the status code that should be returned
            for a standby node.
        :type standbycode: int
        :param drsecondarycode: Specifies the status code that should be
            returned for a DR secondary node.
        :type drsecondarycode: int
        :param performancestandbycode: Specifies the status code that should be
            returned for a performance standby node.
        :type performancestandbycode: int
        :param sealedcode: Specifies the status code that should be returned
            for a sealed node.
        :type sealedcode: int
        :param uninitcode: Specifies the status code that should be returned
            for a uninitialized node.
        :type uninitcode: int
        :param method: Supported methods:
            HEAD: /sys/health. Produces: 000 (empty body)
            GET: /sys/health. Produces: 000 application/json
        :type method: str | unicode
        :return: The data key from the JSON response of the request.
        :rtype: requests.Response
        """
        params = {
            'standbyok': standbyok,
            'activecode': activecode,
            'standbycode': standbycode,
            'drsecondarycode': drsecondarycode,
            'performancestandbycode': performancestandbycode,
            'sealedcode': sealedcode,
            'uninitcode': uninitcode,
        }

        if method == 'HEAD':
            api_path = '/v1/sys/health'.format()
            return self._adapter.head(
                url=api_path,
                json=params,
            )

        elif method == 'GET':
            api_path = '/v1/sys/health'.format()
            return self._adapter.head(
                url=api_path,
                json=params,
            )
