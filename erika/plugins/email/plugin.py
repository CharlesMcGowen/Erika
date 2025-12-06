#!/usr/bin/env python3
"""
Erika Email Plugin
==================

Gmail OAuth integration plugin for Erika.

Author: EGO Revolution Team
Version: 1.0.0
"""

import logging
from ..base import ErikaPlugin
from .gmail_service import ErikaGmailService

logger = logging.getLogger(__name__)


class EmailPlugin(ErikaPlugin):
    """Email processing plugin for Erika - Gmail OAuth integration"""
    
    @property
    def name(self) -> str:
        return 'email'
    
    @property
    def version(self) -> str:
        return '1.0.0'
    
    @property
    def description(self) -> str:
        return "Gmail OAuth integration for email processing"
    
    def __init__(self):
        self.gmail_service = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize email plugin components"""
        try:
            # Gmail service is initialized per-user, so we don't create it here
            self._initialized = True
            logger.info("✅ Email plugin initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize email plugin: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown email plugin"""
        self._initialized = False
        logger.info("Email plugin shut down")

