KV Secrets Engines
==================

.. contents::
   :local:
   :depth: 1

.. testsetup:: kv

    client.sys.enable_secrets_engine(
        backend_type='kv',
        path='kv',
        options=dict(version=2),
    )

    # We occasionally see issues with the newly enabled secrets engine not becoming available in time for our test cases.
    # So we wait for it to show up in the mounted secrets engines list here before proceeding.
    attempts = 0
    while attempts < 25 and 'kv/' not in client.sys.list_mounted_secrets_engines()['data']:
        attempts += 1
        logging.debug('Waiting 1 second for KV V2 secrets engine under path {path} to become available...'.format(
            path='kv',
        ))
        sleep(1)

    hvac_secret = dict(pssst='this is secret')
    client.secrets.kv.v2.create_or_update_secret(
        path='hvac',
        secret=hvac_secret,
        mount_point='kv',
    )
    client.secrets.kv.v1.create_or_update_secret(
        path='hvac',
        secret=hvac_secret,
    )



The :py:class:`hvac.api.secrets_engines.Kv` instance under the :py:attr:`Client class's kv attribute<hvac.v1.Client.kv>` is a wrapper to expose either version 1 (:py:class:`KvV1<hvac.api.secrets_engines.KvV1>`) or version 2 of the key/value secrets engines' API methods (:py:class:`KvV2<hvac.api.secrets_engines.KvV2>`). At present, this class defaults to version 2 when accessing methods on the instance.



Setting the Default KV Version
------------------------------

Examples
````````

.. testcode:: kv

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    client.secrets.kv.default_kv_version = 1
    client.secrets.kv.read_secret(path='hvac')  # => calls hvac.api.secrets_engines.KvV1.read_secret

Explicitly Calling a KV Version Method
--------------------------------------

.. testcode:: kv

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    client.secrets.kv.v1.read_secret(path='hvac')
    client.secrets.kv.v2.read_secret_version(path='hvac', mount_point='kv')


Specific KV Version Usage
-------------------------

.. toctree::
   :maxdepth: 2

   ../secrets_engines/kv_v1
   ../secrets_engines/kv_v2
