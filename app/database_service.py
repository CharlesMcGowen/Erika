#!/usr/bin/env python3
"""
Erika Database Service
======================

Standalone database service for Erika using the erika library.

Author: EGO Revolution Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

# Import from erika library
from erika.database import db_session, init_db, DATABASE_URL
from erika.models import ErikaEmailConfig

logger = logging.getLogger(__name__)


class ErikaDatabaseService:
    """Database service for Erika's email management data"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize database connection
        
        Args:
            database_url: PostgreSQL connection string (optional, uses DATABASE_URL env var)
        """
        if database_url:
            os.environ['DATABASE_URL'] = database_url
        
        # Initialize database tables if needed
        try:
            init_db()
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.warning(f"⚠️ Database initialization warning: {e}")
        
        self.connected = True
    
    def get_email_stats(self) -> Dict[str, Any]:
        """Get email analysis statistics"""
        try:
            from erika.models import ErikaEmailAnalysis
            
            with db_session() as session:
                # Total emails
                total = session.query(ErikaEmailAnalysis).count()
                
                # By category
                from sqlalchemy import func
                category_counts = session.query(
                    ErikaEmailAnalysis.category,
                    func.count(ErikaEmailAnalysis.id)
                ).group_by(ErikaEmailAnalysis.category).all()
                by_category = {cat: count for cat, count in category_counts}
                
                # By sentiment
                sentiment_counts = session.query(
                    ErikaEmailAnalysis.sentiment,
                    func.count(ErikaEmailAnalysis.id)
                ).group_by(ErikaEmailAnalysis.sentiment).all()
                by_sentiment = {sent: count for sent, count in sentiment_counts}
                
                # High priority
                high_priority = session.query(ErikaEmailAnalysis).filter(
                    (ErikaEmailAnalysis.is_important == True) |
                    (ErikaEmailAnalysis.requires_response == True)
                ).count()
                
                return {
                    'total': total,
                    'by_category': by_category,
                    'by_sentiment': by_sentiment,
                    'high_priority': high_priority
                }
        except Exception as e:
            logger.error(f"Error getting email stats: {e}")
            return {'total': 0, 'by_category': {}, 'by_sentiment': {}, 'high_priority': 0}
    
    def get_recent_emails(self, limit: int = 10, offset: int = 0,
                         category_filter: Optional[str] = None,
                         sentiment_filter: Optional[str] = None,
                         search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent email analyses with optional filtering"""
        try:
            from erika.models import ErikaEmailAnalysis
            from sqlalchemy import or_
            
            with db_session() as session:
                query = session.query(ErikaEmailAnalysis)
                
                if category_filter:
                    query = query.filter(ErikaEmailAnalysis.category == category_filter)
                
                if sentiment_filter:
                    query = query.filter(ErikaEmailAnalysis.sentiment == sentiment_filter)
                
                if search_query:
                    search = f"%{search_query}%"
                    query = query.filter(
                        or_(
                            ErikaEmailAnalysis.subject.ilike(search),
                            ErikaEmailAnalysis.sender.ilike(search),
                            ErikaEmailAnalysis.body.ilike(search)
                        )
                    )
                
                emails = query.order_by(
                    ErikaEmailAnalysis.received_date.desc()
                ).offset(offset).limit(limit).all()
                
                result = []
                for email in emails:
                    result.append({
                        'id': str(email.id),
                        'subject': email.subject or 'No subject',
                        'sender': email.sender or 'Unknown',
                        'category': email.category or 'other',
                        'sentiment': email.sentiment or 'neutral',
                        'is_important': email.is_important or False,
                        'requires_response': email.requires_response or False,
                        'malicious_confidence_score': getattr(email, 'fraud_score', 0.0) or 0.0,
                        'body': email.body or '',
                        'received_date': email.received_date.isoformat() if email.received_date else None
                    })
                return result
        except Exception as e:
            logger.error(f"Error getting recent emails: {e}")
            return []
    
    def get_email_count(self, category_filter: Optional[str] = None,
                       sentiment_filter: Optional[str] = None,
                       search_query: Optional[str] = None) -> int:
        """Get total email count with optional filtering"""
        try:
            from erika.models import ErikaEmailAnalysis
            from sqlalchemy import or_
            
            with db_session() as session:
                query = session.query(ErikaEmailAnalysis)
                
                if category_filter:
                    query = query.filter(ErikaEmailAnalysis.category == category_filter)
                
                if sentiment_filter:
                    query = query.filter(ErikaEmailAnalysis.sentiment == sentiment_filter)
                
                if search_query:
                    search = f"%{search_query}%"
                    query = query.filter(
                        or_(
                            ErikaEmailAnalysis.subject.ilike(search),
                            ErikaEmailAnalysis.sender.ilike(search),
                            ErikaEmailAnalysis.body.ilike(search)
                        )
                    )
                
                return query.count()
        except Exception as e:
            logger.error(f"Error getting email count: {e}")
            return 0
    
    def get_email_config(self, user_id: str = "default") -> Optional[Dict[str, Any]]:
        """Get email configuration for user"""
        try:
            with db_session() as session:
                config = session.query(ErikaEmailConfig).filter(
                    ErikaEmailConfig.user_id == user_id
                ).first()
                
                if config:
                    return {
                        'id': str(config.id),
                        'gmail_client_id': config.gmail_client_id or '',
                        'gmail_client_secret': config.gmail_client_secret or '',
                        'gmail_enabled': config.gmail_enabled or False,
                        'gmail_check_interval': config.gmail_check_interval or 300,
                        'gmail_keywords': config.gmail_keywords or [],
                        'phishing_detection_enabled': getattr(config, 'phishing_detection_enabled', True),
                        'reverse_image_search_enabled': getattr(config, 'reverse_image_search_enabled', True),
                        'enable_ares_bridge': getattr(config, 'enable_ares_bridge', False),
                        'auto_mitigate_threats': getattr(config, 'auto_mitigate_threats', False),
                        'threat_mitigation_threshold': getattr(config, 'threat_mitigation_threshold', 80),
                        'is_active': config.is_active or True,
                        'last_modified': config.last_modified.isoformat() if config.last_modified else None
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting email config: {e}")
            return None
    
    def update_email_config(self, user_id: str = "default", **kwargs) -> bool:
        """Update email configuration for user"""
        try:
            with db_session() as session:
                config = session.query(ErikaEmailConfig).filter(
                    ErikaEmailConfig.user_id == user_id
                ).first()
                
                if not config:
                    config = ErikaEmailConfig(user_id=user_id)
                    session.add(config)
                
                # Update provided fields
                for key, value in kwargs.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                
                config.last_modified = datetime.utcnow()
                
                logger.info(f"✅ Updated email config for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error updating email config: {e}")
            return False
    
    def get_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Get email by ID"""
        try:
            from erika.models import ErikaEmailAnalysis
            import uuid
            
            with db_session() as session:
                email = session.query(ErikaEmailAnalysis).filter(
                    ErikaEmailAnalysis.id == uuid.UUID(email_id)
                ).first()
                
                if email:
                    return {
                        'id': str(email.id),
                        'subject': email.subject,
                        'sender': email.sender,
                        'recipient': email.recipient,
                        'body': email.body,
                        'content': email.content,
                        'category': email.category,
                        'sentiment': email.sentiment,
                        'is_important': email.is_important,
                        'requires_response': email.requires_response,
                        'priority': email.priority,
                        'harmony_score': email.harmony_score,
                        'nlp_quality_score': email.nlp_quality_score,
                        'received_date': email.received_date.isoformat() if email.received_date else None,
                        'analyzed_at': email.analyzed_at.isoformat() if email.analyzed_at else None
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting email by id: {e}")
            return None
    
    def update_email(self, email_id: str, **kwargs) -> bool:
        """Update email fields"""
        try:
            from erika.models import ErikaEmailAnalysis
            import uuid
            
            with db_session() as session:
                email = session.query(ErikaEmailAnalysis).filter(
                    ErikaEmailAnalysis.id == uuid.UUID(email_id)
                ).first()
                
                if not email:
                    return False
                
                # Update provided fields
                for key, value in kwargs.items():
                    if hasattr(email, key):
                        setattr(email, key, value)
                
                return True
        except Exception as e:
            logger.error(f"Error updating email: {e}")
            return False

