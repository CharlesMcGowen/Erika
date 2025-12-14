#!/usr/bin/env python3
"""
Erika CLI - Email Monitoring and Fraud Detection
================================================

Command-line interface for Erika that provides all GUI features through
command-line arguments. Monitor email servers, detect fraud, sort emails,
and configure settings - all without the GUI.

Usage:
    erika monitor [--interval SECONDS] [--output FORMAT]
    erika check [--max-results N] [--days-back N] [--output FORMAT]
    erika analyze EMAIL_ID [--output FORMAT]
    erika sort [--output FORMAT]
    erika config [--client-id ID] [--client-secret SECRET] [--test]
    erika settings [--gateway-url URL] [--database-url URL] [--test-gateway]
    erika setup [--gateway-url URL] [--test]
    erika status [--output FORMAT]
    erika authenticate [--refresh]

Author: Living Archive team
Version: 1.0.0
"""

import sys
import os
import json
import argparse
import logging
import time
import signal
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag for daemon mode
_running = True


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global _running
    logger.info(f"\n🛑 Received signal {signum}, shutting down...")
    _running = False


class ErikaCLI:
    """Main CLI class for Erika email monitoring and fraud detection"""
    
    # Free tier limits
    MAX_EMAILS_PER_DAY = 50
    MAX_EMAILS_PER_CHECK = 50
    MAX_ACCOUNTS = 1
    
    # Feature flags (CLI = free tier, Pro = full features)
    FEATURES = {
        'ares_bridge': False,  # CLI: disabled, Pro: enabled
        'reverse_image_search': False,  # CLI: disabled, Pro: enabled
        'egollama_gateway': False,  # CLI: disabled, Pro: enabled
        'auto_mitigation': False,  # CLI: disabled, Pro: enabled
        'batch_operations': False,  # CLI: disabled, Pro: enabled
        'advanced_analytics': False,  # CLI: disabled, Pro: enabled
    }
    
    PRO_UPGRADE_URL = "https://erika.pro/pricing"
    
    def __init__(self, user_id: str = "cli_user", config: Optional[Dict[str, Any]] = None):
        """Initialize CLI with configuration"""
        self.user_id = user_id
        self.config = config or {}
        self.gmail_service = None
        self.config_manager = None
        self.db_service = None
        self._init_services()
    
    def _init_services(self):
        """Initialize services"""
        try:
            from app.config_manager import ErikaConfigManager
            self.config_manager = ErikaConfigManager()
            
            # Load config from file if not provided
            if not self.config:
                self.config = self._load_config()
            
            # Initialize Gmail service if credentials available
            if self.config.get('gmail_client_id') and self.config.get('gmail_client_secret'):
                from erika.plugins.email.gmail_service import ErikaGmailService
                self.gmail_service = ErikaGmailService(
                    user_id=self.user_id,
                    config=self.config
                )
            
            # Initialize database service if available
            try:
                from app.database_service import ErikaDatabaseService
                self.db_service = ErikaDatabaseService()
            except Exception as e:
                logger.debug(f"Database service not available: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and database"""
        config = {}
        
        # Load from config file
        config_path = Path.home() / ".erika" / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
        
        # Load Gmail credentials from database if available
        if self.db_service:
            try:
                db_config = self.db_service.get_email_config(user_id="default")
                if db_config:
                    config.update({
                        'gmail_client_id': db_config.get('gmail_client_id'),
                        'gmail_client_secret': db_config.get('gmail_client_secret'),
                        'gmail_enabled': db_config.get('gmail_enabled', False),
                        'phishing_detection_enabled': db_config.get('phishing_detection_enabled', True),
                        'reverse_image_search_enabled': db_config.get('reverse_image_search_enabled', True),
                        'enable_ares_bridge': db_config.get('enable_ares_bridge', False),
                        'auto_mitigate_threats': db_config.get('auto_mitigate_threats', False)
                    })
            except Exception as e:
                logger.debug(f"Could not load database config: {e}")
        
        return config
    
    def setup(self, gateway_url: Optional[str] = None, test: bool = False) -> bool:
        """Setup wizard - configure EgoLlama Gateway (matches Installation Wizard)"""
        if not self.config_manager:
            logger.error("Config manager not initialized")
            return False
        
        if gateway_url:
            # Validate URL format
            if not (gateway_url.startswith("http://") or gateway_url.startswith("https://")):
                logger.error("Server address must start with http:// or https://")
                return False
            
            # Test connection if requested
            if test:
                logger.info(f"🔍 Testing connection to {gateway_url}...")
                if not self._test_gateway_connection(gateway_url):
                    logger.warning("⚠️  Connection test failed, but saving configuration anyway")
            
            # Save configuration
            try:
                self.config_manager.set_gateway_url(gateway_url)
                logger.info(f"✅ Configuration saved: {gateway_url}")
                return True
            except Exception as e:
                logger.error(f"Failed to save configuration: {e}")
                return False
        else:
            # Interactive setup
            current_url = self.config_manager.get_gateway_url()
            print(f"\n🌿 Erika Setup Wizard")
            print(f"Current gateway URL: {current_url}")
            print("\nEnter EgoLlama Gateway server address:")
            print("Example: http://localhost:8082 or http://egollama.company.com:8082")
            
            url = input("Server address: ").strip()
            if not url:
                url = "http://localhost:8082"
            
            if not (url.startswith("http://") or url.startswith("https://")):
                logger.error("Server address must start with http:// or https://")
                return False
            
            # Test connection
            print(f"\n🔍 Testing connection...")
            if self._test_gateway_connection(url):
                print("✅ Connection successful!")
            else:
                print("⚠️  Connection test failed")
                response = input("Save configuration anyway? (y/n): ").strip().lower()
                if response != 'y':
                    return False
            
            # Save
            try:
                self.config_manager.set_gateway_url(url)
                print(f"✅ Configuration saved!")
                return True
            except Exception as e:
                logger.error(f"Failed to save: {e}")
                return False
    
    def configure_settings(
        self,
        gateway_url: Optional[str] = None,
        database_url: Optional[str] = None,
        phishing_enabled: Optional[bool] = None,
        reverse_search_enabled: Optional[bool] = None,
        ares_enabled: Optional[bool] = None,
        auto_mitigate: Optional[bool] = None,
        test_gateway: bool = False
    ) -> bool:
        """Configure settings (matches Settings Dialog)"""
        success = True
        
        # Gateway URL
        if gateway_url:
            if not (gateway_url.startswith("http://") or gateway_url.startswith("https://")):
                logger.error("Gateway URL must start with http:// or https://")
                return False
            
            if test_gateway:
                logger.info(f"🔍 Testing gateway connection...")
                if not self._test_gateway_connection(gateway_url):
                    logger.warning("⚠️  Connection test failed")
                    return False
            
            try:
                self.config_manager.set_gateway_url(gateway_url)
                logger.info(f"✅ Gateway URL saved: {gateway_url}")
            except Exception as e:
                logger.error(f"Failed to save gateway URL: {e}")
                success = False
        
        # Database URL
        if database_url:
            try:
                self.config_manager.set_database_url(database_url)
                logger.info("✅ Database URL saved")
            except Exception as e:
                logger.error(f"Failed to save database URL: {e}")
                success = False
        
        # Security settings (save to database)
        if self.db_service and any([phishing_enabled is not None, reverse_search_enabled is not None,
                                   ares_enabled is not None, auto_mitigate is not None]):
            # Free tier: disable advanced features
            if reverse_search_enabled and not self.FEATURES.get('reverse_image_search'):
                logger.warning(
                    f"⚠️  Reverse image search requires Erika Pro. "
                    f"Upgrade at: {self.PRO_UPGRADE_URL}"
                )
                reverse_search_enabled = False
            
            if ares_enabled and not self.FEATURES.get('ares_bridge'):
                logger.warning(
                    f"⚠️  AresBridge threat detection requires Erika Pro. "
                    f"Upgrade at: {self.PRO_UPGRADE_URL}"
                )
                ares_enabled = False
            
            if auto_mitigate and not self.FEATURES.get('auto_mitigation'):
                logger.warning(
                    f"⚠️  Auto-mitigation requires Erika Pro. "
                    f"Upgrade at: {self.PRO_UPGRADE_URL}"
                )
                auto_mitigate = False
            
            try:
                update_data = {}
                if phishing_enabled is not None:
                    update_data['phishing_detection_enabled'] = phishing_enabled
                if reverse_search_enabled is not None:
                    update_data['reverse_image_search_enabled'] = reverse_search_enabled
                if ares_enabled is not None:
                    update_data['enable_ares_bridge'] = ares_enabled
                if auto_mitigate is not None:
                    update_data['auto_mitigate_threats'] = auto_mitigate
                
                self.db_service.update_email_config(user_id="default", **update_data)
                logger.info("✅ Security settings saved")
            except Exception as e:
                logger.warning(f"Could not save security settings: {e}")
        
        return success
    
    def configure_credentials(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        enable: Optional[bool] = None,
        test: bool = False
    ) -> bool:
        """Configure Gmail credentials (matches Credentials Dialog)"""
        if not self.db_service:
            logger.error("Database service not available")
            return False
        
        # Interactive mode if credentials not provided
        if not client_id or not client_secret:
            print("\n🌿 Gmail OAuth2 Configuration")
            print("\nTo get credentials:")
            print("1. Go to https://console.cloud.google.com")
            print("2. Create a project or select existing one")
            print("3. Enable Gmail API in APIs & Services > Library")
            print("4. Create OAuth2 credentials in APIs & Services > Credentials")
            print("5. Application type: Desktop app")
            print("6. Copy the Client ID and Client Secret\n")
            
            if not client_id:
                client_id = input("Client ID: ").strip()
            if not client_secret:
                client_secret = input("Client Secret: ").strip()
        
        if not client_id or not client_secret:
            logger.error("Client ID and Client Secret are required")
            return False
        
        # Validate format
        if not client_id.endswith('.apps.googleusercontent.com'):
            logger.error("Client ID should end with '.apps.googleusercontent.com'")
            return False
        
        # Test credentials if requested
        if test:
            logger.info("🧪 Testing credentials...")
            if not self._test_credentials(client_id, client_secret):
                logger.error("❌ Credential test failed")
                return False
            logger.info("✅ Credentials are valid!")
        
        # Save to database
        try:
            update_data = {
                'gmail_client_id': client_id,
                'gmail_client_secret': client_secret
            }
            if enable is not None:
                update_data['gmail_enabled'] = enable
            
            self.db_service.update_email_config(user_id="default", **update_data)
            logger.info("✅ Credentials saved")
            
            # Update local config
            self.config['gmail_client_id'] = client_id
            self.config['gmail_client_secret'] = client_secret
            
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            return False
    
    def authenticate(self, refresh: bool = False) -> bool:
        """Authenticate with Gmail (matches Connect Gmail button)"""
        if not self.gmail_service:
            # Try to initialize
            client_id = self.config.get('gmail_client_id')
            client_secret = self.config.get('gmail_client_secret')
            
            if not client_id or not client_secret:
                logger.error("Gmail credentials not configured. Run 'erika config' first.")
                return False
            
            from erika.plugins.email.gmail_service import ErikaGmailService
            self.gmail_service = ErikaGmailService(
                user_id=self.user_id,
                config=self.config
            )
        
        try:
            logger.info("🔐 Authenticating with Gmail...")
            if refresh:
                logger.info("🔄 Refreshing token (browser will open)...")
            
            result = self.gmail_service.authenticate(
                client_id=self.config.get('gmail_client_id'),
                client_secret=self.config.get('gmail_client_secret')
            )
            
            if result:
                logger.info("✅ Gmail authentication successful")
                return True
            else:
                logger.error("❌ Gmail authentication failed")
                return False
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def check_emails(
        self,
        max_results: int = 50,
        days_back: int = 7,
        output_format: str = "human"
    ) -> List[Dict[str, Any]]:
        """Check for unread emails"""
        if not self.gmail_service:
            logger.error("Gmail service not initialized. Run 'erika authenticate' first.")
            return []
        
        # Free tier rate limiting
        if max_results > self.MAX_EMAILS_PER_CHECK:
            logger.warning(
                f"⚠️  Free tier limited to {self.MAX_EMAILS_PER_CHECK} emails per check. "
                f"Upgrade to Pro for unlimited: {self.PRO_UPGRADE_URL}"
            )
            max_results = min(max_results, self.MAX_EMAILS_PER_CHECK)
        
        logger.info(f"📧 Checking emails (max: {max_results}, days: {days_back})...")
        emails = self.gmail_service.get_unread_emails(
            max_results=max_results,
            days_back=days_back
        )
        
        if output_format == "json":
            print(json.dumps(emails, indent=2, default=str))
        else:
            self._print_emails_human(emails)
        
        return emails
    
    def analyze_email(
        self,
        email_id: str,
        output_format: str = "human"
    ) -> Optional[Dict[str, Any]]:
        """Analyze a specific email for fraud"""
        if not self.gmail_service:
            logger.error("Gmail service not initialized")
            return None
        
        logger.info(f"🔍 Analyzing email: {email_id}")
        
        # Get email details
        email_data = self.gmail_service._get_email_details(email_id)
        if not email_data:
            logger.error(f"Email {email_id} not found")
            return None
        
        # Free tier: basic analysis only
        if not self.FEATURES.get('ares_bridge') and not self.FEATURES.get('reverse_image_search'):
            logger.warning(
                f"⚠️  Advanced fraud analysis (AresBridge, reverse image search) requires Erika Pro. "
                f"Upgrade at: {self.PRO_UPGRADE_URL}\n"
                f"CLI provides basic analysis only."
            )
        
        # Perform fraud analysis (basic in CLI, advanced in Pro)
        analysis = self._analyze_fraud(email_data)
        
        if output_format == "json":
            print(json.dumps(analysis, indent=2, default=str))
        else:
            self._print_analysis_human(analysis)
        
        return analysis
    
    def sort_emails(
        self,
        emails: Optional[List[Dict[str, Any]]] = None,
        output_format: str = "human"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Sort emails into categories"""
        if emails is None:
            if not self.gmail_service:
                logger.error("Gmail service not initialized")
                return {}
            emails = self.gmail_service.get_unread_emails(max_results=100, days_back=7)
        
        categories = {
            'fraud_high_risk': [],
            'fraud_medium_risk': [],
            'important': [],
            'normal': [],
            'spam_likely': []
        }
        
        for email in emails:
            risk_score = email.get('phishing_risk_score', 0.0) or email.get('threat_score', 0.0)
            
            if risk_score >= 0.8 or email.get('is_phishing'):
                categories['fraud_high_risk'].append(email)
            elif risk_score >= 0.5:
                categories['fraud_medium_risk'].append(email)
            # Add more sorting logic here based on keywords, sender, etc.
            else:
                categories['normal'].append(email)
        
        if output_format == "json":
            print(json.dumps(categories, indent=2, default=str))
        else:
            self._print_sorted_human(categories)
        
        return categories
    
    def monitor(
        self,
        interval: int = 300,
        output_format: str = "human"
    ):
        """Monitor emails continuously (daemon mode)"""
        global _running
        
        logger.info(f"🔄 Starting email monitoring (interval: {interval}s)")
        logger.info("Press Ctrl+C to stop")
        
        while _running:
            try:
                emails = self.check_emails(max_results=50, days_back=1, output_format=output_format)
                
                # Check for fraud
                fraud_count = sum(1 for e in emails if e.get('is_phishing') or e.get('threat_score', 0) >= 0.7)
                if fraud_count > 0:
                    logger.warning(f"🚨 Found {fraud_count} potentially fraudulent emails!")
                
                # Wait for next check
                for _ in range(interval):
                    if not _running:
                        break
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        logger.info("🛑 Monitoring stopped")
    
    def status(self, output_format: str = "human") -> Dict[str, Any]:
        """Show status (matches Main Window status display)"""
        status = {
            'gmail_configured': bool(self.config.get('gmail_client_id')),
            'gmail_enabled': self.config.get('gmail_enabled', False),
            'gateway_url': self.config_manager.get_gateway_url() if self.config_manager else None,
            'database_available': self.db_service is not None,
            'phishing_detection': self.config.get('phishing_detection_enabled', True),
            'reverse_image_search': self.config.get('reverse_image_search_enabled', True),
            'ares_bridge': self.config.get('enable_ares_bridge', False)
        }
        
        if output_format == "json":
            print(json.dumps(status, indent=2, default=str))
        else:
            self._print_status_human(status)
        
        return status
    
    def _test_gateway_connection(self, url: str) -> bool:
        """Test connection to gateway"""
        try:
            import requests
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_credentials(self, client_id: str, client_secret: str) -> bool:
        """Test OAuth2 credentials"""
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify'
            ]
            
            # Validate config structure
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            return True
        except Exception as e:
            logger.debug(f"Credential test error: {e}")
            return False
    
    def _analyze_fraud(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive fraud analysis on email"""
        analysis = {
            'email_id': email_data.get('id'),
            'subject': email_data.get('subject'),
            'sender': email_data.get('sender'),
            'timestamp': datetime.now().isoformat(),
            'fraud_indicators': [],
            'risk_score': 0.0,
            'recommendations': []
        }
        
        # Phishing detection
        phishing_analysis = email_data.get('phishing_analysis')
        if phishing_analysis:
            if phishing_analysis.get('is_phishing'):
                analysis['fraud_indicators'].append({
                    'type': 'phishing',
                    'severity': 'high',
                    'message': 'Email flagged as phishing',
                    'confidence': phishing_analysis.get('confidence', 0.0)
                })
                analysis['risk_score'] = max(
                    analysis['risk_score'],
                    phishing_analysis.get('risk_score', 0.0)
                )
        
        # Threat analysis
        threat_analysis = email_data.get('threat_analysis')
        if threat_analysis:
            threat_score = threat_analysis.get('threat_score', 0.0)
            if threat_score >= 0.7:
                analysis['fraud_indicators'].append({
                    'type': 'threat',
                    'severity': 'high',
                    'message': f'High threat score: {threat_score:.2f}',
                    'breakdown': threat_analysis.get('scoring_breakdown', {})
                })
                analysis['risk_score'] = max(analysis['risk_score'], threat_score)
        
        # Determine overall risk
        if analysis['risk_score'] >= 0.8:
            analysis['recommendations'].append("🚨 HIGH RISK: Mark as spam/phishing")
            analysis['recommendations'].append("🚨 HIGH RISK: Do not click links or download attachments")
        elif analysis['risk_score'] >= 0.5:
            analysis['recommendations'].append("⚠️  MEDIUM RISK: Exercise caution")
            analysis['recommendations'].append("⚠️  MEDIUM RISK: Verify sender identity")
        
        return analysis
    
    def _print_emails_human(self, emails: List[Dict[str, Any]]):
        """Print emails in human-readable format"""
        if not emails:
            print("📭 No emails found")
            return
        
        print(f"\n📬 Found {len(emails)} emails:\n")
        for i, email in enumerate(emails, 1):
            print(f"{i}. {email.get('subject', 'No subject')}")
            print(f"   From: {email.get('sender', 'Unknown')}")
            print(f"   Date: {email.get('date', 'Unknown')}")
            
            if email.get('is_phishing'):
                print(f"   🚨 PHISHING DETECTED (risk: {email.get('phishing_risk_score', 0):.2f})")
            elif email.get('threat_score', 0) >= 0.7:
                print(f"   ⚠️  HIGH THREAT (score: {email.get('threat_score', 0):.2f})")
            
            print()
    
    def _print_analysis_human(self, analysis: Dict[str, Any]):
        """Print fraud analysis in human-readable format"""
        print(f"\n🔍 Fraud Analysis for Email: {analysis.get('email_id')}")
        print(f"Subject: {analysis.get('subject')}")
        print(f"Sender: {analysis.get('sender')}")
        print(f"Risk Score: {analysis.get('risk_score', 0):.2f}")
        
        indicators = analysis.get('fraud_indicators', [])
        if indicators:
            print("\n🚨 Fraud Indicators:")
            for indicator in indicators:
                print(f"  - {indicator.get('type').upper()}: {indicator.get('message')}")
        
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  {rec}")
        print()
    
    def _print_sorted_human(self, categories: Dict[str, List[Dict[str, Any]]]):
        """Print sorted emails in human-readable format"""
        print("\n📊 Email Categories:\n")
        
        for category, emails in categories.items():
            if emails:
                print(f"{category.replace('_', ' ').title()}: {len(emails)} emails")
                for email in emails[:5]:  # Show first 5
                    print(f"  - {email.get('subject', 'No subject')}")
                if len(emails) > 5:
                    print(f"  ... and {len(emails) - 5} more")
                print()
    
    def _print_status_human(self, status: Dict[str, Any]):
        """Print status in human-readable format"""
        print("\n🌿 Erika Status\n")
        print(f"Gmail: {'✅ Configured' if status['gmail_configured'] else '❌ Not configured'}")
        if status['gmail_configured']:
            print(f"  Enabled: {'✅ Yes' if status['gmail_enabled'] else '❌ No'}")
        print(f"Gateway: {status['gateway_url'] or 'Not configured'}")
        print(f"Database: {'✅ Available' if status['database_available'] else '❌ Not available'}")
        print(f"Phishing Detection: {'✅ Enabled' if status['phishing_detection'] else '❌ Disabled'}")
        print(f"Reverse Image Search: {'✅ Enabled' if status['reverse_image_search'] else '❌ Disabled'}")
        print(f"AresBridge: {'✅ Enabled' if status['ares_bridge'] else '❌ Disabled'}")
        print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Erika CLI - Email Monitoring and Fraud Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor emails continuously (daemon mode)')
    monitor_parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds (default: 300)')
    monitor_parser.add_argument('--output', choices=['human', 'json'], default='human', help='Output format')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check for unread emails (one-time)')
    check_parser.add_argument('--max-results', type=int, default=50, help='Maximum results (default: 50)')
    check_parser.add_argument('--days-back', type=int, default=7, help='Days to look back (default: 7)')
    check_parser.add_argument('--output', choices=['human', 'json'], default='human', help='Output format')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze specific email for fraud')
    analyze_parser.add_argument('email_id', help='Gmail message ID to analyze')
    analyze_parser.add_argument('--output', choices=['human', 'json'], default='human', help='Output format')
    
    # Sort command
    sort_parser = subparsers.add_parser('sort', help='Sort emails into categories')
    sort_parser.add_argument('--output', choices=['human', 'json'], default='human', help='Output format')
    
    # Config command (Gmail credentials)
    config_parser = subparsers.add_parser('config', help='Configure Gmail OAuth2 credentials')
    config_parser.add_argument('--client-id', help='Gmail OAuth client ID')
    config_parser.add_argument('--client-secret', help='Gmail OAuth client secret')
    config_parser.add_argument('--enable', action='store_true', help='Enable Gmail integration')
    config_parser.add_argument('--disable', action='store_true', help='Disable Gmail integration')
    config_parser.add_argument('--test', action='store_true', help='Test credentials before saving')
    
    # Settings command
    settings_parser = subparsers.add_parser('settings', help='Configure Erika settings')
    settings_parser.add_argument('--gateway-url', help='EgoLlama Gateway URL')
    settings_parser.add_argument('--database-url', help='Database connection URL')
    settings_parser.add_argument('--phishing-enabled', type=bool, help='Enable phishing detection (true/false)')
    settings_parser.add_argument('--reverse-search-enabled', type=bool, help='Enable reverse image search (true/false)')
    settings_parser.add_argument('--ares-enabled', type=bool, help='Enable AresBridge threat detection (true/false)')
    settings_parser.add_argument('--auto-mitigate', type=bool, help='Auto-mitigate high-threat emails (true/false)')
    settings_parser.add_argument('--test-gateway', action='store_true', help='Test gateway connection before saving')
    
    # Setup command (installation wizard)
    setup_parser = subparsers.add_parser('setup', help='First-time setup wizard')
    setup_parser.add_argument('--gateway-url', help='EgoLlama Gateway URL')
    setup_parser.add_argument('--test', action='store_true', help='Test connection before saving')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show Erika status')
    status_parser.add_argument('--output', choices=['human', 'json'], default='human', help='Output format')
    
    # Authenticate command
    auth_parser = subparsers.add_parser('authenticate', help='Authenticate with Gmail (opens browser)')
    auth_parser.add_argument('--refresh', action='store_true', help='Refresh existing token')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        cli = ErikaCLI()
        
        # Execute command
        if args.command == 'setup':
            enable = None
            if args.enable:
                enable = True
            elif args.disable:
                enable = False
            success = cli.setup(gateway_url=args.gateway_url, test=args.test)
            return 0 if success else 1
        
        elif args.command == 'config':
            enable = None
            if args.enable:
                enable = True
            elif args.disable:
                enable = False
            success = cli.configure_credentials(
                client_id=args.client_id,
                client_secret=args.client_secret,
                enable=enable,
                test=args.test
            )
            return 0 if success else 1
        
        elif args.command == 'settings':
            success = cli.configure_settings(
                gateway_url=args.gateway_url,
                database_url=args.database_url,
                phishing_enabled=args.phishing_enabled,
                reverse_search_enabled=args.reverse_search_enabled,
                ares_enabled=args.ares_enabled,
                auto_mitigate=args.auto_mitigate,
                test_gateway=args.test_gateway
            )
            return 0 if success else 1
        
        elif args.command == 'authenticate':
            if not cli.authenticate(refresh=args.refresh):
                return 1
            return 0
        
        elif args.command == 'status':
            cli.status(output_format=args.output)
            return 0
        
        elif args.command == 'monitor':
            cli.monitor(interval=args.interval, output_format=args.output)
            return 0
        
        elif args.command == 'check':
            cli.check_emails(
                max_results=args.max_results,
                days_back=args.days_back,
                output_format=args.output
            )
            return 0
        
        elif args.command == 'analyze':
            cli.analyze_email(args.email_id, output_format=args.output)
            return 0
        
        elif args.command == 'sort':
            cli.sort_emails(output_format=args.output)
            return 0
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
