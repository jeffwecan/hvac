<<<<<<< Updated upstream
"""Collection of Vault API endpoint classes."""
from hvac.api import auth
from hvac.api.azure import Azure
from hvac.api import secrets_engines
from hvac.api.vault_api_base import VaultApiBase

__all__ = (
    'auth',
    'Azure',
    'secrets_engines',
    'VaultApiBase',
)
=======
"""
Vault API Endpoints

"""
from hvac.api.aws import AWS

__all__ = [
    'AWS'
]
>>>>>>> Stashed changes
