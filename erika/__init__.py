#!/usr/bin/env python3
"""
Erika - Gmail OAuth Integration
================================

Gmail OAuth integration library for email processing.

Author: Living Archive team
Version: 1.0.0
"""

# Core exports
from .plugins.email import (
    ErikaGmailService,
    OAuthTokenManager,
    EmailPlugin,
    get_gmail_service_for_user,
)

from .models import ErikaEmailConfig

from .api import (
    get_email_config,
    update_email_config,
    test_gmail_connection,
)

from .services import ErikaEgoLlamaGateway

__all__ = [
    # Gmail Service
    'ErikaGmailService',
    'OAuthTokenManager',
    'EmailPlugin',
    'get_gmail_service_for_user',
    
    # Models
    'ErikaEmailConfig',
    
    # API
    'get_email_config',
    'update_email_config',
    'test_gmail_connection',
    
    # EgoLlama Gateway
    'ErikaEgoLlamaGateway',
]

__version__ = '1.0.0'

