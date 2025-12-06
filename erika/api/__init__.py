#!/usr/bin/env python3
"""
Erika API
=========

API endpoints for Gmail OAuth integration.

Author: EGO Revolution Team
Version: 1.0.0
"""

from .email_api import (
    get_email_config,
    update_email_config,
    test_gmail_connection,
)

__all__ = [
    'get_email_config',
    'update_email_config',
    'test_gmail_connection',
]

