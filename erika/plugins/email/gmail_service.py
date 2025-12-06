#!/usr/bin/env python3
"""
Gmail Service for Erika AI
==========================

Gmail OAuth integration for reading and sending emails.

Security Features:
- HTML sanitization for email content
- Input validation for all email fields
- Secure base64 decoding with error handling
- OAuth token management via OAuthTokenManager

Author: Living Archive team
Version: 1.0.0
"""

import logging
import base64
import re
import html
from datetime import datetime, timedelta, timezone as dt_timezone
from email.mime.text import MIMEText
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import HTML sanitization library, fallback to basic escaping
try:
    from html_sanitizer import Sanitizer
    _has_sanitizer = True
except ImportError:
    _has_sanitizer = False
    logger.warning("html_sanitizer not available, using basic HTML escaping")


class GmailServiceError(Exception):
    """Base exception for Gmail service errors"""
    pass


class GmailAuthenticationError(GmailServiceError):
    """Exception for Gmail authentication errors"""
    pass


class GmailValidationError(GmailServiceError):
    """Exception for input validation errors"""
    pass


def _sanitize_html(html_content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        Sanitized HTML string
    """
    if not html_content:
        return ""
    
    if _has_sanitizer:
        # Use html_sanitizer library for comprehensive sanitization
        sanitizer = Sanitizer({
            'tags': ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li'],
            'attributes': {'a': ('href',)},
            'empty': {'br'},
            'separate': {'a', 'p'},
        })
        return sanitizer.sanitize(html_content)
    else:
        # Fallback: Basic HTML escaping (removes all HTML tags)
        # This is safer but less feature-rich
        return html.escape(html_content)


def _validate_email_address(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex (RFC 5322 simplified)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))


def _validate_text_field(text: str, field_name: str, max_length: int = 10000) -> str:
    """
    Validate and sanitize text field
    
    Args:
        text: Text to validate
        field_name: Name of the field (for error messages)
        max_length: Maximum allowed length
        
    Returns:
        Validated and sanitized text
        
    Raises:
        GmailValidationError: If validation fails
    """
    if not isinstance(text, str):
        raise GmailValidationError(f"{field_name} must be a string")
    
    if len(text) > max_length:
        raise GmailValidationError(f"{field_name} exceeds maximum length of {max_length} characters")
    
    # Remove null bytes and control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
    
    return text.strip()


class ErikaGmailService:
    """
    Service for Gmail OAuth integration
    
    This service provides secure Gmail API integration with:
    - OAuth2 authentication
    - HTML sanitization
    - Input validation
    - Secure token management
    """
    
    # Maximum field lengths for validation
    MAX_SUBJECT_LENGTH = 500
    MAX_BODY_LENGTH = 100000
    MAX_SENDER_LENGTH = 255
    
    def __init__(self, user_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Gmail service
        
        Args:
            user_id: User identifier (string or int)
            config: Optional configuration dict with:
                - gmail_client_id: OAuth2 client ID
                - gmail_client_secret: OAuth2 client secret
                - gmail_keywords: List of keywords for filtering (optional)
        """
        self.user_id = user_id or "default"
        self.config = config or {}
        self.service = None
        self.token_manager = None
        
        # Initialize token manager
        from .oauth_token_manager import OAuthTokenManager
        self.token_manager = OAuthTokenManager(user_id=self.user_id)
    
    def authenticate(self, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> bool:
        """
        Authenticate with Gmail API using OAuth2
        
        Args:
            client_id: OAuth2 client ID (optional, can use config values)
            client_secret: OAuth2 client secret (optional, can use config values)
            
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            GmailAuthenticationError: If authentication fails
        """
        try:
            # Import Gmail API libraries
            from googleapiclient.discovery import build
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            
            # Use provided credentials or config values
            client_id = client_id or self.config.get('gmail_client_id')
            client_secret = client_secret or self.config.get('gmail_client_secret')
            
            if not client_id or not client_secret:
                raise GmailAuthenticationError("OAuth2 client_id and client_secret are required")
            
            # Define Gmail scopes
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/gmail.labels'
            ]
            
            # Try to load existing token
            creds = self.token_manager.load_token()
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info(f"[AUTH] Refreshing expired token for user {self.user_id}...")
                    try:
                        creds.refresh(Request())
                        self.token_manager.save_token(creds)
                    except Exception as e:
                        logger.warning(f"Token refresh failed: {e}, initiating new OAuth flow")
                        creds = None
                
                if not creds:
                    logger.info(f"[AUTH] Initiating OAuth2 flow for user {self.user_id}...")
                    # Create credentials config
                    client_config = {
                        "installed": {
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["http://localhost"]
                        }
                    }
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                    creds = flow.run_local_server(port=0)
                    self.token_manager.save_token(creds)
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info(f"Gmail service authenticated successfully for user {self.user_id}")
            return True
            
        except ImportError as e:
            logger.error(f"Google API client not installed: {e}")
            raise GmailAuthenticationError(f"Google API client libraries not installed: {e}")
        except GmailAuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Gmail authentication failed for user {self.user_id}: {e}")
            raise GmailAuthenticationError(f"Authentication failed: {e}")
    
    def get_unread_emails(self, max_results: int = 50, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Get unread emails from the last N days
        
        Args:
            max_results: Maximum number of emails to retrieve (default: 50, max: 500)
            days_back: How many days back to search (default: 7, max: 30)
            
        Returns:
            List of email dictionaries with sanitized content
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            # Validate parameters
            max_results = min(max(1, max_results), 500)  # Clamp between 1 and 500
            days_back = min(max(1, days_back), 30)  # Clamp between 1 and 30
            
            # Build search query
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            
            # Search for unread emails
            query_parts = ['is:unread', f'after:{date_filter}']
            
            # Add keyword filters from config (if provided)
            keywords = self.config.get('gmail_keywords', [])
            if keywords and isinstance(keywords, list):
                # Sanitize keywords to prevent injection
                sanitized_keywords = []
                for keyword in keywords[:10]:  # Limit to 10 keywords
                    if isinstance(keyword, str) and len(keyword) <= 100:
                        sanitized_keywords.append(keyword.strip())
                if sanitized_keywords:
                    keyword_query = ' OR '.join([f'"{kw}"' for kw in sanitized_keywords])
                    query_parts.append(f'({keyword_query})')
            
            query = ' '.join(query_parts)
            
            logger.info(f"🔍 Searching Gmail with query: {query}")
            
            # Call Gmail API
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("📭 No unread emails found")
                return []
            
            logger.info(f"📬 Found {len(messages)} unread emails")
            
            # Get full message details with sanitization
            emails = []
            for msg in messages:
                try:
                    email_data = self._get_email_details(msg['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    logger.warning(f"Error processing email {msg.get('id', 'unknown')}: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            logger.error(f"❌ Error fetching emails: {e}", exc_info=True)
            return []
    
    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific email with sanitization
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dictionary with sanitized email details, or None if error
        """
        try:
            if not message_id or not isinstance(message_id, str):
                raise GmailValidationError("Invalid message_id")
            
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message.get('payload', {}).get('headers', [])
            subject = self._get_header(headers, 'Subject')
            sender = self._get_header(headers, 'From')
            date_str = self._get_header(headers, 'Date')
            
            # Extract and sanitize body
            body = self._get_email_body(message.get('payload', {}))
            
            # Validate and sanitize all fields
            try:
                subject = _validate_text_field(subject, "subject", self.MAX_SUBJECT_LENGTH)
                sender = _validate_text_field(sender, "sender", self.MAX_SENDER_LENGTH)
                body = _validate_text_field(body, "body", self.MAX_BODY_LENGTH)
            except GmailValidationError as e:
                logger.warning(f"Validation error for email {message_id}: {e}")
                # Use safe defaults
                subject = subject[:self.MAX_SUBJECT_LENGTH] if subject else ""
                sender = sender[:self.MAX_SENDER_LENGTH] if sender else ""
                body = body[:self.MAX_BODY_LENGTH] if body else ""
            
            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'subject': subject,
                'sender': sender,
                'date': date_str,
                'body': body,
                'raw_message': message  # Keep raw for advanced use cases, but don't expose directly
            }
            
            # Automatic phishing detection (if enabled)
            phishing_enabled = self.config.get('phishing_detection_enabled', True)
            if phishing_enabled:
                try:
                    phishing_result = self._check_phishing(email_data, message)
                    if phishing_result:
                        email_data['phishing_analysis'] = phishing_result
                        email_data['is_phishing'] = phishing_result.get('is_phishing', False)
                        email_data['phishing_risk_score'] = phishing_result.get('risk_score', 0.0)
                except Exception as e:
                    logger.debug(f"Phishing detection error (non-fatal): {e}")
                    # Don't fail email processing if phishing check fails
            
            # AresBridge threat scoring and mitigation (if enabled)
            ares_enabled = self.config.get('enable_ares_bridge', False)
            if ares_enabled:
                try:
                    threat_analysis = self._analyze_threat(email_data, message)
                    if threat_analysis:
                        email_data['threat_analysis'] = threat_analysis
                        email_data['threat_score'] = threat_analysis.get('threat_score', 0.0)
                        
                        # Auto-mitigate if high threat and auto-mitigation enabled
                        auto_mitigate = self.config.get('auto_mitigate_threats', False)
                        if auto_mitigate and threat_analysis.get('threat_score', 0.0) >= 0.8:
                            mitigation_result = self._apply_mitigation(
                                message_id,
                                threat_analysis.get('mitigation_action_recommended', 'NONE')
                            )
                            email_data['mitigation_applied'] = mitigation_result
                except Exception as e:
                    logger.warning(f"AresBridge error (non-fatal): {e}")
                    # Don't fail email processing if threat analysis fails
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error getting email details for message {message_id}: {e}")
            return None
    
    def _get_header(self, headers: List[Dict[str, str]], name: str) -> str:
        """Extract header value by name"""
        if not headers or not isinstance(headers, list):
            return ""
        
        for header in headers:
            if isinstance(header, dict) and header.get('name', '').lower() == name.lower():
                value = header.get('value', '')
                if isinstance(value, str):
                    return value
        return ""
    
    def _get_email_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract email body from payload with secure base64 decoding
        
        Args:
            payload: Gmail API payload
            
        Returns:
            Sanitized email body text
        """
        body = ""
        
        try:
            if 'parts' in payload and isinstance(payload['parts'], list):
                for part in payload['parts']:
                    if not isinstance(part, dict):
                        continue
                    
                    mime_type = part.get('mimeType', '')
                    body_data = part.get('body', {}).get('data')
                    
                    if mime_type == 'text/plain' and body_data:
                        try:
                            decoded = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                            body += decoded
                        except (ValueError, UnicodeDecodeError) as e:
                            logger.warning(f"Error decoding text/plain part: {e}")
                            continue
                    elif mime_type == 'text/html' and not body:
                        # Prefer plain text, but use HTML if no plain text available
                        if body_data:
                            try:
                                decoded = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                                # Sanitize HTML content
                                body = _sanitize_html(decoded)
                            except (ValueError, UnicodeDecodeError) as e:
                                logger.warning(f"Error decoding text/html part: {e}")
                                continue
            else:
                # Single part message
                mime_type = payload.get('mimeType', '')
                body_data = payload.get('body', {}).get('data')
                
                if mime_type == 'text/plain' and body_data:
                    try:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                    except (ValueError, UnicodeDecodeError) as e:
                        logger.warning(f"Error decoding text/plain: {e}")
                        body = ""
                elif mime_type == 'text/html' and body_data:
                    try:
                        decoded = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                        body = _sanitize_html(decoded)
                    except (ValueError, UnicodeDecodeError) as e:
                        logger.warning(f"Error decoding text/html: {e}")
                        body = ""
        except Exception as e:
            logger.error(f"Error extracting email body: {e}")
            body = ""
        
        return body
    
    def _check_phishing(self, email_data: Dict[str, Any], raw_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check email for phishing using reverse image search (if enabled)
        
        Args:
            email_data: Processed email data
            raw_message: Raw Gmail API message (for image extraction)
            
        Returns:
            Phishing analysis dictionary or None if disabled/error
        """
        try:
            # Check if phishing detection is enabled
            phishing_enabled = self.config.get('phishing_detection_enabled', True)
            if not phishing_enabled:
                return None
            
            # Check if reverse image search is available
            reverse_search_enabled = self.config.get('reverse_image_search_enabled', True)
            if not reverse_search_enabled:
                return None
            
            # Import phishing detector
            try:
                from ..services.phishing_detector import PhishingDetector
            except ImportError:
                logger.debug("Phishing detector not available")
                return None
            
            # Perform analysis
            detector = PhishingDetector()
            analysis = detector.analyze_email(
                email_data=email_data,
                email_message=raw_message
            )
            
            return analysis
            
        except Exception as e:
            logger.debug(f"Phishing check error (non-fatal): {e}")
            return None
    
    def send_email(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> bool:
        """
        Send email via Gmail API with input validation
        
        Args:
            to: Recipient email address (validated)
            subject: Email subject (validated, max 500 chars)
            body: Email body (validated, max 100000 chars)
            thread_id: Optional thread ID for replies
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            GmailValidationError: If input validation fails
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            # Validate inputs
            if not _validate_email_address(to):
                raise GmailValidationError(f"Invalid recipient email address: {to}")
            
            subject = _validate_text_field(subject, "subject", self.MAX_SUBJECT_LENGTH)
            body = _validate_text_field(body, "body", self.MAX_BODY_LENGTH)
            
            # Create message
            message = MIMEText(body, 'plain', 'utf-8')
            message['to'] = to
            message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            send_params = {
                'userId': 'me',
                'body': {'raw': raw_message}
            }
            
            if thread_id:
                if not isinstance(thread_id, str) or len(thread_id) > 200:
                    raise GmailValidationError("Invalid thread_id")
                send_params['body']['threadId'] = thread_id
            
            result = self.service.users().messages().send(**send_params).execute()
            
            logger.info(f"✅ Email sent successfully: {result.get('id')}")
            return True
            
        except GmailValidationError:
            raise
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def create_draft(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> bool:
        """
        Create email draft via Gmail API with input validation
        
        Args:
            to: Recipient email address (validated)
            subject: Email subject (validated, max 500 chars)
            body: Email body (validated, max 100000 chars)
            thread_id: Optional thread ID for replies
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            GmailValidationError: If input validation fails
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            # Validate inputs
            if not _validate_email_address(to):
                raise GmailValidationError(f"Invalid recipient email address: {to}")
            
            subject = _validate_text_field(subject, "subject", self.MAX_SUBJECT_LENGTH)
            body = _validate_text_field(body, "body", self.MAX_BODY_LENGTH)
            
            # Create message
            message = MIMEText(body, 'plain', 'utf-8')
            message['to'] = to
            message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Create draft
            draft_params = {
                'userId': 'me',
                'body': {
                    'message': {'raw': raw_message}
                }
            }
            
            if thread_id:
                if not isinstance(thread_id, str) or len(thread_id) > 200:
                    raise GmailValidationError("Invalid thread_id")
                draft_params['body']['message']['threadId'] = thread_id
            
            result = self.service.users().drafts().create(**draft_params).execute()
            
            logger.info(f"✅ Draft created successfully: {result.get('id')}")
            return True
            
        except GmailValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creating draft: {e}")
            return False


def get_gmail_service_for_user(user_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> ErikaGmailService:
    """
    Get Gmail service instance for a specific user
    
    Args:
        user_id: User identifier (string or int)
        config: Optional configuration dict
        
    Returns:
        ErikaGmailService instance
    """
    return ErikaGmailService(user_id=user_id, config=config)

