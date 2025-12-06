#!/usr/bin/env python3
"""
Erika Plugin
============

Main plugin class for integrating Erika with EgoLlama Gateway.
Handles plugin initialization, router creation, and registration.

Author: Living Archive team
Version: 1.0.0
"""

import logging
from typing import Optional
from fastapi import FastAPI

from .erika_router import router as erika_router
from .plugin_client import ErikaPluginClient

logger = logging.getLogger(__name__)


class ErikaPlugin:
    """
    Erika Plugin for EgoLlama Gateway
    
    This plugin provides email management and analysis capabilities
    to EgoLlama Gateway as an external plugin.
    """
    
    def __init__(self, egollama_url: str = "http://localhost:8082"):
        """
        Initialize Erika plugin
        
        Args:
            egollama_url: EgoLlama Gateway URL
        """
        self.egollama_url = egollama_url
        self.router = erika_router
        self.client = ErikaPluginClient(egollama_url)
        self._app: Optional[FastAPI] = None
    
    def get_router(self):
        """Get the FastAPI router for this plugin"""
        return self.router
    
    def register_with_gateway(self) -> bool:
        """
        Register this plugin with EgoLlama Gateway
        
        Returns:
            True if registration successful
        """
        return self.client.register_plugin()
    
    def unregister_from_gateway(self) -> bool:
        """Unregister plugin from gateway"""
        return self.client.unregister_plugin()
    
    def create_standalone_app(self) -> FastAPI:
        """
        Create a standalone FastAPI app for testing/development
        
        This is useful for testing the plugin independently
        before registering with EgoLlama Gateway.
        
        Returns:
            FastAPI application instance
        """
        if self._app is None:
            self._app = FastAPI(
                title="Erika Email Assistant",
                description="Standalone Erika plugin for testing",
                version="1.0.0"
            )
            self._app.include_router(self.router)
        
        return self._app
    
    def is_registered(self) -> bool:
        """Check if plugin is registered with gateway"""
        return self.client.registered
    
    def get_plugin_info(self):
        """Get plugin information from gateway"""
        return self.client.get_plugin_info()

