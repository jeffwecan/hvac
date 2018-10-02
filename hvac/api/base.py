"""
Base Endpoint class used by all "api" classes

"""
import logging
from abc import ABCMeta

logger = logging.getLogger(__name__)


class Endpoint(object):
    """Base class for API endpoints"""
    __metaclass__ = ABCMeta

    def __init__(self, adapter):
        self._adapter = adapter
