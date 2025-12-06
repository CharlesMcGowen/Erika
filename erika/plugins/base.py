#!/usr/bin/env python3
"""
Erika Plugin Base Interface
============================

Base class for all Erika plugins implementing the plugin interface.

Author: Living Archive team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ErikaPlugin(ABC):
    """Base class for all Erika plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name (must be unique)"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @property
    def description(self) -> str:
        """Plugin description (optional)"""
        return ""
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize plugin
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown plugin and cleanup resources"""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get plugin configuration
        
        Returns:
            Dict[str, Any]: Plugin configuration dictionary
        """
        return {}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get plugin status information
        
        Returns:
            Dict[str, Any]: Plugin status dictionary
        """
        return {
            'name': self.name,
            'version': self.version,
            'initialized': hasattr(self, '_initialized') and self._initialized,
        }
    
    def validate(self) -> bool:
        """
        Validate plugin configuration and dependencies
        
        Returns:
            bool: True if plugin is valid, False otherwise
        """
        return True

