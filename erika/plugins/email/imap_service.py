#!/usr/bin/env python3
"""
IMAP Email Service
==================

IMAP protocol support for generic email providers (Yahoo, iCloud, custom servers, etc.)

Author: Living Archive team
Version: 1.0.0
"""

import logging
import imaplib
import email
import email.header
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from email.mime.text import MIMEText
import re

from .base_email_service import (
    BaseEmailService,
    EmailServiceError,
    EmailAuthenticationError,
    EmailValidationError
)

logger = logging.getLogger(__name__)


class IMAPService(BaseEmailService):
    """
    IMAP email service for generic email providers.
    
    Supports any email server with IMAP access:
    - Yahoo Mail
    - iCloud Mail
    - Custom IMAP servers
    - Most email providers
    """
    
    def __init__(self, user_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize IMAP service
        
        Args:
            user_id: User identifier
            config: Configuration dictionary with:
                - imap_server: IMAP server address (e.g., 'imap.gmail.com')
                - imap_port: IMAP port (default: 993 for SSL)
                - imap_username: Email username
                - imap_password: Email password or app password
                - use_ssl: Use SSL/TLS (default: True)
                - use_oauth: Use OAuth2 (if supported by provider)
        """
        super().__init__(user_id, config)
        self.imap_server = self.config.get('imap_server')
        self.imap_port = self.config.get('imap_port', 993)
        self.imap_username = self.config.get('imap_username')
        self.imap_password = self.config.get('imap_password')
        self.use_ssl = self.config.get('use_ssl', True)
        self.connection = None
    
    def authenticate(self, **kwargs) -> bool:
        """
        Authenticate with IMAP server
        
        Args:
            username: Optional username override
            password: Optional password override
            
        Returns:
            True if authentication successful
            
        Raises:
            EmailAuthenticationError: If authentication fails
        """
        username = kwargs.get('username') or self.imap_username
        password = kwargs.get('password') or self.imap_password
        
        if not username or not password:
            raise EmailAuthenticationError("IMAP username and password are required")
        
        if not self.imap_server:
            raise EmailAuthenticationError("IMAP server address is required")
        
        try:
            # Connect to IMAP server
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                self.connection = imaplib.IMAP4(self.imap_server, self.imap_port)
            
            # Authenticate
            self.connection.login(username, password)
            self._authenticated = True
            logger.info(f"✅ IMAP authentication successful: {self.imap_server}")
            return True
            
        except imaplib.IMAP4.error as e:
            self._authenticated = False
            error_msg = f"IMAP authentication failed: {str(e)}"
            logger.error(error_msg)
            raise EmailAuthenticationError(error_msg)
        except Exception as e:
            self._authenticated = False
            error_msg = f"IMAP connection error: {str(e)}"
            logger.error(error_msg)
            raise EmailAuthenticationError(error_msg)
    
    def get_unread_emails(
        self,
        max_results: int = 50,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get unread emails via IMAP
        
        Args:
            max_results: Maximum number of emails to retrieve
            days_back: Number of days to look back
            
        Returns:
            List of email dictionaries
        """
        if not self._authenticated or not self.connection:
            if not self.authenticate():
                return []
        
        try:
            # Select INBOX
            self.connection.select('INBOX')
            
            # Build search query for unread emails
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%d-%b-%Y')
            search_query = f'(UNSEEN SINCE {date_filter})'
            
            # Search for unread emails
            status, message_ids = self.connection.search(None, search_query)
            
            if status != 'OK' or not message_ids[0]:
                logger.info("📭 No unread emails found")
                return []
            
            # Get message IDs
            msg_ids = message_ids[0].split()
            msg_ids = msg_ids[:max_results]  # Limit results
            
            emails = []
            for msg_id in msg_ids:
                try:
                    # Fetch email
                    status, msg_data = self.connection.fetch(msg_id, '(RFC822)')
                    
                    if status != 'OK' or not msg_data[0]:
                        continue
                    
                    # Parse email
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract headers
                    subject = self._decode_header(email_message.get('Subject', ''))
                    sender = self._decode_header(email_message.get('From', ''))
                    date_str = email_message.get('Date', '')
                    
                    # Extract body
                    body = self._extract_body(email_message)
                    
                    # Create email dict
                    email_dict = {
                        'id': msg_id.decode('utf-8'),
                        'thread_id': None,  # IMAP doesn't have thread IDs
                        'subject': subject or 'No subject',
                        'sender': sender or 'Unknown',
                        'date': date_str,
                        'body': body,
                        'provider': 'imap'
                    }
                    
                    emails.append(email_dict)
                    
                except Exception as e:
                    logger.warning(f"Error processing email {msg_id}: {e}")
                    continue
            
            logger.info(f"📬 Found {len(emails)} unread emails via IMAP")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails via IMAP: {e}")
            return []
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP (IMAP is read-only, need SMTP for sending)
        
        Note: IMAP is read-only. Sending requires SMTP configuration.
        This is a placeholder - actual implementation would need SMTP server config.
        """
        logger.warning("IMAP service is read-only. Use SMTP service for sending emails.")
        return False
    
    def _decode_header(self, header: str) -> str:
        """Decode email header (handles encoded words)"""
        if not header:
            return ""
        
        try:
            decoded_parts = email.header.decode_header(header)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            return decoded_string
        except Exception as e:
            logger.debug(f"Error decoding header: {e}")
            return str(header)
    
    def _extract_body(self, email_message: email.message.Message) -> str:
        """Extract email body from message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get text content
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
                elif content_type == "text/html":
                    try:
                        html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Basic HTML to text conversion
                        body = re.sub(r'<[^>]+>', '', html_body)
                        break
                    except:
                        pass
        else:
            # Single part message
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())
        
        return body.strip()
    
    def __del__(self):
        """Cleanup IMAP connection"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except:
                pass
