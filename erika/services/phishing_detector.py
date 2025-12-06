#!/usr/bin/env python3
"""
Phishing Detector with Reverse Image Search
===========================================

Detects phishing emails by analyzing profile photos using reverse image search.

Author: EGO Revolution Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class PhishingDetector:
    """
    Detects phishing emails using reverse image search and identity verification.
    
    Compares claimed identity in email with actual online presence found via
    Google reverse image search.
    """
    
    def __init__(self):
        """Initialize phishing detector"""
        self.reverse_image_search = None
        self.image_extractor = None
        
        try:
            from .reverse_image_search import ReverseImageSearchService
            self.reverse_image_search = ReverseImageSearchService()
        except ImportError as e:
            logger.warning(f"Reverse image search not available: {e}")
        
        try:
            from .image_extractor import ImageExtractor
            self.image_extractor = ImageExtractor()
        except ImportError as e:
            logger.warning(f"Image extractor not available: {e}")
    
    def analyze_email(self, email_data: Dict[str, Any], 
                     email_message: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze email for phishing indicators using reverse image search
        
        Args:
            email_data: Email data dictionary with:
                - sender: Sender email/name
                - subject: Email subject
                - body: Email body
            email_message: Optional full Gmail API message (for image extraction)
            
        Returns:
            Analysis dictionary with:
                - is_phishing: bool
                - confidence: float (0.0-1.0)
                - risk_score: float (0.0-1.0)
                - indicators: List of phishing indicators
                - recommendations: List of recommendations
                - image_analysis: Image search results (if available)
        """
        result = {
            'is_phishing': False,
            'confidence': 0.0,
            'risk_score': 0.0,
            'indicators': [],
            'recommendations': [],
            'image_analysis': None
        }
        
        if not self.reverse_image_search or not self.image_extractor:
            result['indicators'].append({
                'type': 'warning',
                'message': 'Reverse image search not available - install dependencies'
            })
            return result
        
        # Extract images from email
        images = []
        if email_message:
            images = self.image_extractor.extract_images_from_email(email_message)
        
        if not images:
            result['indicators'].append({
                'type': 'info',
                'message': 'No images found in email - cannot perform reverse image search'
            })
            return result
        
        # Find profile image
        profile_image = self.image_extractor.find_profile_image(images)
        
        if not profile_image:
            result['indicators'].append({
                'type': 'info',
                'message': 'No suitable profile image found'
            })
            return result
        
        # Perform reverse image search
        try:
            search_results = self.reverse_image_search.search_image(
                profile_image['data']
            )
            
            # Verify sender identity
            verification = self.reverse_image_search.verify_email_sender(
                email_data,
                profile_image['data']
            )
            
            result['image_analysis'] = {
                'search_results': search_results,
                'verification': verification
            }
            
            # Update risk score based on verification
            result['risk_score'] = verification['risk_score']
            result['confidence'] = 0.8 if search_results['matches'] else 0.3
            
            # Determine if phishing
            if verification['risk_score'] >= 0.7:
                result['is_phishing'] = True
                result['confidence'] = 0.9
            
            # Add indicators
            if verification['risk_score'] >= 0.7:
                result['indicators'].append({
                    'type': 'critical',
                    'message': 'Profile photo appears on multiple unrelated domains',
                    'details': search_results.get('analysis', '')
                })
            
            if search_results.get('suspicious_patterns'):
                for pattern in search_results['suspicious_patterns']:
                    result['indicators'].append({
                        'type': 'warning' if pattern['severity'] == 'medium' else 'critical',
                        'message': pattern['description'],
                        'pattern_type': pattern['type']
                    })
            
            # Add recommendations
            result['recommendations'] = verification.get('recommendations', [])
            
        except Exception as e:
            logger.error(f"Error in reverse image search analysis: {e}")
            result['indicators'].append({
                'type': 'error',
                'message': f'Error performing reverse image search: {str(e)}'
            })
        
        return result
    
    def get_phishing_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Generate human-readable phishing analysis summary
        
        Args:
            analysis: Analysis dictionary from analyze_email()
            
        Returns:
            Summary text
        """
        lines = []
        
        if analysis['is_phishing']:
            lines.append("🚨 PHISHING DETECTED")
            lines.append(f"Confidence: {analysis['confidence']:.0%}")
            lines.append(f"Risk Score: {analysis['risk_score']:.0%}")
        else:
            lines.append("✅ Email appears legitimate")
            if analysis['risk_score'] > 0.3:
                lines.append(f"⚠️  Risk Score: {analysis['risk_score']:.0%}")
        
        if analysis['indicators']:
            lines.append("\nIndicators:")
            for indicator in analysis['indicators']:
                icon = "🚨" if indicator['type'] == 'critical' else "⚠️" if indicator['type'] == 'warning' else "ℹ️"
                lines.append(f"  {icon} {indicator['message']}")
        
        if analysis['recommendations']:
            lines.append("\nRecommendations:")
            for rec in analysis['recommendations']:
                lines.append(f"  • {rec}")
        
        if analysis.get('image_analysis'):
            img_analysis = analysis['image_analysis']
            if img_analysis.get('search_results'):
                lines.append("\n" + img_analysis['search_results'].get('analysis', ''))
        
        return "\n".join(lines)

