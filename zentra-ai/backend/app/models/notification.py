import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class NotificationType(str, enum.Enum):
    RENEWAL_REMINDER = "renewal_reminder"
    PAYMENT_DETECTED = "payment_detected"
    UNUSED_SERVICE = "unused_service"
    PRICE_INCREASE = "price_increase"
    RECOMMENDATION = "recommendation"
    SPENDING_ALERT = "spending_alert"
    DUPLICATE_DETECTED = "duplicate_detected"
    TRIAL_ENDING = "trial_ending"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    IN_APP = "in_app"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)

    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(SAEnum(NotificationType), nullable=False)
    channel = Column(SAEnum(NotificationChannel), default=NotificationChannel.IN_APP)

    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)

    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    whatsapp_enabled = Column(Boolean, default=False)
    voice_enabled = Column(Boolean, default=False)

    renewal_reminders = Column(Boolean, default=True)
    payment_alerts = Column(Boolean, default=True)
    unused_service_alerts = Column(Boolean, default=True)
    spending_alerts = Column(Boolean, default=True)
    recommendation_alerts = Column(Boolean, default=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notification_preferences")
