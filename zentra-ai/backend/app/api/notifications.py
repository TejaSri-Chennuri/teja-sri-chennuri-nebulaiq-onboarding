"""
Zentra AI - Notifications API
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.notification import Notification, NotificationPreference, NotificationType, NotificationChannel
from app.services.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    notification_type: str
    channel: str
    is_read: bool
    is_sent: bool
    created_at: datetime
    subscription_id: Optional[str]

    class Config:
        from_attributes = True


class NotificationPreferenceResponse(BaseModel):
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    whatsapp_enabled: bool
    voice_enabled: bool
    renewal_reminders: bool
    payment_alerts: bool
    unused_service_alerts: bool
    spending_alerts: bool
    recommendation_alerts: bool


class UpdatePreferencesRequest(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    voice_enabled: Optional[bool] = None
    renewal_reminders: Optional[bool] = None
    payment_alerts: Optional[bool] = None
    unused_service_alerts: Optional[bool] = None
    spending_alerts: Optional[bool] = None
    recommendation_alerts: Optional[bool] = None


def _to_response(notif: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=str(notif.id),
        title=notif.title,
        message=notif.message,
        notification_type=notif.notification_type.value if notif.notification_type else "renewal_reminder",
        channel=notif.channel.value if notif.channel else "in_app",
        is_read=notif.is_read,
        is_sent=notif.is_sent,
        created_at=notif.created_at,
        subscription_id=str(notif.subscription_id) if notif.subscription_id else None,
    )


@router.get("", response_model=List[NotificationResponse])
def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user notifications."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    return [_to_response(n) for n in notifications]


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get count of unread notifications."""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()
    return {"unread_count": count}


@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    notif.read_at = datetime.utcnow()
    db.commit()
    return {"message": "Marked as read"}


@router.put("/mark-all-read")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    return {"message": "All notifications marked as read"}


@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get notification preferences."""
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    if not prefs:
        prefs = NotificationPreference(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)

    return NotificationPreferenceResponse(
        email_enabled=prefs.email_enabled,
        sms_enabled=prefs.sms_enabled,
        push_enabled=prefs.push_enabled,
        whatsapp_enabled=prefs.whatsapp_enabled,
        voice_enabled=prefs.voice_enabled,
        renewal_reminders=prefs.renewal_reminders,
        payment_alerts=prefs.payment_alerts,
        unused_service_alerts=prefs.unused_service_alerts,
        spending_alerts=prefs.spending_alerts,
        recommendation_alerts=prefs.recommendation_alerts,
    )


@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update notification preferences."""
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    if not prefs:
        prefs = NotificationPreference(user_id=current_user.id)
        db.add(prefs)

    fields = request.dict(exclude_none=True)
    for field, value in fields.items():
        setattr(prefs, field, value)

    db.commit()
    db.refresh(prefs)

    return NotificationPreferenceResponse(
        email_enabled=prefs.email_enabled,
        sms_enabled=prefs.sms_enabled,
        push_enabled=prefs.push_enabled,
        whatsapp_enabled=prefs.whatsapp_enabled,
        voice_enabled=prefs.voice_enabled,
        renewal_reminders=prefs.renewal_reminders,
        payment_alerts=prefs.payment_alerts,
        unused_service_alerts=prefs.unused_service_alerts,
        spending_alerts=prefs.spending_alerts,
        recommendation_alerts=prefs.recommendation_alerts,
    )
