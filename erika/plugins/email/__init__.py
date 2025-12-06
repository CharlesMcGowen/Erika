#!/usr/bin/env python3
"""
Erika Email Plugin
==================

Gmail OAuth integration for email processing.

Author: EGO Revolution Team
Version: 1.0.0
"""

from .gmail_service import ErikaGmailService, get_gmail_service_for_user

# check_gmail_for_user may not exist - make it optional
try:
    from .gmail_service import check_gmail_for_user
except ImportError:
    def check_gmail_for_user(*args, **kwargs):
        """Placeholder if function doesn't exist"""
        return False
from .oauth_token_manager import OAuthTokenManager
from .plugin import EmailPlugin

__all__ = [
    'ErikaGmailService',
    'OAuthTokenManager',
    'EmailPlugin',
    'get_gmail_service_for_user',
    'check_gmail_for_user',
]

