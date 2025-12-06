#!/usr/bin/env python3
"""
OAuth2 Token Manager
====================

Manages OAuth2 token lifecycle with structured persistence and automatic refresh.

Features:
- Structured JSON metadata for token lifecycle tracking
- Automatic token refresh on expiry
- Revocation detection and handling
- Per-user token storage

Author: EGO Revolution Team
Version: 1.0.0
"""

import json
import pickle
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


class OAuthTokenManager:
    """Manages OAuth2 token lifecycle with structured persistence"""
    
    def __init__(self, token_path: Optional[Path] = None, user_id: Optional[str] = None):
        """
        Initialize OAuth token manager
        
        Args:
            token_path: Optional custom path for token file
            user_id: User ID for per-user token storage (string or int)
        """
        self.user_id = user_id or "default"
        # Use Path.home() / ".erika" for user-specific local file storage
        token_dir = Path.home() / ".erika"
        token_dir.mkdir(parents=True, exist_ok=True)
        
        # Use .pickle for Google library compatibility
        self.token_path = token_path or (token_dir / f"gmail_token_{self.user_id}.pickle")
        # Use .json for human-readable structured metadata and lifecycle tracking
        self.metadata_path = self.token_path.parent / f"gmail_token_{self.user_id}_metadata.json"
    
    def save_token(self, creds: Credentials) -> bool:
        """
        Save token with metadata
        
        Args:
            creds: Google OAuth2 Credentials object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # 1. Save pickle (for Google library compatibility)
            with open(self.token_path, 'wb') as f:
                pickle.dump(creds, f)
            
            # 2. Save structured metadata (for lifecycle tracking and diagnostics)
            # SECURITY: We do NOT save sensitive data (token, refresh_token, client_id, client_secret)
            # These are stored in the pickle file only, not in human-readable JSON
            metadata = {
                'token_uri': getattr(creds, 'token_uri', 'https://oauth2.googleapis.com/token'),
                'scopes': list(getattr(creds, 'scopes', [])),
                'expiry': creds.expiry.isoformat() if creds.expiry else None,
                'last_refreshed': datetime.now(timezone.utc).isoformat(),
                'user_id': str(self.user_id),
                # Note: token, refresh_token, client_id, client_secret are NOT saved here for security
                # They are only in the encrypted pickle file
            }
            
            with open(self.metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Token saved with metadata: {self.metadata_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save token: {e}")
            return False
    
    def load_token(self) -> Optional[Credentials]:
        """
        Load token with automatic refresh and revocation handling
        
        Returns:
            Credentials object if successful, None otherwise
            
        Raises:
            Exception: If token is revoked or cannot be refreshed
        """
        try:
            if not self.token_path.exists():
                logger.warning("Token file not found")
                return None
            
            with open(self.token_path, 'rb') as f:
                creds = pickle.load(f)
            
            # Auto-refresh if expired
            if hasattr(creds, 'expired') and creds.expired:
                if hasattr(creds, 'refresh_token') and creds.refresh_token:
                    try:
                        logger.info("🔄 Auto-refreshing expired token...")
                        # Use a Request transport object for the refresh
                        creds.refresh(Request()) 
                        self.save_token(creds)  # Persist refreshed token
                        logger.info("✅ Token auto-refreshed")
                    except Exception as refresh_error:
                        error_str = str(refresh_error).lower()
                        # Specific error detection for revocation
                        if 'invalid_grant' in error_str or 'revoked' in error_str:
                            logger.error("❌ Token revoked - requires full re-authentication")
                            # Delete invalid token files to force new flow
                            self.token_path.unlink(missing_ok=True)
                            self.metadata_path.unlink(missing_ok=True)
                            # Re-raise to signal the calling service needs to initiate the OAuth flow
                            raise Exception("Token has been revoked. Please re-authenticate.")
                        raise  # Re-raise other refresh errors
                else:
                    logger.error("❌ Token expired and no refresh token available. Requires re-authentication.")
                    raise Exception("Token expired. Please re-authenticate.")
            
            return creds
        except Exception as e:
            logger.error(f"❌ Failed to load token: {e}")
            return None
    
    def detect_revocation(self, api_error: Exception) -> bool:
        """
        Detect if API error indicates token revocation or permanent failure
        
        Args:
            api_error: Exception from API call
            
        Returns:
            True if error indicates revocation, False otherwise
        """
        error_str = str(api_error).lower()
        revocation_indicators = [
            'invalid_grant',
            'token has been revoked',
            'unauthorized',  # 401
            '401'
        ]
        return any(indicator in error_str for indicator in revocation_indicators)
    
    def get_token_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get token metadata without loading the full token
        
        Returns:
            Metadata dict if available, None otherwise
        """
        try:
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to load token metadata: {e}")
            return None

