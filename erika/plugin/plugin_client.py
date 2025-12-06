#!/usr/bin/env python3
"""
Erika Plugin Client
===================

Client for connecting Erika plugin to EgoLlama Gateway.
Handles plugin registration and connection management.

Author: Living Archive team
Version: 1.0.0
"""

import logging
import requests
import time
from typing import Optional, Dict, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class PluginConnectionError(Exception):
    """Exception for plugin connection errors"""
    pass


class ErikaPluginClient:
    """
    Client for connecting Erika to EgoLlama Gateway
    
    This client:
    1. Connects to EgoLlama Gateway
    2. Registers Erika as a plugin
    3. Keeps connection alive
    4. Handles reconnection on failure
    """
    
    def __init__(self, egollama_url: str = "http://localhost:8082"):
        """
        Initialize plugin client
        
        Args:
            egollama_url: EgoLlama Gateway URL
        """
        self.egollama_url = egollama_url.rstrip('/')
        self.registered = False
        self.plugin_name = "erika"
        self.plugin_version = "1.0.0"
        
    def check_gateway_health(self) -> bool:
        """
        Check if EgoLlama Gateway is available
        
        Returns:
            True if gateway is reachable
        """
        try:
            response = requests.get(
                f"{self.egollama_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Gateway health check failed: {e}")
            return False
    
    def register_plugin(self) -> bool:
        """
        Register Erika plugin with EgoLlama Gateway
        
        Returns:
            True if registration successful
        """
        try:
            # Check gateway health first
            if not self.check_gateway_health():
                logger.warning(f"⚠️  EgoLlama Gateway not available at {self.egollama_url}")
                return False
            
            # Get plugin URL (if running as standalone server)
            # For now, Erika registers metadata only
            # The router will be included if Erika is installed locally in EgoLlama
            plugin_url = None  # Can be set if Erika runs its own server
            
            # Prepare registration data
            registration_data = {
                "plugin_name": self.plugin_name,
                "version": self.plugin_version,
                "description": "Erika Email Assistant - AI-powered email management and analysis",
                "author": "Living Archive team",
                "endpoints": [
                    "/api/erika/health",
                    "/api/erika/emails",
                    "/api/erika/emails/{email_id}",
                    "/api/erika/emails/analyze",
                    "/api/erika/gmail/connect",
                    "/api/erika/gmail/status",
                    "/api/erika/gmail/disconnect",
                    "/api/erika/stats"
                ],
                "plugin_url": plugin_url,
                "metadata": {
                    "type": "email_assistant",
                    "capabilities": [
                        "email_reading",
                        "email_analysis",
                        "phishing_detection",
                        "gmail_oauth"
                    ]
                }
            }
            
            # Register plugin
            response = requests.post(
                f"{self.egollama_url}/api/plugins/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Erika plugin registered with EgoLlama Gateway")
                logger.info(f"   Plugin: {result.get('plugin', {}).get('name', 'erika')}")
                logger.info(f"   Endpoints: {len(result.get('plugin', {}).get('endpoints', []))}")
                self.registered = True
                return True
            else:
                logger.error(f"❌ Plugin registration failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Cannot connect to EgoLlama Gateway at {self.egollama_url}")
            logger.error("   Make sure EgoLlama Gateway is running")
            return False
        except Exception as e:
            logger.error(f"❌ Error registering plugin: {e}", exc_info=True)
            return False
    
    def unregister_plugin(self) -> bool:
        """Unregister plugin from gateway"""
        try:
            response = requests.delete(
                f"{self.egollama_url}/api/plugins/{self.plugin_name}",
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Erika plugin unregistered")
                self.registered = False
                return True
            return False
        except Exception as e:
            logger.error(f"Error unregistering plugin: {e}")
            return False
    
    def get_plugin_info(self) -> Optional[Dict[str, Any]]:
        """Get plugin information from gateway"""
        try:
            response = requests.get(
                f"{self.egollama_url}/api/plugins/{self.plugin_name}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json().get('plugin')
            return None
        except Exception as e:
            logger.debug(f"Error getting plugin info: {e}")
            return None
    
    def keep_alive(self, interval: int = 60):
        """
        Keep plugin connection alive by periodically checking gateway
        
        Args:
            interval: Check interval in seconds (default: 60)
        """
        logger.info(f"🔄 Starting keep-alive loop (interval: {interval}s)")
        
        while True:
            try:
                time.sleep(interval)
                
                # Check gateway health
                if not self.check_gateway_health():
                    logger.warning("⚠️  Gateway connection lost, attempting reconnection...")
                    self.registered = False
                    # Try to re-register
                    if self.register_plugin():
                        logger.info("✅ Reconnected to gateway")
                    else:
                        logger.warning("⚠️  Reconnection failed, will retry...")
                else:
                    # Gateway is healthy, verify registration
                    if not self.registered:
                        logger.info("🔄 Gateway available, re-registering plugin...")
                        self.register_plugin()
                    else:
                        # Check if we're still registered
                        info = self.get_plugin_info()
                        if not info:
                            logger.warning("⚠️  Plugin not found in gateway, re-registering...")
                            self.register_plugin()
                        
            except KeyboardInterrupt:
                logger.info("🛑 Keep-alive loop interrupted")
                break
            except Exception as e:
                logger.error(f"Error in keep-alive loop: {e}")
                time.sleep(interval)  # Wait before retrying

