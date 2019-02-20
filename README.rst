hvac
====


.. image:: https://raw.githubusercontent.com/hvac/hvac/master/docs/_static/hvac_logo_800px.png
   :target: https://raw.githubusercontent.com/hvac/hvac/master/docs/_static/hvac_logo_800px.png
   :alt: Header image


`HashiCorp <https://hashicorp.com/>`_ `Vault <https://www.vaultproject.io>`_ API client for Python 2.7/3.x


.. image:: https://travis-ci.org/hvac/hvac.svg?branch=master
   :target: https://travis-ci.org/hvac/hvac
   :alt: Travis CI


.. image:: https://codecov.io/gh/hvac/hvac/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/hvac/hvac
   :alt: codecov


.. image:: https://readthedocs.org/projects/hvac/badge/
   :target: https://hvac.readthedocs.io/en/latest/?badge=latest
   :alt: "Documentation Status"


.. image:: https://badge.fury.io/py/hvac.svg
   :target: https://badge.fury.io/py/hvac
   :alt: PyPI version


.. image:: https://img.shields.io/twitter/follow/python_hvac.svg?label=Twitter%20-%20@python_hvac&style=social?style=plastic
   :target: https://twitter.com/python_hvac
   :alt: Twitter - @python_hvac


Tested against the latest release, HEAD ref, and 3 previous major versions (counting back from the latest release) of Vault.
Currently supports Vault v0.9.6 or later.

Getting started
---------------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   pip install hvac

or

.. code-block:: bash

   pip install "hvac[parser]"

if you would like to be able to return parsed HCL data as a Python dict for methods that support it.

Initialize the Client
^^^^^^^^^^^^^^^^^^^^^

Using TLS:

.. doctest:: init

    >>> client = hvac.Client(url='https://localhost:8200')
    >>> client.is_authenticated()
    True


Using TLS with client-side certificate authentication:

.. doctest:: init

    >>> client = hvac.Client(
    ...     url='https://localhost:8200',
    ...     token=os.environ['VAULT_TOKEN'],
    ...     cert=(client_cert_path, client_key_path),
    ...     verify=server_cert_path,
    ... )
    >>> client.is_authenticated()
    True


Using `Vault Enterprise namespace <https://www.vaultproject.io/docs/enterprise/namespaces/index.html>`_\ :

.. doctest:: init

    >>> client = hvac.Client(
    ...     url='https://localhost:8200',
    ...     namespace=os.getenv('VAULT_NAMESPACE'),
    ... )


Using plaintext / HTTP (not recommended for anything other than development work):

.. doctest:: init

    >>> client = hvac.Client(url='http://localhost:8200')

Vault Cluster - Initialize and Seal/Unseal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. testsetup:: init-seal-and-unseal

    manager.restart_vault_cluster(perform_init=False)
    client.token = manager.root_token

.. doctest:: init-seal-and-unseal

    >>> client.sys.is_initialized()
    False

    >>> shares = 5
    >>> threshold = 3
    >>> result = client.sys.initialize(shares, threshold)
    >>> root_token = result['root_token']
    >>> keys = result['keys']
    >>> client.sys.is_initialized()
    True

    >>> client.token = root_token

    >>> client.sys.is_sealed()
    True
    >>> # Unseal a Vault cluster with individual keys
    >>> unseal_response1 = client.sys.submit_unseal_key(keys[0])
    >>> unseal_response2 = client.sys.submit_unseal_key(keys[1])
    >>> unseal_response3 = client.sys.submit_unseal_key(keys[2])
    >>> client.sys.is_sealed()
    False
    >>> # Seal a previously unsealed Vault cluster.
    >>> client.sys.seal()
    <Response [204]>
    >>> client.sys.is_sealed()
    True

    >>> # Unseal with multiple keys until threshold met
    >>> unseal_response = client.sys.submit_unseal_keys(keys)

    >>> client.sys.is_sealed()
    False

.. testcleanup:: init-seal-and-unseal

    manager.restart_vault_cluster(perform_init=True)
    client.token = manager.root_token


Read and write to secrets engines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

