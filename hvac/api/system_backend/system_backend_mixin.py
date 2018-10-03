"""Collection of Vault system backend API endpoint classes."""
import logging
from abc import ABCMeta, abstractproperty

logger = logging.getLogger(__name__)


class SystemBackendMixin(object):
    """Base class for System Backend API endpoints."""
    __metaclass__ = ABCMeta
    _adapter = None

    # @abstractproperty
    # def _adapter(self):
    #     """
    #
    #     :return:
    #     :rtype: hvac.adapters.Adapter
    #     """
    #     raise NotImplementedError

