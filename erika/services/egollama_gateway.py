#!/usr/bin/env python3
"""
Erika EgoLlama Gateway Integration
==================================

Integration service for connecting Erika to EgoLlama Gateway server.
Handles email syncing, model training, and AI-powered email analysis.

Author: EGO Revolution Team
Version: 1.0.0
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import html
import re

logger = logging.getLogger(__name__)


class EgoLlamaGatewayError(Exception):
    """Base exception for EgoLlama Gateway errors"""
    pass


class EgoLlamaGatewayConnectionError(EgoLlamaGatewayError):
    """Exception for connection errors"""
    pass


def _sanitize_email_content(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize email content before sending to gateway
    
    Args:
        email_data: Raw email data dictionary
        
    Returns:
        Sanitized email data dictionary
    """
    sanitized = email_data.copy()
    
    # Sanitize text fields
    text_fields = ['subject', 'body', 'content', 'sender', 'recipient']
    for field in text_fields:
        if field in sanitized and sanitized[field]:
            value = str(sanitized[field])
            # Remove null bytes and control characters (except newlines/tabs)
            value = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', value)
            # Escape HTML to prevent XSS
            value = html.escape(value)
            # Limit length
            max_lengths = {
                'subject': 500,
                'sender': 255,
                'recipient': 255,
                'body': 100000,
                'content': 100000
            }
            if field in max_lengths and len(value) > max_lengths[field]:
                value = value[:max_lengths[field]]
            sanitized[field] = value
    
    # Remove sensitive fields that shouldn't be sent
    sensitive_fields = ['raw_message', 'raw_payload', 'credentials', 'token']
    for field in sensitive_fields:
        sanitized.pop(field, None)
    
    return sanitized


