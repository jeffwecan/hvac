Transit
=======

.. contents::
   :local:
   :depth: 1

.. testsetup:: transit, transit_delete_key, transit_export_key, transit_backup_and_restore_key, transit_trim_key

    client.sys.enable_secrets_engine(
        backend_type='transit',
    )

Create Key
----------

.. automethod:: hvac.api.secrets_engines.Transit.create_key
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    client.secrets.transit.create_key(
        name='hvac-key',
        key_type='rsa-4096',
    )

Read Key
--------

.. automethod:: hvac.api.secrets_engines.Transit.create_key
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    read_key_response = client.secrets.transit.read_key(name='hvac-key')
    latest_version = read_key_response['data']['latest_version']
    print('Latest version for key "hvac-key" is: {ver}'.format(ver=latest_version))

Example output:

.. testoutput:: transit

    Latest version for key "hvac-key" is: 1


List Keys
---------

.. automethod:: hvac.api.secrets_engines.Transit.read_key
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    list_keys_response = client.secrets.transit.read_key(name='hvac-key')
    keys = list_keys_response['data']['keys']
    print('Currently configured keys: {keys}'.format(keys=keys))

Example output:

.. testoutput:: transit

    Currently configured keys: {'1': ...}


Delete Key
----------

.. automethod:: hvac.api.secrets_engines.Transit.delete_key
   :noindex:

Examples
````````

.. testsetup:: transit_delete_key

    client.secrets.transit.create_key(
        name='hvac-key-deleteme',
    )

    client.secrets.transit.update_key_configuration(
        name='hvac-key-deleteme',
        deletion_allowed=True,
    )

.. note::

    By default deletion of keys is not allowed. To allow this destructive action, the previously created key needs to be updated to set `deletion_allowed` parameter set to `True`.

.. testcode:: transit_delete_key

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')
    client.secrets.transit.delete_key(name='hvac-key-deleteme')


Update Key Configuration
------------------------

.. automethod:: hvac.api.secrets_engines.Transit.update_key_configuration
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    # allow key "hvac-key" to be exported in subsequent requests
    client.secrets.transit.update_key_configuration(
        name='hvac-key',
        exportable=True,
    )


Rotate Key
----------

.. automethod:: hvac.api.secrets_engines.Transit.rotate_key
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')
    client.secrets.transit.rotate_key(name='hvac-key')

Export Key
----------

.. automethod:: hvac.api.secrets_engines.Transit.export_key
   :noindex:

Examples
````````

.. testsetup:: transit_export_key

    client.secrets.transit.create_key(
        name='hvac-key',
    )

    client.secrets.transit.update_key_configuration(
        name='hvac-key',
        exportable=True,
    )

.. testcode:: transit_export_key

    import hvac

    client = hvac.Client(url='https://127.0.0.1:8200')
    export_key_response = client.secrets.transit.export_key(
        name='hvac-key',
        key_type='hmac-key',
    )

    print('Exported keys: {keys}'.format(keys=export_key_response['data']['keys']))

Example output:

