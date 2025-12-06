#!/usr/bin/env python3
"""
Ares Bridge - Threat Detection and Mitigation Service
======================================================

Bridge service for the Ares Threat Detection system.
Handles risk scoring and client-side mitigation requests.

Features:
- Threat score calculation (0.0-1.0)
- Multi-factor risk analysis (footprint, domain mismatch, content)
- Gmail API mitigation (mark as spam/phishing)
- Automatic label management

Author: EGO Revolution Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, List
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class AresBridge:
    """
    Bridge service for the Ares Threat Detection system.
    
    Handles risk scoring and client-side mitigation requests.
    """
    
    def __init__(self, client_config: Dict[str, Any] = None):
        """
        Initialize Ares Bridge
        
        Args:
            client_config: Optional configuration dictionary
        """
        self.client_config = client_config or {}
        logger.info("Ares Bridge initialized")
    
    def calculate_threat_score(
        self,
        email_analysis: Dict[str, Any],
        footprint_data: Dict[str, Any],
        content_risk_score: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates a normalized threat score (0.0-1.0) and returns a breakdown.
        
        Args:
            email_analysis: Email data dictionary with:
                - id: Email ID
                - sender: Sender email/name
                - subject: Email subject
                - body: Email body
            footprint_data: Domain footprint data with:
                - source_count: Number of sources found
                - age_days: Domain age in days
                - domain: Domain name
            content_risk_score: LLM-determined content risk (0.0-1.0)
        
        Returns:
            {
                'threat_score': float,  # 0.0-1.0
                'scoring_breakdown': {
                    'footprint_risk': float,  # Max 0.40
                    'domain_mismatch_risk': float,  # Max 0.30
                    'content_risk': float  # Max 0.30
                },
                'mitigation_action_recommended': str  # 'NONE', 'FLAG', 'MARK_AS_PHISHING'
            }
        """
        try:
            logger.info(f"🛡️ Calculating threat score for email: {email_analysis.get('id', 'unknown')}")
            
            # Initialize breakdown
            breakdown = {
                'footprint_risk': 0.0,
                'domain_mismatch_risk': 0.0,
                'content_risk': 0.0
            }
            
            # --- SCORING LOGIC IMPLEMENTATION (Threat Fusion) ---
            
            # 1. FOOTPRINT (40% weight)
            source_count = footprint_data.get('source_count', 0)
            age_days = footprint_data.get('age_days', 999)
            
            # Full 40% applied if footprint is extremely low/new
            if source_count == 0 and age_days < 90:
                breakdown['footprint_risk'] = 0.40
            elif source_count < 3 and age_days < 180:
                # Partial risk for low footprint
                breakdown['footprint_risk'] = 0.20
            elif source_count < 10:
                # Minimal risk
                breakdown['footprint_risk'] = 0.10
            
            # 2. DOMAIN MISMATCH (30% weight)
            # Check if sender claims a role/company that doesn't match the actual domain
            # e.g., recruiter using @gmail.com instead of company domain
            domain_mismatch = self._detect_domain_mismatch(
                email_analysis.get('sender', ''),
                email_analysis.get('body', '')
            )
            
            if domain_mismatch:
                breakdown['domain_mismatch_risk'] = 0.30
            
            # 3. CONTENT (30% weight)
            # Content risk is typically a partial score of the 30% bucket
            # Clamp content_risk_score to 0.0-1.0
            content_risk_score = max(0.0, min(1.0, content_risk_score))
            weighted_content_risk = content_risk_score * 0.30
            breakdown['content_risk'] = min(weighted_content_risk, 0.30)
            
            # Calculate final score
            final_score = sum(breakdown.values())
            final_score = min(final_score, 1.0)  # Cap at 1.0
            
            # Determine mitigation action based on Score Range
            if final_score >= 0.8:
                mitigation_action = 'MARK_AS_PHISHING'
            elif final_score >= 0.5:
                mitigation_action = 'FLAG'
            else:
                mitigation_action = 'NONE'
            
            logger.info(f"Threat Score calculated: {final_score:.2f}, Action: {mitigation_action}")
            
            return {
                'threat_score': final_score,
                'scoring_breakdown': breakdown,
                'mitigation_action_recommended': mitigation_action
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating threat score: {e}")
            # Return a default moderate risk on internal error
            return {
                'threat_score': 0.50,
                'scoring_breakdown': {
                    'footprint_risk': 0.0,
                    'domain_mismatch_risk': 0.0,
                    'content_risk': 0.0
                },
                'mitigation_action_recommended': 'FLAG'
            }
    
    def _detect_domain_mismatch(self, sender: str, body: str) -> bool:
        """
        Detect if sender claims a professional role but uses personal email domain
        
        Args:
            sender: Sender email address
            body: Email body text
        
        Returns:
            True if domain mismatch detected, False otherwise
        """
        try:
            import re
            
            # Extract domain from sender
            email_match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', sender)
            if not email_match:
                return False
            
            domain = email_match.group(1).lower()
            
            # Personal email domains
            personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                              'icloud.com', 'protonmail.com', 'aol.com']
            
            if domain not in personal_domains:
                return False  # Corporate domain, no mismatch
            
            # Check if body claims professional role
            professional_keywords = [
                r'recruiter', r'hiring manager', r'hr department', r'human resources',
                r'company', r'corporation', r'inc\.', r'llc', r'ltd',
                r'financial advisor', r'bank', r'investment', r'legal counsel',
                r'attorney', r'law firm', r'accountant', r'cpa'
            ]
            
            body_lower = body.lower()
            for keyword in professional_keywords:
                if re.search(keyword, body_lower):
                    return True  # Mismatch: professional claim with personal domain
            
            return False
            
        except Exception as e:
            logger.debug(f"Error detecting domain mismatch: {e}")
            return False
    
    def request_client_mitigation(
        self,
        email_client_id: str,
        mitigation_action: str,
        creds: Credentials
    ) -> Dict[str, Any]:
        """
        Requests Gmail API modification (e.g., mark as spam/phishing) using user credentials.
        
        Args:
            email_client_id: Gmail message ID
            mitigation_action: Action to take ('MARK_AS_PHISHING', 'MARK_AS_SPAM', 'MARK_AS_READ')
            creds: Google OAuth2 Credentials object
        
        Returns:
            Structured status object with:
                - status: 'SUCCESS' or 'FAILURE'
                - message_id: Email ID
                - action: Mitigation action attempted
                - labels_applied: List of labels added
                - labels_removed: List of labels removed
                - error: Error message if failed
                - error_code: Error code if failed
        """
        
        # Determine Gmail labels based on the requested action
        add_labels: List[str] = []
        remove_labels: List[str] = []
        
        if mitigation_action == 'MARK_AS_PHISHING':
            add_labels = ['SPAM', 'PHISHING_DETECTED_BY_ERIKA']
            remove_labels = ['INBOX']
        elif mitigation_action == 'MARK_AS_SPAM':
            add_labels = ['SPAM']
            remove_labels = ['INBOX']
        elif mitigation_action == 'MARK_AS_READ':
            remove_labels = ['UNREAD']
        else:
            logger.warning(f"Mitigation action '{mitigation_action}' not supported by bridge.")
            return {
                'status': 'FAILURE',
                'message_id': email_client_id,
                'action': mitigation_action,
                'error': f"Unknown mitigation action: {mitigation_action}",
                'error_code': 'UNSUPPORTED_ACTION',
                'labels_applied': [],
                'labels_removed': []
            }
        
        try:
            # Check for the required 'gmail.modify' scope
            if 'https://www.googleapis.com/auth/gmail.modify' not in creds.scopes:
                raise PermissionError("Missing 'gmail.modify' scope for mitigation action.")
            
            # Build the Gmail service client
            service = build('gmail', 'v1', credentials=creds)
            
            # Apply mitigation labels
            if add_labels or remove_labels:
                modify_request = {
                    'addLabelIds': add_labels,
                    'removeLabelIds': remove_labels
                }
                
                # Executes the modification on the Gmail message
                result = service.users().messages().modify(
                    userId='me',
                    id=email_client_id,
                    body=modify_request
                ).execute()
                
                logger.info(f"✅ Mitigation SUCCESS: Applied {add_labels}, Removed {remove_labels}")
            
            return {
                'status': 'SUCCESS',
                'message_id': email_client_id,
                'action': mitigation_action,
                'labels_applied': add_labels,
                'labels_removed': remove_labels,
                'error': None,
                'error_code': None
            }
            
        except PermissionError as pe:
            # Handle specific scope error
            error_code = 'INSUFFICIENT_SCOPE'
            error_msg = str(pe)
        except Exception as e:
            # Catch all API and network errors
            error_str = str(e).lower()
            
            # Detect specific error types
            error_code = None
            if '403' in error_str or 'insufficient' in error_str or 'scope' in error_str:
                error_code = 'INSUFFICIENT_SCOPE'
            elif '401' in error_str or 'unauthorized' in error_str:
                error_code = 'UNAUTHORIZED'  # Revocation/expired token that refresh couldn't handle
            elif '404' in error_str or 'not found' in error_str:
                error_code = 'MESSAGE_NOT_FOUND'
            else:
                error_code = 'UNKNOWN_API_ERROR'
            
            error_msg = str(e)
            logger.error(f"❌ Mitigation failed: {error_code} - {error_msg}")
            
        return {
            'status': 'FAILURE',
            'message_id': email_client_id,
            'action': mitigation_action,
            'error': error_msg,
            'error_code': error_code,
            'labels_applied': [],
            'labels_removed': []
        }

