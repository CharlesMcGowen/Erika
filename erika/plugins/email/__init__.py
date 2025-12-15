#!/usr/bin/env python3
"""
Erika Email Plugin Package
==========================

Email integration for Erika supporting multiple providers:
- Gmail (OAuth2)
- IMAP (generic email servers)
"""

from .base_email_service import (
    BaseEmailService,
    EmailServiceError,
    EmailAuthenticationError,
    EmailValidationError
)
from .gmail_service import ErikaGmailService
from .imap_service import IMAPService
from .oauth_token_manager import OAuthTokenManager
from .plugin import EmailPlugin

# Legacy exports for backward compatibility
try:
    from .gmail_service import get_gmail_service_for_user, check_gmail_for_user
except ImportError:
    def get_gmail_service_for_user(*args, **kwargs):
        """Placeholder if function doesn't exist"""
        return None
    def check_gmail_for_user(*args, **kwargs):
        """Placeholder if function doesn't exist"""
        return False

__all__ = [
    'BaseEmailService',
    'EmailServiceError',
    'EmailAuthenticationError',
    'EmailValidationError',
    'ErikaGmailService',
    'IMAPService',
    'OAuthTokenManager',
    'EmailPlugin',
    'get_gmail_service_for_user',
    'check_gmail_for_user',
]
