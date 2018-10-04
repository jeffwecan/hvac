"""Collection of Vault API endpoint classes."""
from hvac.api import auth_methods
from hvac.api import secrets_engines
from hvac.api.azure import Azure
from hvac.api.vault_api_base import VaultApiBase

__all__ = (
    'auth_methods',
    'Azure',
    'secrets_engines',
    'VaultApiBase',
)
