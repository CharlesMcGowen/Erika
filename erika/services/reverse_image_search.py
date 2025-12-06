#!/usr/bin/env python3
"""
Reverse Image Search Service for Erika
======================================

Uses Google reverse image search to verify profile photos in emails
and detect phishing/fraud attempts.

Author: EGO Revolution Team
Version: 1.0.0
"""

import logging
import base64
import requests
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import re
import time

logger = logging.getLogger(__name__)


class ReverseImageSearchError(Exception):
    """Base exception for reverse image search errors"""
    pass


class ReverseImageSearchService:
    """
    Service for performing reverse image searches to verify email sender identities.
    
    Detects phishing by comparing claimed identity with actual online presence.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize reverse image search service
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    def search_image(self, image_data: bytes, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform reverse image search on Google
        
        Args:
            image_data: Image file bytes
            image_url: Optional URL of the image (if from email)
            
        Returns:
            Dictionary with:
                - matches: List of match results
                - domains: List of domains where image appears
                - identities: List of claimed identities
                - risk_score: Risk score (0.0-1.0)
                - analysis: Analysis text
        """
        try:
            # Upload image to Google and get search results
            results = self._perform_google_search(image_data)
            
            # Analyze results
            analysis = self._analyze_results(results)
            
            return {
                'matches': results.get('matches', []),
                'domains': analysis['domains'],
                'identities': analysis['identities'],
                'risk_score': analysis['risk_score'],
                'analysis': analysis['text'],
                'suspicious_patterns': analysis['suspicious_patterns']
            }
            
        except Exception as e:
            logger.error(f"Error in reverse image search: {e}")
            return {
                'matches': [],
                'domains': [],
                'identities': [],
                'risk_score': 0.5,  # Unknown risk
                'analysis': f"Error performing search: {str(e)}",
                'suspicious_patterns': []
            }
    
    def _perform_google_search(self, image_data: bytes) -> Dict[str, Any]:
        """
        Perform Google reverse image search using Google Lens
        
        Args:
            image_data: Image file bytes
            
        Returns:
            Dictionary with search results
        """
        try:
            # Try to use Google Lens search
            try:
                from .google_lens_search import GoogleLensSearch
                lens_search = GoogleLensSearch(headless=True)
                results = lens_search.search_image(image_data)
                return results
            except ImportError:
                logger.warning("Selenium not available - reverse image search disabled")
                logger.warning("Install with: pip install selenium webdriver-manager")
                return {'matches': [], 'search_url': None}
            except Exception as e:
                logger.error(f"Error in Google Lens search: {e}")
                return {'matches': [], 'search_url': None}
            
        except Exception as e:
            logger.error(f"Error performing Google search: {e}")
            raise ReverseImageSearchError(f"Search failed: {e}")
    
    def _analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze search results to detect suspicious patterns
        
        Args:
            results: Search results from Google
            
        Returns:
            Analysis dictionary with:
                - domains: List of domains
                - identities: List of claimed identities
                - risk_score: Risk score
                - text: Analysis text
                - suspicious_patterns: List of suspicious patterns found
        """
        matches = results.get('matches', [])
        domains = set()
        identities = []
        suspicious_patterns = []
        
        # Extract domains and identities from matches
        for match in matches:
            domain = match.get('domain', '')
            if domain:
                domains.add(domain)
            
            title = match.get('title', '')
            if title:
                # Try to extract identity from title
                identity = self._extract_identity(title, match.get('context', ''))
                if identity:
                    identities.append(identity)
        
        # Analyze for suspicious patterns
        risk_score = 0.0
        
        # Pattern 1: Image used across multiple unrelated domains
        if len(domains) > 3:
            suspicious_patterns.append({
                'type': 'multiple_domains',
                'severity': 'medium',
                'description': f'Image appears on {len(domains)} different domains',
                'domains': list(domains)
            })
            risk_score += 0.2
        
        # Pattern 2: Identity mismatch (e.g., claimed recruiter but image shows real estate agent)
        identity_types = self._categorize_identities(identities)
        if len(identity_types) > 1:
            suspicious_patterns.append({
                'type': 'identity_mismatch',
                'severity': 'high',
                'description': f'Image associated with multiple different roles: {", ".join(identity_types)}',
                'identities': identities
            })
            risk_score += 0.4
        
        # Pattern 3: Image on Facebook with different name
        facebook_matches = [m for m in matches if 'facebook' in m.get('domain', '').lower()]
        if facebook_matches:
            for match in facebook_matches:
                title = match.get('title', '').lower()
                # Check if name in title differs from claimed name
                # This would be compared with email sender name
                suspicious_patterns.append({
                    'type': 'facebook_mismatch',
                    'severity': 'high',
                    'description': 'Image found on Facebook with potentially different identity',
                    'match': match
                })
                risk_score += 0.3
        
        # Pattern 4: Image used by law firms, real estate, etc. (common in phishing)
        suspicious_domains = ['law', 'real estate', 'attorney', 'lawyer', 'realtor']
        for domain in domains:
            domain_lower = domain.lower()
            for suspicious in suspicious_domains:
                if suspicious in domain_lower:
                    suspicious_patterns.append({
                        'type': 'suspicious_domain',
                        'severity': 'medium',
                        'description': f'Image found on {domain} (common in phishing)',
                        'domain': domain
                    })
                    risk_score += 0.2
                    break
        
        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Generate analysis text
        analysis_text = self._generate_analysis_text(
            domains, identities, suspicious_patterns, risk_score
        )
        
        return {
            'domains': list(domains),
            'identities': identities,
            'risk_score': risk_score,
            'text': analysis_text,
            'suspicious_patterns': suspicious_patterns
        }
    
    def _extract_identity(self, title: str, context: str = '') -> Optional[Dict[str, Any]]:
        """
        Extract identity information from search result title/context
        
        Args:
            title: Title of search result
            context: Additional context
            
        Returns:
            Identity dictionary or None
        """
        text = f"{title} {context}".lower()
        
        # Try to extract name
        # Common patterns: "John Doe - Title", "John Doe at Company", etc.
        name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', title)
        if not name_match:
            # Try single name
            name_match = re.search(r'([A-Z][a-z]+)', title)
        
        name = name_match.group(1) if name_match else None
        
        # Try to extract role/company
        role = None
        company = None
        
        # Common role patterns
        roles = ['recruiter', 'headhunter', 'real estate', 'realtor', 'attorney', 
                 'lawyer', 'agent', 'director', 'manager', 'executive']
        for r in roles:
            if r in text:
                role = r
                break
        
        # Try to extract company
        # Look for patterns like "at Company", "Company -", etc.
        company_match = re.search(r'(?:at|from|of|with)\s+([A-Z][a-zA-Z\s&]+)', text)
        if company_match:
            company = company_match.group(1).strip()
        
        if name or role or company:
            return {
                'name': name,
                'role': role,
                'company': company,
                'source': title
            }
        
        return None
    
    def _categorize_identities(self, identities: List[Dict[str, Any]]) -> List[str]:
        """
        Categorize identities by type
        
        Args:
            identities: List of identity dictionaries
            
        Returns:
            List of identity categories
        """
        categories = set()
        
        for identity in identities:
            role = identity.get('role', '').lower()
            if 'recruiter' in role or 'headhunter' in role:
                categories.add('recruiter')
            elif 'real estate' in role or 'realtor' in role:
                categories.add('real_estate')
            elif 'attorney' in role or 'lawyer' in role or 'law' in role:
                categories.add('legal')
            elif 'director' in role or 'manager' in role:
                categories.add('corporate')
            else:
                categories.add('other')
        
        return list(categories)
    
    def _generate_analysis_text(self, domains: List[str], identities: List[Dict[str, Any]], 
                                suspicious_patterns: List[Dict[str, Any]], 
                                risk_score: float) -> str:
        """
        Generate human-readable analysis text
        
        Args:
            domains: List of domains
            identities: List of identities
            suspicious_patterns: List of suspicious patterns
            risk_score: Risk score
            
        Returns:
            Analysis text
        """
        lines = []
        
        if risk_score >= 0.7:
            lines.append("🚨 HIGH RISK: Profile photo shows suspicious patterns")
        elif risk_score >= 0.4:
            lines.append("⚠️  MEDIUM RISK: Profile photo shows some inconsistencies")
        else:
            lines.append("✅ LOW RISK: Profile photo appears consistent")
        
        if domains:
            lines.append(f"\nImage found on {len(domains)} domain(s):")
            for domain in domains[:5]:  # Show first 5
                lines.append(f"  - {domain}")
            if len(domains) > 5:
                lines.append(f"  ... and {len(domains) - 5} more")
        
        if identities:
            lines.append(f"\nAssociated identities found:")
            for identity in identities[:3]:  # Show first 3
                name = identity.get('name', 'Unknown')
                role = identity.get('role', '')
                company = identity.get('company', '')
                parts = [p for p in [name, role, company] if p]
                lines.append(f"  - {' - '.join(parts)}")
        
        if suspicious_patterns:
            lines.append(f"\n⚠️  Suspicious patterns detected:")
            for pattern in suspicious_patterns:
                lines.append(f"  - {pattern['description']}")
        
        return "\n".join(lines)
    
    def verify_email_sender(self, email_data: Dict[str, Any], 
                           image_data: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Verify email sender by comparing claimed identity with image search results
        
        Args:
            email_data: Email data with sender information
            image_data: Optional image bytes from email
            
        Returns:
            Verification result with:
                - verified: bool
                - risk_score: float
                - analysis: str
                - recommendations: List[str]
        """
        claimed_name = email_data.get('sender', '').split('<')[0].strip()
        claimed_role = email_data.get('subject', '')  # Could extract from email body
        
        if not image_data:
            return {
                'verified': False,
                'risk_score': 0.5,
                'analysis': 'No profile image found in email',
                'recommendations': ['Email contains no profile image to verify']
            }
        
        # Perform reverse image search
        search_results = self.search_image(image_data)
        
        # Compare claimed identity with search results
        risk_score = search_results['risk_score']
        identities = search_results['identities']
        
        # Check for name mismatch
        name_mismatch = False
        if claimed_name and identities:
            claimed_name_lower = claimed_name.lower()
            for identity in identities:
                identity_name = identity.get('name', '').lower()
                if identity_name and identity_name not in claimed_name_lower and claimed_name_lower not in identity_name:
                    name_mismatch = True
                    risk_score = min(risk_score + 0.2, 1.0)
                    break
        
        # Generate recommendations
        recommendations = []
        if risk_score >= 0.7:
            recommendations.append("🚨 HIGH RISK: Do not respond to this email")
            recommendations.append("Report as phishing/spam")
            recommendations.append("Block sender")
        elif risk_score >= 0.4:
            recommendations.append("⚠️  Verify sender identity through other channels")
            recommendations.append("Be cautious with any requests")
        else:
            recommendations.append("✅ Profile photo appears legitimate")
        
        verified = risk_score < 0.4
        
        return {
            'verified': verified,
            'risk_score': risk_score,
            'analysis': search_results['analysis'],
            'recommendations': recommendations,
            'search_results': search_results
        }

