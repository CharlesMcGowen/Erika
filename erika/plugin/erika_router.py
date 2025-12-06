#!/usr/bin/env python3
"""
Erika FastAPI Router
====================

FastAPI router for Erika email assistant endpoints.
This router is registered with EgoLlama Gateway as a plugin.

Author: Living Archive team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import Erika services
from ..plugins.email.gmail_service import ErikaGmailService, GmailAuthenticationError
from ..services.egollama_gateway import ErikaEgoLlamaGateway
from ..database import db_session
from ..models import ErikaEmailConfig, ErikaEmailAnalysis

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/erika",
    tags=["Erika Email Assistant"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class EmailListRequest(BaseModel):
    max_results: int = 50
    days_back: int = 7
    keywords: Optional[List[str]] = None


class EmailAnalyzeRequest(BaseModel):
    email_id: str
    analysis_type: Optional[str] = "full"  # full, quick, phishing


class GmailConnectRequest(BaseModel):
    client_id: str
    client_secret: str
    user_id: str = "default"


# ============================================================================
# EMAIL ENDPOINTS
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for Erika plugin"""
    return JSONResponse(content={
        "status": "healthy",
        "plugin": "erika",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })


@router.get("/emails")
async def get_emails(
    max_results: int = 50,
    days_back: int = 7,
    keywords: Optional[str] = None
):
    """
    Get user's emails from Gmail
    
    Args:
        max_results: Maximum number of emails to retrieve
        days_back: Number of days to look back
        keywords: Comma-separated keywords to filter emails
        
    Returns:
        List of email dictionaries
    """
    try:
        # Parse keywords if provided
        keyword_list = [k.strip() for k in keywords.split(',')] if keywords else None
        
        # Get email config from database
        with db_session() as session:
            config = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.user_id == "default"
            ).first()
            
            if not config or not config.gmail_enabled:
                raise HTTPException(
                    status_code=400,
                    detail="Gmail not configured. Please connect Gmail first."
                )
            
            # Initialize Gmail service
            gmail_service = ErikaGmailService(
                client_id=config.gmail_client_id,
                client_secret=config.gmail_client_secret,
                user_id=config.user_id
            )
            
            # Fetch emails
            emails = gmail_service.get_unread_emails(
                max_results=max_results,
                days_back=days_back
            )
            
            # Filter by keywords if provided
            if keyword_list:
                filtered_emails = []
                for email in emails:
                    subject = email.get('subject', '').lower()
                    sender = email.get('sender', '').lower()
                    body = email.get('body', '').lower()
                    
                    if any(keyword.lower() in subject or 
                           keyword.lower() in sender or 
                           keyword.lower() in body 
                           for keyword in keyword_list):
                        filtered_emails.append(email)
                emails = filtered_emails
            
            return JSONResponse(content={
                "success": True,
                "emails": emails,
                "count": len(emails)
            })
            
    except GmailAuthenticationError as e:
        logger.error(f"Gmail authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Gmail authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error fetching emails: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch emails: {str(e)}"
        )


@router.get("/emails/{email_id}")
async def get_email_details(email_id: str):
    """Get detailed information about a specific email"""
    try:
        with db_session() as session:
            config = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.user_id == "default"
            ).first()
            
            if not config or not config.gmail_enabled:
                raise HTTPException(
                    status_code=400,
                    detail="Gmail not configured"
                )
            
            gmail_service = ErikaGmailService(
                client_id=config.gmail_client_id,
                client_secret=config.gmail_client_secret,
                user_id=config.user_id
            )
            
            # Get email details (this would need to be implemented in gmail_service)
            # For now, return a placeholder
            return JSONResponse(content={
                "success": True,
                "email_id": email_id,
                "message": "Email details endpoint - implementation needed"
            })
            
    except Exception as e:
        logger.error(f"Error getting email details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get email details: {str(e)}"
        )