class ErikaEgoLlamaGateway:
    """
    Integration service for Erika with EgoLlama Gateway
    
    Connects to EgoLlama Gateway server for:
    - Email data synchronization
    - AI-powered email analysis
    - Model training and management
    """
    
    def __init__(self, gateway_url: str = None, timeout: int = 30):
        """
        Initialize EgoLlama Gateway integration
        
        Args:
            gateway_url: EgoLlama Gateway URL. If None, will check:
                        1. EGOLLAMA_GATEWAY_URL environment variable
                        2. Config file (~/.erika/config.json)
                        3. Default: http://localhost:8082
            timeout: Request timeout in seconds (default: 30)
        """
        if gateway_url is None:
            # Try environment variable first
            import os
            gateway_url = os.getenv('EGOLLAMA_GATEWAY_URL')
            
            # If not in env, try config file
            if not gateway_url:
                try:
                    from pathlib import Path
                    import json
                    config_path = Path.home() / ".erika" / "config.json"
                    if config_path.exists():
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                            gateway_url = config.get('egollama_gateway_url')
                except Exception:
                    pass
            
            # Default fallback
            if not gateway_url:
                gateway_url = "http://localhost:8082"
        
        self.gateway_url = gateway_url.rstrip('/')
        self.timeout = timeout
        self._health_check()
    
    def _health_check(self) -> bool:
        """
        Check if gateway is available
        
        Returns:
            True if gateway is reachable, False otherwise
        """
        try:
            response = requests.get(
                f"{self.gateway_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"✅ Connected to EgoLlama Gateway at {self.gateway_url}")
                return True
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ EgoLlama Gateway not available at {self.gateway_url}")
            logger.warning("   Gateway features will be disabled until connection is available")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error checking gateway health: {e}")
            return False
        return False
    
    def is_available(self) -> bool:
        """
        Check if gateway is currently available
        
        Returns:
            True if gateway is reachable
        """
        return self._health_check()
    
    def sync_email(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Sync email to EgoLlama Gateway for processing
        
        Args:
            email_data: Email data dictionary with fields like:
                - subject, sender, body, content
                - gmail_message_id, gmail_thread_id
                - category, priority, sentiment
                
        Returns:
            Gateway response dictionary or None on error
        """
        try:
            # Sanitize email data
            sanitized = _sanitize_email_content(email_data)
            
            # Prepare payload
            payload = {
                'action': 'store_erika_email',
                'email_data': sanitized,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to gateway
            response = requests.post(
                f"{self.gateway_url}/api/erika/email",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Synced email to gateway: {sanitized.get('subject', 'Unknown')[:50]}")
                return result
            else:
                logger.warning(f"Gateway returned status {response.status_code}: {response.text[:200]}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ Could not connect to EgoLlama Gateway at {self.gateway_url}")
            raise EgoLlamaGatewayConnectionError(f"Gateway not available at {self.gateway_url}")
        except Exception as e:
            logger.error(f"Error syncing email to gateway: {e}")
            return None
    
    def batch_sync_emails(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch sync multiple emails to gateway
        
        Args:
            emails: List of email data dictionaries
            
        Returns:
            Summary dictionary with:
                - total: Total emails
                - success: Successfully synced count
                - failed: Failed count
                - errors: List of error messages
        """
        results = {
            'total': len(emails),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for email in emails:
            try:
                response = self.sync_email(email)
                if response:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to sync email: {email.get('subject', 'Unknown')}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
        
        logger.info(f"Batch sync complete: {results['success']}/{results['total']} successful")
        return results
    
    def analyze_email(self, email_data: Dict[str, Any], model: str = "erika-email-classifier") -> Optional[Dict[str, Any]]:
        """
        Analyze email using Erika's model in the gateway
        
        Args:
            email_data: Email data to analyze
            model: Model name to use (default: erika-email-classifier)
            
        Returns:
            Analysis results dictionary with:
                - analysis: Analysis text
                - model: Model used
                - usage: Token usage information
        """
        try:
            # Sanitize email data
            sanitized = _sanitize_email_content(email_data)
            
            # Prepare prompt
            subject = sanitized.get('subject', '')
            body = sanitized.get('body', '') or sanitized.get('content', '')
            body_preview = body[:1000] if body else ''
            
            prompt = f"Analyze this email and provide insights:\n\nSubject: {subject}\n\nBody: {body_preview}"
            
            # Prepare payload for OpenAI-compatible API
            payload = {
                'model': model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.3,
                'max_tokens': 500
            }
            
            # Send to gateway
            response = requests.post(
                f"{self.gateway_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                return {
                    'analysis': analysis_text,
                    'model': result.get('model', model),
                    'usage': result.get('usage', {}),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                logger.warning(f"Analysis request returned status {response.status_code}: {response.text[:200]}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ Could not connect to EgoLlama Gateway for analysis")
            return None
        except Exception as e:
            logger.error(f"Error analyzing email: {e}")
            return None
    
    def get_model_status(self) -> Optional[Dict[str, Any]]:
        """
        Get status of Erika's model in the gateway
        
        Returns:
            Model status dictionary or None on error
        """
        try:
            response = requests.get(
                f"{self.gateway_url}/api/erika/model/status",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Model status request returned status {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ Could not connect to EgoLlama Gateway for model status")
            return None
        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            return None
    
    def train_model(self, training_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Trigger Erika model training in the gateway
        
        Args:
            training_config: Optional training configuration dictionary
            
        Returns:
            Training job response or None on error
        """
        try:
            payload = {
                'action': 'train_erika_model',
                'config': training_config or {}
            }
            
            response = requests.post(
                f"{self.gateway_url}/api/erika/model/train",
                json=payload,
                timeout=300,  # Longer timeout for training
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Model training initiated")
                return result
            else:
                logger.warning(f"Training request returned status {response.status_code}: {response.text[:200]}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ Could not connect to EgoLlama Gateway for training")
            return None
        except Exception as e:
            logger.error(f"Error triggering model training: {e}")
            return None
    
    def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Optional[Dict[str, Any]]:
        """
        Chat with Erika via the gateway
        
        Args:
            message: User message
            conversation_history: Optional conversation history list of {role, content} dicts
            
        Returns:
            Chat response dictionary with:
                - response: Erika's response text
                - model: Model used
                - usage: Token usage
        """
        try:
            # Build messages list
            messages = []
            
            # Add system message
            messages.append({
                'role': 'system',
                'content': 'You are Erika, an AI assistant specialized in email management and natural language processing. You help users manage their emails with harmony and efficiency.'
            })
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({
                'role': 'user',
                'content': message
            })
            
            # Prepare payload
            payload = {
                'model': 'erika',
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 1000
            }
            
            # Send to gateway
            response = requests.post(
                f"{self.gateway_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                return {
                    'response': response_text,
                    'model': result.get('model', 'erika'),
                    'usage': result.get('usage', {}),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                logger.warning(f"Chat request returned status {response.status_code}: {response.text[:200]}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ Could not connect to EgoLlama Gateway for chat")
            return None
        except Exception as e:
            logger.error(f"Error chatting with Erika: {e}")
            return None

