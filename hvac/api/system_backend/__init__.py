"""Collection of Vault system backend API endpoint classes."""
import logging

from hvac.api.system_backend.audit import Audit
from hvac.api.system_backend.auth import Auth
from hvac.api.system_backend.health import Health
from hvac.api.system_backend.init import Init
from hvac.api.system_backend.key import Key
from hvac.api.system_backend.leader import Leader
from hvac.api.system_backend.lease import Lease
from hvac.api.system_backend.mount import Mount
from hvac.api.system_backend.policy import Policy
from hvac.api.system_backend.seal import Seal
from hvac.api.system_backend.wrapping import Wrapping
from hvac.api.system_backend.system_backend_mixin import SystemBackendMixin
from hvac.api.vault_api_base import VaultApiBase

__all__ = (
    'Audit',
    'SystemBackend',
    'SystemBackendMixin',
)


logger = logging.getLogger(__name__)


class SystemBackend(VaultApiBase, Audit, Auth, Health, Init, Key, Leader, Lease, Mount, Policy, Seal, Wrapping):
    pass
