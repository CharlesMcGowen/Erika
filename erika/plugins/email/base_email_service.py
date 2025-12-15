#!/usr/bin/env python3
"""
Base Email Service Interface
============================

Abstract base class for all email service providers (Gmail, IMAP, Office365, etc.)

Author: Living Archive team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class EmailServiceError(Exception):
    """Base exception for email service errors"""
    pass


class EmailAuthenticationError(EmailServiceError):
    """Exception for email authentication errors"""
    pass


class EmailValidationError(EmailServiceError):
    """Exception for input validation errors"""
    pass


class BaseEmailService(ABC):
    """
    Abstract base class for all email service providers.
    
    All email providers (Gmail, IMAP, Office365, etc.) must implement this interface.
    """
    
    def __init__(self, user_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize email service
        
        Args:
            user_id: User identifier
            config: Configuration dictionary (provider-specific)
        """
        self.user_id = user_id or "default"
        self.config = config or {}
        self._authenticated = False
    
    @abstractmethod
    def authenticate(self, **kwargs) -> bool:
        """
        Authenticate with email provider
        
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            EmailAuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def get_unread_emails(
        self,
        max_results: int = 50,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get unread emails from the provider
        
        Args:
            max_results: Maximum number of emails to retrieve
            days_back: Number of days to look back
            
        Returns:
            List of email dictionaries with:
                - id: Email ID (provider-specific)
                - subject: Email subject
                - sender: Sender email/name
                - date: Email date
                - body: Email body (sanitized)
                - thread_id: Thread ID (if available)
        """
        pass
    
    @abstractmethod
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None
    ) -> bool:
        """
        Send email via provider
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            thread_id: Optional thread ID for replies
            
        Returns:
            True if sent successfully, False otherwise
            
        Raises:
            EmailValidationError: If input validation fails
        """
        pass
    
    def get_email_details(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific email
        
        Args:
            email_id: Email ID (provider-specific)
            
        Returns:
            Email dictionary with full details, or None if not found
        """
        # Default implementation: get from unread emails
        emails = self.get_unread_emails(max_results=1000, days_back=30)
        for email in emails:
            if email.get('id') == email_id:
                return email
        return None
    
    def is_authenticated(self) -> bool:
        """Check if service is authenticated"""
        return self._authenticated
    
    def get_provider_name(self) -> str:
        """Get provider name (e.g., 'gmail', 'imap', 'office365')"""
        return self.__class__.__name__.replace('Service', '').lower()
    
    def validate_email_address(self, email: str) -> bool:
        """
        Validate email address format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        import re
        if not email or not isinstance(email, str):
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email.strip()))
