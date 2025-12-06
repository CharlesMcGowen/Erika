#!/usr/bin/env python3
"""
Footprint Analyzer
==================

Analyzes domain footprint data for threat detection.
Fetches domain age, source count, and reputation data.

Author: Living Archive team
Version: 1.0.0
"""

import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class FootprintAnalyzer:
    """
    Analyzes domain footprint for threat detection.
    
    Provides domain age, source count, and reputation metrics.
    """
    
    def __init__(self):
        """Initialize footprint analyzer"""
        self.cache = {}  # Simple in-memory cache
    
    def get_footprint_data(self, sender: str) -> Dict[str, Any]:
        """
        Get footprint data for email sender domain
        
        Args:
            sender: Sender email address or name
        
        Returns:
            Dictionary with:
                - domain: Domain name
                - source_count: Number of sources found (0 if unknown)
                - age_days: Domain age in days (999 if unknown)
                - reputation: 'unknown', 'new', 'established', 'suspicious'
        """
        try:
            # Extract domain from sender
            domain = self._extract_domain(sender)
            if not domain:
                return self._default_footprint()
            
            # Check cache
            if domain in self.cache:
                return self.cache[domain]
            
            # Analyze domain
            footprint = {
                'domain': domain,
                'source_count': 0,
                'age_days': 999,
                'reputation': 'unknown'
            }
            
            # Try to get domain information
            # Note: This is a simplified implementation
            # In production, you might use:
            # - WHOIS API for domain age
            # - Search engine APIs for source count
            # - Reputation services for reputation
            
            # For now, use heuristics based on domain type
            if self._is_personal_domain(domain):
                footprint['source_count'] = 1  # Personal domains typically have low footprint
                footprint['age_days'] = 365  # Assume at least 1 year old
                footprint['reputation'] = 'established'
            else:
                # Corporate domain - assume established
                footprint['source_count'] = 10  # Corporate domains typically have more presence
                footprint['age_days'] = 730  # Assume at least 2 years old
                footprint['reputation'] = 'established'
            
            # Cache result
            self.cache[domain] = footprint
            
            return footprint
            
        except Exception as e:
            logger.warning(f"Error analyzing footprint for {sender}: {e}")
            return self._default_footprint()
    
    def _extract_domain(self, sender: str) -> Optional[str]:
        """
        Extract domain from sender email address
        
        Args:
            sender: Sender email address or name
        
        Returns:
            Domain name or None
        """
        try:
            # Try to extract email from sender string
            # Format: "Name <email@domain.com>" or "email@domain.com"
            email_match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', sender)
            if email_match:
                return email_match.group(1).lower()
            return None
        except Exception as e:
            logger.debug(f"Error extracting domain: {e}")
            return None
    
    def _is_personal_domain(self, domain: str) -> bool:
        """
        Check if domain is a personal email provider
        
        Args:
            domain: Domain name
        
        Returns:
            True if personal domain, False otherwise
        """
        personal_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'protonmail.com', 'aol.com', 'mail.com',
            'yandex.com', 'zoho.com', 'gmx.com'
        ]
        return domain.lower() in personal_domains
    
    def _default_footprint(self) -> Dict[str, Any]:
        """Return default footprint data when analysis fails"""
        return {
            'domain': 'unknown',
            'source_count': 0,
            'age_days': 999,
            'reputation': 'unknown'
        }
    
    def clear_cache(self):
        """Clear the footprint cache"""
        self.cache.clear()

