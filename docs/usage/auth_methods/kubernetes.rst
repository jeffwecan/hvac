Kubernetes
==========

.. contents::
   :local:
   :depth: 1

.. testsetup:: k8s

    from tests.doctest import mock_login_response
    mock_login_response(
        path='kubernetes/login',
        client_token=manager.root_token,
    )

Authentication
--------------

.. automethod:: hvac.v1.Client.auth_kubernetes
   :noindex:


.. testsetup:: k8s

    from mock import mock_open
    original_open = open
    open = mock_open(read_data="data")

.. testcode:: k8s

    # Kubernetes (from k8s pod)
    f = open('/var/run/secrets/kubernetes.io/serviceaccount/token')
    jwt = f.read()

    client = hvac.Client(url='https://127.0.0.1:8200')
    client.auth_kubernetes(role="example", jwt=jwt)

.. testcleanup:: k8s

    open = original_open
