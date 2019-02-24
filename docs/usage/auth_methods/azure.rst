.. _azure-auth-method:

Azure
=====

.. contents::
   :local:
   :depth: 1

.. testsetup:: azure



    from tests.doctest import azure_auth_test_setup
    azure_requests_mocker = azure_auth_test_setup(token=manager.root_token)
    azure_requests_mocker.start()



Enabling the Auth Method
------------------------

Examples
````````

.. testcode:: azure

    import hvac

    client = hvac.Client(url='https://127.0.0.1:8200')

    azure_auth_path = 'company-azure'
    description = "Auth method for use by team members in our company's Azure organization"

    if '%s/' % azure_auth_path not in client.sys.list_auth_methods()['data']:
        print('Enabling the azure auth backend at mount_point: {path}'.format(
            path=azure_auth_path,
        ))
        client.sys.enable_auth_method(
            method_type='azure',
            description=description,
            path=azure_auth_path,
        )

Would produce the following output:

.. testoutput:: azure

    Enabling the azure auth backend at mount_point: company-azure

Configure
---------

.. automethod:: hvac.api.auth_methods.Azure.configure
   :noindex:

Examples
````````

.. testcode:: azure

    import os
    import hvac

    client = hvac.Client(url='https://127.0.0.1:8200')

    client.auth.azure.configure(
        tenant_id='my-tenant-id',
        resource='my-resource',
        client_id=os.getenv('AZURE_CLIENT_ID'),
        client_secret=os.getenv('AZURE_CLIENT_SECRET'),
    )

Read Config
-----------

.. automethod:: hvac.api.auth_methods.Azure.read_config
   :noindex:

Examples
````````

.. testsetup:: azure

    client = hvac.Client(url='https://127.0.0.1:8200')
    client.sys.enable_auth_method(
        method_type='azure',
    )
    client.auth.azure.configure(
        tenant_id='my-tenant-id',
        resource='my-resource',
        client_id=os.getenv('AZURE_CLIENT_ID'),
        client_secret=os.getenv('AZURE_CLIENT_SECRET'),
    )

.. testcode:: azure

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    read_config = client.auth.azure.read_config()
    print('The configured tenant_id is: {id}'.format(id=read_config['tenant_id']))


.. testoutput:: azure

    The configured tenant_id is: my-tenant-id

Delete Config
-------------

.. automethod:: hvac.api.auth_methods.Azure.delete_config
   :noindex:

Examples
````````

.. testcode:: azure

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    client.auth.azure.delete_config()

Create a Role
-------------

.. automethod:: hvac.api.auth_methods.Azure.create_role
   :noindex:

Examples
````````

.. testcode:: azure

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    client.auth.azure.create_role(
        name='my-role',
        policies=['some_policy'],
        bound_service_principal_ids=['some_principle_id'],
    )

Read A Role
-----------

.. automethod:: hvac.api.auth_methods.Azure.read_role
   :noindex:

Examples
````````

.. testsetup:: azure

    client = hvac.Client(url='https://127.0.0.1:8200')
    client.auth.azure.create_role(
        name='my-role',
        policies=['default'],
        bound_service_principal_ids=['some_principle_id'],
    )

.. testcode:: azure

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    role_name = 'my-role'
    read_role_response = client.auth.azure.read_role(
        name=role_name,
    )
    print('Policies for role "{name}": {policies}'.format(
        name='my-role',
        policies=','.join(read_role_response['policies']),
    ))

.. testoutput:: azure

    Policies for role "my-role": some_policy

List Roles
----------

.. automethod:: hvac.api.auth_methods.Azure.list_roles
   :noindex:

Examples
````````

.. testsetup:: azure

    client = hvac.Client(url='https://127.0.0.1:8200')
    client.auth.azure.create_role(
        name='my-role',
        policies=['default'],
        bound_service_principal_ids=['some_principle_id'],
    )

.. testcode:: azure

    import hvac

    client = hvac.Client(url='https://127.0.0.1:8200')
    client.auth.azure.create_role(
        name='my-role',
        policies=['default'],
        bound_service_principal_ids=['some_principle_id'],
    )

    roles = client.auth.azure.list_roles()
    print('The following Azure auth roles are configured: {roles}'.format(
        roles=','.join(roles['keys']),
    ))

.. testoutput:: azure

    The following Azure auth roles are configured: my-role


Delete A Role
-------------

.. automethod:: hvac.api.auth_methods.Azure.delete_role
   :noindex:

Examples
````````

.. testcode:: azure

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    client.auth.azure.delete_role(
        name='my-role',
    )

Login
-----

.. automethod:: hvac.api.auth_methods.Azure.login
   :noindex:

Examples
````````

.. testcode:: azure

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    client.auth.azure.login(
        role=role_name,
        jwt='Some MST JWT...',
    )
    assert client.is_authenticated
