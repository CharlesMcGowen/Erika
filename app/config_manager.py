#!/usr/bin/env python3
"""
Configuration Manager for Erika
================================

Manages application configuration including EgoLlama Gateway settings.

Author: Living Archive team
Version: 1.0.0
"""

import json
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ErikaConfigManager:
    """Manages Erika application configuration"""
    
    def __init__(self):
        self.config_path = Path.home() / ".erika" / "config.json"
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self._config = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
                self._config = {}
        else:
            self._config = {}
    
    def get_gateway_url(self) -> str:
        """
        Get EgoLlama Gateway URL
        
        Priority:
        1. Environment variable EGOLLAMA_GATEWAY_URL
        2. Config file
        3. Default: http://localhost:8082
        
        Returns:
            Gateway URL string
        """
        # Check environment variable first
        env_url = os.getenv('EGOLLAMA_GATEWAY_URL')
        if env_url:
            return env_url
        
        # Check config file
        if self._config:
            config_url = self._config.get('egollama_gateway_url')
            if config_url:
                return config_url
        
        # Default
        return "http://localhost:8082"
    
    def set_gateway_url(self, url: str):
        """Set gateway URL in config file"""
        if not self._config:
            self._config = {}
        
        self._config['egollama_gateway_url'] = url
        self._config['configured'] = True
        
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"✅ Saved gateway URL: {url}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise
    
    def is_configured(self) -> bool:
        """Check if configuration exists"""
        return self._config.get('configured', False) if self._config else False
    
    def get_config(self) -> Dict[str, Any]:
        """Get full configuration dictionary"""
        return self._config.copy() if self._config else {}
    
    def get_database_url(self) -> Optional[str]:
        """
        Get database URL
        
        Priority:
        1. Environment variable DATABASE_URL
        2. Config file
        3. None (use defaults)
        
        Returns:
            Database URL string or None
        """
        # Check environment variable first
        env_url = os.getenv('DATABASE_URL')
        if env_url:
            return env_url
        
        # Check config file
        if self._config:
            return self._config.get('database_url')
        
        return None
    
    def set_database_url(self, url: str):
        """Set database URL in config file"""
        if not self._config:
            self._config = {}
        
        self._config['database_url'] = url
        
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info("✅ Saved database URL")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

