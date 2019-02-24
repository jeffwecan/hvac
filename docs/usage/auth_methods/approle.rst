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
        path='approle-test',
    )
    client.write(
        path="auth/approle-test/role/testrole",
    )

.. testcode:: approle

    read_role_response = client.read(
        path='auth/approle-test/role/testrole',
    )

    secret_id_response = client.write(
        path='auth/approle-test/role/testrole/secret-id',
    )
    #client.auth_approle(read_role_response['data']['role_id'], secret_id_response['data']['secret_id'])
    print(read_role_response)