KV Secrets Engine - Version 2
"""""""""""""""""""""""""""""

.. note::

    Vault currently defaults to KV version 2 automatically when a `Vault server is running in "dev" mode <https://www.vaultproject.io/docs/secrets/kv/kv-v2.html#setup>`_.


.. doctest:: kvv2
   :skipif: client.sys.retrieve_mount_option('secret', 'version', '1') != '2' and os.getenv('HVAC_RENDER_DOCTESTS') is None

    >>> # Retrieve an authenticated hvac.Client() instance
    >>> client = test_utils.create_client()
    >>>
    >>> # Write a k/v pair under path: secret/foo
    >>> create_response = client.secrets.kv.v2.create_or_update_secret(
    ...     path='foo',
    ...     secret=dict(baz='bar'),
    ... )
    >>>
    >>> # Read the data written under path: secret/foo
    >>> read_response = client.secrets.kv.read_secret_version(path='foo')
    >>> print('Value under path "secret/foo" / key "baz": {val}'.format(
    ...     val=read_response['data']['data']['baz'],
    ... ))
    Value under path "secret/foo" / key "baz": bar
    >>>
    >>> # Delete all metadata/versions for path: secret/foo
    >>> client.secrets.kv.delete_metadata_and_all_versions('foo')
    <Response [204]>


KV Secrets Engine - Version 1
"""""""""""""""""""""""""""""

Preferred usage:

.. doctest:: kvv1
   :skipif: client.sys.retrieve_mount_option('secret', 'version', '1') != '1' and os.getenv('HVAC_RENDER_DOCTESTS') is None

    >>> client.secrets.kv.default_kv_version = '1'
    >>> create_response = client.secrets.kv.create_or_update_secret('foo', secret=dict(baz='bar'))
    >>> read_response = client.secrets.kv.read_secret('foo')
    >>> print('Value under path "secret/foo" / key "baz": {val}'.format(
    ...     val=read_response['data']['baz'],
    ... ))
    Value under path "secret/foo" / key "baz": bar
    >>> delete_response = client.secrets.kv.delete_secret('foo')



Generic usage:

.. note::

   The following `read()` and `write()` methods are roughly equivalent to the equivalent Vault CLI commands. These methods
    do not offer the same level of validation that hvac methods specific to individual auth methods and secrets engines provide.

.. doctest:: kvv1
   :skipif: client.sys.retrieve_mount_option('secret', 'version', '1') != '1' and os.getenv('HVAC_DOCTEST') is not None

    >>> client.write('secret/foo', baz='bar', lease='1h')
    >>> read_response = client.read('secret/foo')
    >>> print('Value under path "secret/foo" / key "baz": {val}'.format(
    ...     val=read_response['data']['baz'],
    ... ))
    Value under path "secret/foo" / key "baz": bar
    >>> client.delete('secret/foo')


Authentication
^^^^^^^^^^^^^^

Basic Token Authentication
""""""""""""""""""""""""""

.. doctest::

   # Token
   >>> client.token = os.environ['VAULT_TOKEN']
   >>> client.is_authenticated()
   True

LDAP Authentication Example
"""""""""""""""""""""""""""

.. testsetup:: ldap

    from tests.utils.mock_ldap_server import MockLdapServer
    ldap_server = MockLdapServer()
    ldap_server.start()
    client.sys.enable_auth_method(
        method_type='ldap',
    )
    client.auth.ldap.configure(
        url=ldap_server.url,
        bind_dn=ldap_server.ldap_bind_dn,
        bind_pass=ldap_server.ldap_bind_password,
        user_dn=ldap_server.ldap_users_dn,
        user_attr='uid',
        group_dn=ldap_server.ldap_groups_dn,
        group_attr='cn',
        insecure_tls=True,
    )
    client.auth.ldap.create_or_update_group(
        name=ldap_server.ldap_group_name,
        policies=['default'],
    )
    client.token = None

.. doctest:: ldap

   >>> client = hvac.Client(url='https://localhost:8200')
   >>> # LDAP, getpass -> user/password, bring in LDAP3 here for teststup?
   >>> login_response = client.auth.ldap.login(
   ...     username=os.environ['LDAP_USERNAME'],
   ...     password=os.environ['LDAP_PASSWORD'],
   ... )
   >>> client.is_authenticated()
   True
   >>> print('The client token returned from the LDAP auth method is: {token}'.format(
   ...     token=login_response['auth']['client_token']
   ... ))
   The client token returned from the LDAP auth method is: ...

.. testcleanup:: ldap

    client.token = os.environ['VAULT_TOKEN']
    ldap_server.stop()

Additional Information
----------------------

Additional documentation for this module available at: `hvac.readthedocs.io <https://hvac.readthedocs.io/en/stable/usage/index.html>`_.
