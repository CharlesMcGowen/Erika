#!/usr/bin/env python3
"""
Erika Plugin Registry
=====================

Central plugin registry for auto-discovery and management of Erika plugins.

Author: Living Archive team
Version: 1.0.0
"""

from typing import Dict, Type, Optional
import logging
from .base import ErikaPlugin

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central plugin registry for Erika"""
    
    _plugins: Dict[str, ErikaPlugin] = {}
    _plugin_classes: Dict[str, Type[ErikaPlugin]] = {}
    _initialized: bool = False
    
    @classmethod
    def register(cls, plugin_class: Type[ErikaPlugin]) -> ErikaPlugin:
        """
        Register a plugin class
        
        Args:
            plugin_class: Plugin class to register
            
        Returns:
            ErikaPlugin: Plugin instance
        """
        try:
            instance = plugin_class()
            plugin_name = instance.name
            
            if plugin_name in cls._plugins:
                logger.warning(f"Plugin '{plugin_name}' already registered, overwriting")
            
            cls._plugin_classes[plugin_name] = plugin_class
            cls._plugins[plugin_name] = instance
            
            logger.info(f"✅ Registered plugin: {plugin_name} v{instance.version}")
            return instance
            
        except Exception as e:
            logger.error(f"❌ Failed to register plugin {plugin_class.__name__}: {e}")
            raise
    
    @classmethod
    def get(cls, name: str) -> Optional[ErikaPlugin]:
        """
        Get plugin instance by name
        
        Args:
            name: Plugin name
            
        Returns:
            ErikaPlugin or None: Plugin instance if found
        """
        return cls._plugins.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, ErikaPlugin]:
        """
        Get all registered plugins
        
        Returns:
            Dict[str, ErikaPlugin]: Dictionary of all plugins
        """
        return cls._plugins.copy()
    
    @classmethod
    def initialize_all(cls) -> bool:
        """
        Initialize all registered plugins
        
        Returns:
            bool: True if all plugins initialized successfully
        """
        if cls._initialized:
            logger.debug("Plugins already initialized")
            return True
        
        success = True
        for name, plugin in cls._plugins.items():
            try:
                if plugin.initialize():
                    plugin._initialized = True
                    logger.info(f"✅ Initialized plugin: {name}")
                else:
                    logger.error(f"❌ Failed to initialize plugin: {name}")
                    success = False
            except Exception as e:
                logger.error(f"❌ Error initializing plugin {name}: {e}")
                success = False
        
        cls._initialized = success
        return success
    
    @classmethod
    def shutdown_all(cls) -> None:
        """Shutdown all registered plugins"""
        for name, plugin in cls._plugins.items():
            try:
                plugin.shutdown()
                logger.info(f"✅ Shutdown plugin: {name}")
            except Exception as e:
                logger.error(f"❌ Error shutting down plugin {name}: {e}")
        
        cls._initialized = False
    
    @classmethod
    def list_plugins(cls) -> list:
        """
        List all registered plugins
        
        Returns:
            list: List of plugin names
        """
        return list(cls._plugins.keys())
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if plugins are initialized"""
        return cls._initialized


# Export registry
__all__ = ['PluginRegistry', 'ErikaPlugin']