.. testoutput:: transit_export_key

    Exported keys: {'1': ...

Encrypt Data
------------

.. automethod:: hvac.api.secrets_engines.Transit.encrypt_data
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    from tests.utils import base64ify

    client = hvac.Client(url='https://127.0.0.1:8200')

    encrypt_data_response = client.secrets.transit.encrypt_data(
        name='hvac-key',
        plaintext=base64ify('hi its me hvac'),
    )
    ciphertext = encrypt_data_response['data']['ciphertext']
    print('Encrypted plaintext ciphertext is: {cipher}'.format(cipher=ciphertext))

Example output:

.. testoutput:: transit

    Encrypted plaintext ciphertext is: ...


Decrypt Data
------------

.. automethod:: hvac.api.secrets_engines.Transit.decrypt_data
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    decrypt_data_response = client.secrets.transit.decrypt_data(
        name='hvac-key',
        ciphertext=ciphertext,
    )
    plaintext = decrypt_data_response['data']['plaintext']
    print('Encrypted plaintext is: {text}'.format(text=plaintext))

Example output:

.. testoutput:: transit

    Encrypted plaintext is: ...


Rewrap Data
-----------

.. automethod:: hvac.api.secrets_engines.Transit.rewrap_data
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    encrypt_data_response = client.secrets.transit.rewrap_data(
        name='hvac-key',
        ciphertext=ciphertext,
    )
    rewrapped_ciphertext = encrypt_data_response['data']['ciphertext']
    print('Rewrapped ciphertext is: {cipher}'.format(cipher=rewrapped_ciphertext))

Example output:

.. testoutput:: transit

    Rewrapped ciphertext is: ...


Generate Data Key
-----------------

.. automethod:: hvac.api.secrets_engines.Transit.generate_data_key
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')
    gen_data_key_response = client.secrets.transit.generate_data_key(
        name='hvac-key',
        key_type='plaintext',
    )
    ciphertext = gen_data_key_response['data']
    print('Generated data key is: {cipher}'.format(cipher=ciphertext))

Example output:

.. testoutput:: transit

    Generated data key is: {'ciphertext': '...', 'plaintext': '...'}


Generate Random Bytes
---------------------

.. automethod:: hvac.api.secrets_engines.Transit.generate_random_bytes
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    client = hvac.Client(url='https://127.0.0.1:8200')

    gen_bytes_response = client.secrets.transit.generate_random_bytes(n_bytes=32)
    random_bytes = gen_bytes_response['data']['random_bytes']
    print('Here are some random bytes: {bytes}'.format(bytes=random_bytes))

Example output:

.. testoutput:: transit

    Here are some random bytes: ...



Hash Data
---------

.. automethod:: hvac.api.secrets_engines.Transit.hash_data
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    from tests.utils import base64ify

    client = hvac.Client(url='https://127.0.0.1:8200')

    hash_data_response = client.secrets.transit.hash_data(
        hash_input=base64ify('hi its me hvac'),
    )
    sum = hash_data_response['data']['sum']
    print('Hashed data is: {sum}'.format(sum=sum))

Example output:

.. testoutput:: transit

    Hashed data is: ...


Generate Hmac
-------------

.. automethod:: hvac.api.secrets_engines.Transit.generate_hmac
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    from tests.utils import base64ify

    client = hvac.Client(url='https://127.0.0.1:8200')

    generate_hmac_response = client.secrets.transit.generate_hmac(
        name='hvac-key',
        hash_input=base64ify('hi its me hvac'),
    )
    hmac = generate_hmac_response['data']['hmac']
    print("HMAC'd data is: {hmac}".format(hmac=hmac))

Example output:

.. testoutput:: transit

    HMAC'd data is: ...


Sign Data
---------

.. automethod:: hvac.api.secrets_engines.Transit.sign_data
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    from tests.utils import base64ify

    client = hvac.Client(url='https://127.0.0.1:8200')

    sign_data_response = client.secrets.transit.sign_data(
        name='hvac-key',
        hash_input=base64ify('hi its me hvac'),
    )
    signature = sign_data_response['data']['signature']
    print('Signature is: {signature}'.format(signature=signature))

Example output:

.. testoutput:: transit

    Signature is: ...


Verify Signed Data
------------------

.. automethod:: hvac.api.secrets_engines.Transit.verify_signed_data
   :noindex:

Examples
````````

.. testcode:: transit

    import hvac
    from tests.utils import base64ify

    client = hvac.Client(url='https://127.0.0.1:8200')

    verify_signed_data_response = client.secrets.transit.verify_signed_data(
        name='hvac-key',
        hash_input=base64ify('hi its me hvac'),
        signature=signature,
    )
    valid = verify_signed_data_response['data']['valid']
    print('Signature is valid?: {valid}'.format(valid=valid))

Example output:

.. testoutput:: transit

    Signature is valid?: True


Backup Key
----------

.. automethod:: hvac.api.secrets_engines.Transit.backup_key
   :noindex:

Examples
````````

.. note::

    By default deletion of keys is not allowed. To allow action, the previously created key needs to be updated to set `allow_plaintext_backup` parameter set to `True`.

.. testsetup:: transit_backup_and_restore_key

    client.secrets.transit.create_key(
        name='hvac-key',
    )

    client.secrets.transit.update_key_configuration(
        name='hvac-key',
        exportable=True,
        allow_plaintext_backup=True,
        deletion_allowed=True,
    )

.. testcode:: transit_backup_and_restore_key

    import hvac

    client = hvac.Client(url='https://127.0.0.1:8200')

    backup_key_response = client.secrets.transit.backup_key(
        name='hvac-key',
    )
    backed_up_key = backup_key_response['data']['backup']
    print('Backup key data: {key}'.format(key=backed_up_key))

Example output:

.. testoutput:: transit_backup_and_restore_key

    Backup key data: ...

Restore Key
-----------

.. automethod:: hvac.api.secrets_engines.Transit.restore_key
   :noindex:

Examples
````````

.. testcode:: transit_backup_and_restore_key

    import hvac

    client = hvac.Client(url='https://127.0.0.1:8200')
    client.secrets.transit.restore_key(
        backup=backed_up_key,
        name='restored-hvac-key',
    )


Trim Key
--------

.. automethod:: hvac.api.secrets_engines.Transit.trim_key
   :noindex:

Examples
````````

.. testsetup:: transit_trim_key

    client = hvac.Client(url='https://127.0.0.1:8200')

    client.secrets.transit.create_key(
        name='hvac-key',
        key_type='rsa-4096',
    )
    for _ in range(0, 5):
        client.secrets.transit.rotate_key(name='hvac-key')



.. testcode:: transit_trim_key

    import hvac

    client = hvac.Client(url='https://127.0.0.1:8200')

    # "minimum available version cannot be set when minimum encryption version is not set"
    client.secrets.transit.update_key_configuration(
        name='hvac-key',
        min_decryption_version=2,
        min_encryption_version=4,
    )

    client.secrets.transit.trim_key(
        name='hvac-key',
        min_version=1,
    )

.. testcleanup:: transit, transit_delete_key, transit_export_key, transit_backup_and_restore_key, transit_trim_key

    client.sys.disable_secrets_engine(
        path='transit',
    )
