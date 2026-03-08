"""
Zentra AI - Gmail Scanner Service

Scans user Gmail for subscription-related emails using Gmail API.
"""
import logging
import base64
from typing import List, Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class GmailScanner:
    """Scans Gmail inbox for subscription-related emails."""

    SUBSCRIPTION_SEARCH_QUERY = (
        "subject:(subscription OR renewal OR invoice OR receipt OR billing OR "
        "\"payment successful\" OR \"auto-renewed\" OR \"order confirmation\") "
        "newer_than:90d"
    )

    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.service = None

    def _build_service(self):
        """Build Gmail API service."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials(
                token=self.access_token,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GMAIL_CLIENT_ID,
                client_secret=settings.GMAIL_CLIENT_SECRET,
            )
            self.service = build("gmail", "v1", credentials=creds)
            return True
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            return False

    def _decode_body(self, payload: dict) -> str:
        """Decode email body from Gmail API payload."""
        body = ""
        if "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        elif "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    body += base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                elif part.get("mimeType") == "text/html" and not body:
                    html = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                    # Strip basic HTML tags
                    import re
                    body += re.sub(r"<[^>]+>", " ", html)
        return body[:5000]

    def scan_emails(self, max_results: int = 100) -> List[Dict]:
        """Scan Gmail for subscription emails. Returns list of email data."""
        if not self._build_service():
            logger.warning("Gmail service unavailable, returning mock data")
            return self._mock_emails()

        try:
            results = self.service.users().messages().list(
                userId="me",
                q=self.SUBSCRIPTION_SEARCH_QUERY,
                maxResults=max_results,
            ).execute()

            messages = results.get("messages", [])
            emails = []

            for msg in messages:
                try:
                    full_msg = self.service.users().messages().get(
                        userId="me",
                        id=msg["id"],
                        format="full",
                    ).execute()

                    headers = {
                        h["name"].lower(): h["value"]
                        for h in full_msg.get("payload", {}).get("headers", [])
                    }

                    subject = headers.get("subject", "")
                    sender = headers.get("from", "")
                    body = self._decode_body(full_msg.get("payload", {}))

                    emails.append({
                        "id": msg["id"],
                        "subject": subject,
                        "sender": sender,
                        "body": body,
                        "date": headers.get("date", ""),
                    })
                except Exception as e:
                    logger.warning(f"Failed to fetch email {msg['id']}: {e}")

            logger.info(f"Scanned {len(emails)} subscription-related emails")
            return emails

        except Exception as e:
            logger.error(f"Gmail scan failed: {e}")
            return []

    def _mock_emails(self) -> List[Dict]:
        """Return mock emails for testing/demo."""
        return [
            {
                "id": "mock_001",
                "subject": "Netflix Monthly Subscription Renewed - ₹649",
                "sender": "Netflix <info@netflix.com>",
                "body": "Your Netflix subscription has been renewed. Amount charged: ₹649. Next billing date: April 15, 2025.",
                "date": "Mon, 15 Mar 2025 10:00:00 +0530",
            },
            {
                "id": "mock_002",
                "subject": "Spotify Premium - Payment Successful",
                "sender": "Spotify <no-reply@spotify.com>",
                "body": "Your Spotify Premium subscription payment of ₹119 was successful. Monthly plan renewed.",
                "date": "Fri, 1 Mar 2025 09:00:00 +0530",
            },
            {
                "id": "mock_003",
                "subject": "Amazon Prime Membership Renewal",
                "sender": "Amazon <no-reply@amazon.in>",
                "body": "Your Amazon Prime annual membership has been renewed for ₹1499. Next renewal: March 1, 2026.",
                "date": "Sat, 1 Mar 2025 08:00:00 +0530",
            },
        ]
