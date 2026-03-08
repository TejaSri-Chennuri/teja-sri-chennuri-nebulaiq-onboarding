"""
Zentra AI - Notification Service

Handles sending notifications via email, SMS, WhatsApp, push, and voice.
"""
import logging
from typing import Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Multi-channel notification delivery service."""

    def __init__(self):
        self._init_sendgrid()
        self._init_twilio()
        self._init_firebase()

    def _init_sendgrid(self):
        self.sendgrid_client = None
        if settings.SENDGRID_API_KEY:
            try:
                from sendgrid import SendGridAPIClient
                self.sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
                logger.info("SendGrid initialized")
            except Exception as e:
                logger.warning(f"SendGrid not available: {e}")

    def _init_twilio(self):
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                logger.info("Twilio initialized")
            except Exception as e:
                logger.warning(f"Twilio not available: {e}")

    def _init_firebase(self):
        self.firebase_app = None
        if settings.FIREBASE_CREDENTIALS_PATH:
            try:
                import firebase_admin
                from firebase_admin import credentials
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                self.firebase_app = firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized")
            except Exception as e:
                logger.warning(f"Firebase not available: {e}")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send email via SendGrid."""
        if not self.sendgrid_client:
            logger.info(f"[EMAIL MOCK] To: {to_email} | Subject: {subject}")
            return True

        try:
            from sendgrid.helpers.mail import Mail
            message = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
            )
            self.sendgrid_client.send(message)
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS via Twilio."""
        if not self.twilio_client:
            logger.info(f"[SMS MOCK] To: {to_phone} | Message: {message}")
            return True

        try:
            self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone,
            )
            logger.info(f"SMS sent to {to_phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {e}")
            return False

    def send_whatsapp(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp message via Twilio."""
        if not self.twilio_client:
            logger.info(f"[WHATSAPP MOCK] To: {to_phone} | Message: {message}")
            return True

        try:
            self.twilio_client.messages.create(
                body=message,
                from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                to=f"whatsapp:{to_phone}",
            )
            logger.info(f"WhatsApp message sent to {to_phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {to_phone}: {e}")
            return False

    def send_push_notification(
        self, device_token: str, title: str, body: str, data: Optional[dict] = None
    ) -> bool:
        """Send push notification via Firebase."""
        if not self.firebase_app:
            logger.info(f"[PUSH MOCK] Token: {device_token[:20]}... | Title: {title}")
            return True

        try:
            from firebase_admin import messaging
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                token=device_token,
            )
            messaging.send(message)
            logger.info(f"Push notification sent to {device_token[:20]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False

    def send_renewal_reminder(
        self,
        user_email: str,
        user_name: str,
        service_name: str,
        amount: float,
        currency: str,
        renewal_date: str,
        phone: Optional[str] = None,
    ) -> None:
        """Send renewal reminder across all configured channels."""
        # Email
        subject = f"🔔 {service_name} renews soon - Zentra AI"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #6366f1;">Zentra AI - Renewal Reminder</h2>
            <p>Hi {user_name},</p>
            <p>Your <strong>{service_name}</strong> subscription is due to renew on 
               <strong>{renewal_date}</strong>.</p>
            <p style="font-size: 24px; color: #6366f1;">
                Amount: {currency} {amount:,.0f}
            </p>
            <p>Review your subscription in the 
               <a href="{settings.FRONTEND_URL}/dashboard">Zentra AI Dashboard</a>.</p>
            <p style="color: #9ca3af; font-size: 12px;">
                Manage your preferences at {settings.FRONTEND_URL}/settings
            </p>
        </div>
        """
        self.send_email(user_email, subject, html)

        # SMS
        if phone:
            sms_msg = (
                f"Zentra AI: {service_name} renews on {renewal_date} for "
                f"{currency} {amount:,.0f}. Manage at {settings.FRONTEND_URL}"
            )
            self.send_sms(phone, sms_msg)

    def send_spending_insight(
        self,
        user_email: str,
        user_name: str,
        total_monthly: float,
        currency: str,
        insights: list,
    ) -> None:
        """Send monthly spending insight email."""
        insights_html = "".join(f"<li>{insight}</li>" for insight in insights)
        subject = "📊 Your Monthly Subscription Spending - Zentra AI"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #6366f1;">Monthly Spending Insights</h2>
            <p>Hi {user_name},</p>
            <p>Here's your subscription spending summary:</p>
            <p style="font-size: 28px; font-weight: bold; color: #6366f1;">
                {currency} {total_monthly:,.0f}/month
            </p>
            <ul style="line-height: 2;">{insights_html}</ul>
            <p>
                <a href="{settings.FRONTEND_URL}/analytics" 
                   style="background: #6366f1; color: white; padding: 10px 20px; 
                          border-radius: 6px; text-decoration: none;">
                    View Full Analytics
                </a>
            </p>
        </div>
        """
        self.send_email(user_email, subject, html)


notification_service = NotificationService()
