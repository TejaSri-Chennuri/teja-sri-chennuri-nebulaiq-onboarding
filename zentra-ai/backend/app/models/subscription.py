import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, Date, Text,
    Integer, ForeignKey, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class BillingCycle(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"


class SubscriptionSource(str, enum.Enum):
    EMAIL = "email"
    BANK = "bank"
    SMS = "sms"
    MANUAL = "manual"
    AI_DETECTED = "ai_detected"


class SubscriptionCategory(str, enum.Enum):
    STREAMING = "streaming"
    MUSIC = "music"
    PRODUCTIVITY = "productivity"
    CLOUD_STORAGE = "cloud_storage"
    FITNESS = "fitness"
    GAMING = "gaming"
    NEWS = "news"
    FOOD = "food"
    SHOPPING = "shopping"
    EDUCATION = "education"
    FINANCE = "finance"
    COMMUNICATION = "communication"
    SECURITY = "security"
    OTHER = "other"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    merchant = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    website_url = Column(Text, nullable=True)

    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    billing_cycle = Column(SAEnum(BillingCycle), default=BillingCycle.MONTHLY)
    status = Column(SAEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    category = Column(SAEnum(SubscriptionCategory), default=SubscriptionCategory.OTHER)
    source = Column(SAEnum(SubscriptionSource), default=SubscriptionSource.MANUAL)

    start_date = Column(Date, nullable=True)
    next_billing_date = Column(Date, nullable=True)
    last_billed_date = Column(Date, nullable=True)
    cancellation_date = Column(Date, nullable=True)

    # AI Analysis Fields
    usage_score = Column(Float, default=0.0)          # 0-100, how much user uses it
    ai_confidence = Column(Float, default=1.0)        # confidence of AI detection
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(UUID(as_uuid=True), nullable=True)
    ai_notes = Column(Text, nullable=True)

    # Detection metadata
    detection_source_id = Column(String(500), nullable=True)  # email id / txn id
    raw_data = Column(Text, nullable=True)                    # JSON string of source data

    notify_before_days = Column(Integer, default=3)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    usage_logs = relationship("SubscriptionUsage", back_populates="subscription", cascade="all, delete-orphan")


class SubscriptionUsage(Base):
    __tablename__ = "subscription_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False, index=True)

    logged_at = Column(DateTime, default=datetime.utcnow)
    usage_type = Column(String(100), default="session")  # session, login, api_call
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    subscription = relationship("Subscription", back_populates="usage_logs")
