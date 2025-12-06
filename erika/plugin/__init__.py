#!/usr/bin/env python3
"""
Erika Plugin for EgoLlama Gateway
==================================

Plugin system for integrating Erika as an external plugin with EgoLlama Gateway.
"""

from .erika_plugin import ErikaPlugin
from .erika_router import router as erika_router
from .plugin_client import ErikaPluginClient

__all__ = ['ErikaPlugin', 'erika_router', 'ErikaPluginClient']

