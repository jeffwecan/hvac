Approle
=======

.. contents::
   :local:
   :depth: 1

Authentication
--------------

.. automethod:: hvac.v1.Client.auth_approle
   :noindex:

Examples
````````

.. testsetup:: approle

    client.sys.enable_auth_method(
        method_type='approle',
        path='approle',
    )
    client.write(
        path="auth/approle/role/testrole",
    )

.. testcode:: approle

    read_role_response = client.read(
        path='auth/approle/role/testrole/role-id',
    )

    secret_id_response = client.write(
        path='auth/approle/role/testrole/secret-id',
    )
    client.auth_approle(read_role_response['data']['role_id'], secret_id_response['data']['secret_id'])

.. testcleanup:: approle

    client.token = manager.root_token
    client.sys.disable_auth_method(
        path='approle',
    )
