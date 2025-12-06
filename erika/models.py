#!/usr/bin/env python3
"""
Erika SQLAlchemy Models
=======================

SQLAlchemy models for Gmail OAuth integration.

Author: Living Archive team
Version: 1.0.0
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, JSON,
    Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone as dt_timezone
import uuid
from typing import Optional

from .database import Base


class ErikaEmailConfig(Base):
    """
    Erika's Email Configuration for Gmail OAuth
    
    Stores OAuth credentials and settings per user.
    """
    __tablename__ = 'erika_email_config'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Gmail OAuth Integration
    gmail_client_id = Column(Text, nullable=True)  # OAuth2 client ID
    gmail_client_secret = Column(Text, nullable=True)  # OAuth2 client secret (encrypted in production)
    gmail_enabled = Column(Boolean, default=False)
    gmail_check_interval = Column(Integer, default=300)  # Check interval in seconds
    gmail_keywords = Column(JSON, default=list)  # Keywords for email filtering
    
    # Security Features
    phishing_detection_enabled = Column(Boolean, default=True)  # Enable reverse image search phishing detection
    reverse_image_search_enabled = Column(Boolean, default=True)  # Enable reverse image search (requires Selenium)
    enable_ares_bridge = Column(Boolean, default=False)  # Enable AresBridge threat detection
    auto_mitigate_threats = Column(Boolean, default=False)  # Automatically mitigate high-threat emails
    threat_mitigation_threshold = Column(Integer, default=80)  # Threat score threshold for auto-mitigation (0-100)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_modified = Column(DateTime(timezone=True), default=lambda: datetime.now(dt_timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(dt_timezone.utc))
    
    def __repr__(self):
        return f"<ErikaEmailConfig(user_id='{self.user_id}', gmail_enabled={self.gmail_enabled})>"
    
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
    )

