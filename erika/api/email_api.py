#!/usr/bin/env python3
"""
Erika Email API
===============

REST API endpoints for Erika's Gmail OAuth functionality.

Author: Living Archive team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone as dt_timezone

from ..models import ErikaEmailConfig
from ..plugins.email.gmail_service import ErikaGmailService, GmailValidationError, GmailAuthenticationError
from ..database import db_session

logger = logging.getLogger(__name__)


def get_email_config(user_id: str) -> Dict[str, Any]:
    """
    Get user's email configuration
    
    Args:
        user_id: User identifier (string)
        
    Returns:
        Dictionary with status and config data
    """
    try:
        with db_session() as session:
            # Get or create email config
            config = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.user_id == user_id
            ).first()
            
            if not config:
                config = ErikaEmailConfig(user_id=user_id)
                session.add(config)
                session.commit()
            
            # Return config without exposing secrets
            config_data = {
                'gmail_enabled': config.gmail_enabled,
                'gmail_check_interval': config.gmail_check_interval,
                'gmail_keywords': config.gmail_keywords or [],
                'is_active': config.is_active,
                'last_modified': config.last_modified.isoformat() if config.last_modified else None,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'has_credentials': bool(config.gmail_client_id)  # Don't expose client_secret
            }
            
            return {
                'status': 'success',
                'config': config_data
            }
        
    except Exception as e:
        logger.error(f"Error getting email config: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


def update_email_config(user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user's email configuration
    
    Args:
        user_id: User identifier (string)
        request_data: Dictionary with config fields to update
        
    Returns:
        Dictionary with status and message
    """
    try:
        with db_session() as session:
            # Get or create email config
            config = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.user_id == user_id
            ).first()
            
            if not config:
                config = ErikaEmailConfig(user_id=user_id)
                session.add(config)
            
            # Update config fields (with validation)
            if 'gmail_enabled' in request_data:
                if isinstance(request_data['gmail_enabled'], bool):
                    config.gmail_enabled = request_data['gmail_enabled']
            
            if 'gmail_check_interval' in request_data:
                interval = request_data['gmail_check_interval']
                if isinstance(interval, int) and 60 <= interval <= 86400:  # 1 minute to 24 hours
                    config.gmail_check_interval = interval
            
            if 'gmail_keywords' in request_data:
                keywords = request_data['gmail_keywords']
                if isinstance(keywords, list):
                    # Validate and sanitize keywords
                    sanitized_keywords = []
                    for kw in keywords[:20]:  # Limit to 20 keywords
                        if isinstance(kw, str) and len(kw.strip()) <= 100:
                            sanitized_keywords.append(kw.strip())
                    config.gmail_keywords = sanitized_keywords
            
            # OAuth credentials (should be set securely, not via API in production)
            if 'gmail_client_id' in request_data:
                client_id = request_data['gmail_client_id']
                if isinstance(client_id, str) and len(client_id) <= 500:
                    config.gmail_client_id = client_id
            
            if 'gmail_client_secret' in request_data:
                client_secret = request_data['gmail_client_secret']
                if isinstance(client_secret, str) and len(client_secret) <= 500:
                    config.gmail_client_secret = client_secret
            
            config.last_modified = datetime.now(dt_timezone.utc)
            
            return {
                'status': 'success',
                'message': 'Email configuration updated successfully',
                'config_id': str(config.id)
            }
        
    except Exception as e:
        logger.error(f"Error updating email config: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


def test_gmail_connection(user_id: str) -> Dict[str, Any]:
    """
    Test Gmail connection with current credentials
    
    Args:
        user_id: User identifier (string)
        
    Returns:
        Dictionary with status and connection result
    """
    try:
        with db_session() as session:
            # Get email config
            config = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.user_id == user_id
            ).first()
            
            if not config or not config.gmail_enabled:
                return {
                    'status': 'error',
                    'error': 'Gmail not configured for user'
                }
            
            if not config.gmail_client_id or not config.gmail_client_secret:
                return {
                    'status': 'error',
                    'error': 'Gmail OAuth credentials not configured'
                }
        
        # Initialize Gmail service
        gmail_service = ErikaGmailService(
            user_id=user_id,
            config={
                'gmail_client_id': config.gmail_client_id,
                'gmail_client_secret': config.gmail_client_secret,
                'gmail_keywords': config.gmail_keywords or []
            }
        )
        
        # Test authentication
        try:
            authenticated = gmail_service.authenticate(
                client_id=config.gmail_client_id,
                client_secret=config.gmail_client_secret
            )
            
            if authenticated:
                return {
                    'status': 'success',
                    'message': 'Gmail connection successful',
                    'authenticated': True
                }
            else:
                return {
                    'status': 'error',
                    'error': 'Gmail authentication failed',
                    'authenticated': False
                }
        except GmailAuthenticationError as e:
            return {
                'status': 'error',
                'error': str(e),
                'authenticated': False
            }
        
    except Exception as e:
        logger.error(f"Error testing Gmail connection: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

