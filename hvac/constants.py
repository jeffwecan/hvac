
VALID_AZURE_ENVIRONMENTS = [
    'AzurePublicCloud',
    'AzureUSGovernmentCloud',
    'AzureChinaCloud',
    'AzureGermanCloud',
]

DEPRECATED_CLIENT_PROPERTIES = {
    'github': dict(
        to_be_removed_in_version='0.8.0',
        client_property='auth',
    ),
    'ldap': dict(
        to_be_removed_in_version='0.8.0',
        client_property='auth',
    ),
    'mfa': dict(
        to_be_removed_in_version='0.8.0',
        client_property='auth',
    ),
}
