"""Collection of classes for various Vault auth methods."""

from hvac.api.auth_methods.azure import Azure
from hvac.api.auth_methods.gcp import Gcp
from hvac.api.auth_methods.github import Github
from hvac.api.auth_methods.ldap import Ldap
from hvac.api.auth_methods.mfa import Mfa

__all__ = (
    'Azure',
    'Gcp',
    'Github',
    'Ldap',
    'Mfa',
)