@router.post("/emails/analyze")
async def analyze_email(request: EmailAnalyzeRequest):
    """
    Analyze an email with AI
    
    Args:
        request: Email analysis request
        
    Returns:
        Analysis results
    """
    try:
        # Get email from Gmail
        with db_session() as session:
            config = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.user_id == "default"
            ).first()
            
            if not config or not config.gmail_enabled:
                raise HTTPException(
                    status_code=400,
                    detail="Gmail not configured"
                )
            
            gmail_service = ErikaGmailService(
                client_id=config.gmail_client_id,
                client_secret=config.gmail_client_secret,
                user_id=config.user_id
            )
            
            # Get email details
            # TODO: Implement get_email_by_id in gmail_service
            # email = gmail_service.get_email_by_id(request.email_id)
            
            # Analyze with EgoLlama Gateway
            gateway = ErikaEgoLlamaGateway()
            if gateway.is_available():
                # Sync email to gateway for analysis
                # analysis = gateway.analyze_email(email_data)
                pass
            
            return JSONResponse(content={
                "success": True,
                "email_id": request.email_id,
                "analysis_type": request.analysis_type,
                "message": "Email analysis endpoint - full implementation needed"
            })
            
    except Exception as e:
        logger.error(f"Error analyzing email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze email: {str(e)}"
        )


# ============================================================================
# GMAIL CONFIGURATION ENDPOINTS
# ============================================================================

@router.post("/gmail/connect")
async def connect_gmail(request: GmailConnectRequest):
    """
    Connect Gmail account via OAuth
    
    Args:
        request: Gmail OAuth credentials
        
    Returns:
        Connection status
    """
    try:
        with db_session() as session:
            # Get or create config
            config = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.user_id == request.user_id
            ).first()
            
            if not config:
                config = ErikaEmailConfig(user_id=request.user_id)
                session.add(config)
            
            # Update credentials
            config.gmail_client_id = request.client_id
            config.gmail_client_secret = request.client_secret
            config.gmail_enabled = True
            
            session.commit()
            
            # Test connection
            gmail_service = ErikaGmailService(
                client_id=request.client_id,
                client_secret=request.client_secret,
                user_id=request.user_id
            )
            
            # Validate credentials (this will trigger OAuth flow if needed)
            try:
                gmail_service.validate_credentials()
            except GmailAuthenticationError as e:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": f"Gmail authentication failed: {str(e)}",
                        "message": "Please complete OAuth flow manually"
                    }
                )
            
            return JSONResponse(content={
                "success": True,
                "message": "Gmail connected successfully",
                "user_id": request.user_id
            })
            
    except Exception as e:
        logger.error(f"Error connecting Gmail: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect Gmail: {str(e)}"
        )


@router.get("/gmail/status")
async def get_gmail_status():
    """Get Gmail connection status"""
    try:
        with db_session() as session:
            config = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.user_id == "default"
            ).first()
            
            if not config:
                return JSONResponse(content={
                    "success": True,
                    "connected": False,
                    "message": "Gmail not configured"
                })
            
            return JSONResponse(content={
                "success": True,
                "connected": config.gmail_enabled,
                "user_id": config.user_id,
                "check_interval": config.gmail_check_interval,
                "keywords": config.gmail_keywords or []
            })
            
    except Exception as e:
        logger.error(f"Error getting Gmail status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Gmail status: {str(e)}"
        )


@router.post("/gmail/disconnect")
async def disconnect_gmail():
    """Disconnect Gmail account"""
    try:
        with db_session() as session:
            config = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.user_id == "default"
            ).first()
            
            if config:
                config.gmail_enabled = False
                session.commit()
            
            return JSONResponse(content={
                "success": True,
                "message": "Gmail disconnected"
            })
            
    except Exception as e:
        logger.error(f"Error disconnecting Gmail: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect Gmail: {str(e)}"
        )


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@router.get("/stats")
async def get_stats():
    """Get Erika statistics"""
    try:
        with db_session() as session:
            # Count emails analyzed
            email_count = session.query(ErikaEmailAnalysis).count()
            
            # Count active configs
            config_count = session.query(ErikaEmailConfig).filter(
                ErikaEmailConfig.gmail_enabled == True
            ).count()
            
            return JSONResponse(content={
                "success": True,
                "stats": {
                    "emails_analyzed": email_count,
                    "active_configs": config_count
                }
            })
            
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )

