"""
Zentra AI - Subscription Detection Engine

Uses pattern recognition and NLP to detect subscriptions from:
- Gmail email content
- Bank transaction descriptions
- SMS messages
"""
import re
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


# Known subscription merchants and their metadata
KNOWN_MERCHANTS: Dict[str, Dict] = {
    "netflix": {
        "name": "Netflix",
        "category": "streaming",
        "logo": "https://logo.clearbit.com/netflix.com",
        "website": "https://netflix.com",
        "typical_amounts_inr": [149, 199, 499, 649, 799],
    },
    "spotify": {
        "name": "Spotify",
        "category": "music",
        "logo": "https://logo.clearbit.com/spotify.com",
        "website": "https://spotify.com",
        "typical_amounts_inr": [119, 179, 299],
    },
    "amazon prime": {
        "name": "Amazon Prime",
        "category": "streaming",
        "logo": "https://logo.clearbit.com/amazon.com",
        "website": "https://amazon.com",
        "typical_amounts_inr": [179, 299, 1499],
    },
    "hotstar": {
        "name": "Disney+ Hotstar",
        "category": "streaming",
        "logo": "https://logo.clearbit.com/hotstar.com",
        "website": "https://hotstar.com",
        "typical_amounts_inr": [299, 499, 899, 1499],
    },
    "youtube premium": {
        "name": "YouTube Premium",
        "category": "streaming",
        "logo": "https://logo.clearbit.com/youtube.com",
        "website": "https://youtube.com",
        "typical_amounts_inr": [129, 189],
    },
    "apple music": {
        "name": "Apple Music",
        "category": "music",
        "logo": "https://logo.clearbit.com/apple.com",
        "website": "https://apple.com",
        "typical_amounts_inr": [99, 149],
    },
    "google one": {
        "name": "Google One",
        "category": "cloud_storage",
        "logo": "https://logo.clearbit.com/google.com",
        "website": "https://one.google.com",
        "typical_amounts_inr": [130, 210, 650],
    },
    "dropbox": {
        "name": "Dropbox",
        "category": "cloud_storage",
        "logo": "https://logo.clearbit.com/dropbox.com",
        "website": "https://dropbox.com",
        "typical_amounts_inr": [125, 1250],
    },
    "microsoft 365": {
        "name": "Microsoft 365",
        "category": "productivity",
        "logo": "https://logo.clearbit.com/microsoft.com",
        "website": "https://microsoft.com",
        "typical_amounts_inr": [420, 3699],
    },
    "notion": {
        "name": "Notion",
        "category": "productivity",
        "logo": "https://logo.clearbit.com/notion.so",
        "website": "https://notion.so",
        "typical_amounts_inr": [0, 800, 1600],
    },
    "zoom": {
        "name": "Zoom",
        "category": "communication",
        "logo": "https://logo.clearbit.com/zoom.us",
        "website": "https://zoom.us",
        "typical_amounts_inr": [0, 1300, 1800],
    },
    "slack": {
        "name": "Slack",
        "category": "communication",
        "logo": "https://logo.clearbit.com/slack.com",
        "website": "https://slack.com",
        "typical_amounts_inr": [0, 600, 1000],
    },
    "github": {
        "name": "GitHub",
        "category": "productivity",
        "logo": "https://logo.clearbit.com/github.com",
        "website": "https://github.com",
        "typical_amounts_inr": [0, 330, 825],
    },
    "zomato pro": {
        "name": "Zomato Pro",
        "category": "food",
        "logo": "https://logo.clearbit.com/zomato.com",
        "website": "https://zomato.com",
        "typical_amounts_inr": [149, 299],
    },
    "swiggy one": {
        "name": "Swiggy One",
        "category": "food",
        "logo": "https://logo.clearbit.com/swiggy.com",
        "website": "https://swiggy.com",
        "typical_amounts_inr": [149, 299],
    },
    "myntra insider": {
        "name": "Myntra Insider",
        "category": "shopping",
        "logo": "https://logo.clearbit.com/myntra.com",
        "website": "https://myntra.com",
        "typical_amounts_inr": [0, 399],
    },
    "coursera plus": {
        "name": "Coursera Plus",
        "category": "education",
        "logo": "https://logo.clearbit.com/coursera.org",
        "website": "https://coursera.org",
        "typical_amounts_inr": [2400, 5699],
    },
    "duolingo": {
        "name": "Duolingo Plus",
        "category": "education",
        "logo": "https://logo.clearbit.com/duolingo.com",
        "website": "https://duolingo.com",
        "typical_amounts_inr": [435, 2939],
    },
    "nordvpn": {
        "name": "NordVPN",
        "category": "security",
        "logo": "https://logo.clearbit.com/nordvpn.com",
        "website": "https://nordvpn.com",
        "typical_amounts_inr": [270, 540],
    },
}


# Subscription-related email/SMS keywords
SUBSCRIPTION_KEYWORDS = [
    "subscription", "renewal", "renewed", "billing", "charged", "recurring",
    "monthly plan", "annual plan", "membership", "premium", "pro plan",
    "invoice", "receipt", "payment successful", "auto-renewed", "auto-debit",
    "standing instruction", "emi", "subscription fee", "plan activated",
    "trial ended", "free trial", "upgrade", "downgrade",
]

AMOUNT_PATTERNS = [
    r"(?:₹|inr|rs\.?)\s*([0-9,]+(?:\.[0-9]{1,2})?)",
    r"\$\s*([0-9,]+(?:\.[0-9]{1,2})?)",
    r"([0-9,]+(?:\.[0-9]{1,2})?)\s*(?:₹|inr|rs\.?)",
    r"amount[:\s]+(?:₹|inr|rs\.?)?\s*([0-9,]+(?:\.[0-9]{1,2})?)",
]

DATE_PATTERNS = [
    r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    r"(\d{4}-\d{2}-\d{2})",
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2},?\s+\d{4})",
]

BILLING_CYCLE_PATTERNS = {
    "monthly": [r"\bmonthly\b", r"\bper month\b", r"\bm\/m\b", r"\b\/mo\b"],
    "annual": [r"\bannual\b", r"\byearly\b", r"\bper year\b", r"\b\/yr\b", r"\b\/year\b"],
    "quarterly": [r"\bquarterly\b", r"\bper quarter\b"],
    "weekly": [r"\bweekly\b", r"\bper week\b"],
}


@dataclass
class DetectedSubscription:
    merchant: str
    name: str
    amount: float
    currency: str
    billing_cycle: str
    category: str
    confidence: float
    source: str
    next_billing_date: Optional[date] = None
    last_billed_date: Optional[date] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    raw_text: str = ""
    detection_source_id: str = ""
    notes: str = ""


class SubscriptionDetector:
    """AI-powered subscription detection from various data sources."""

    def __init__(self):
        self.merchant_patterns = self._build_merchant_patterns()

    def _build_merchant_patterns(self) -> List[Tuple[re.Pattern, str]]:
        """Build regex patterns for known merchants."""
        patterns = []
        for key, info in KNOWN_MERCHANTS.items():
            pattern = re.compile(re.escape(key), re.IGNORECASE)
            patterns.append((pattern, key))
        return patterns

    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount from text."""
        for pattern in AMOUNT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(",", "")
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return None

    def _extract_currency(self, text: str) -> str:
        """Extract currency from text."""
        if re.search(r"₹|inr|rs\.?", text, re.IGNORECASE):
            return "INR"
        if re.search(r"\$|usd|dollar", text, re.IGNORECASE):
            return "USD"
        return "INR"

    def _extract_billing_cycle(self, text: str) -> str:
        """Extract billing cycle from text."""
        text_lower = text.lower()
        for cycle, patterns in BILLING_CYCLE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return cycle
        return "monthly"

    def _extract_dates(self, text: str) -> List[date]:
        """Extract dates from text."""
        dates = []
        for pattern in DATE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                        try:
                            d = datetime.strptime(match, fmt).date()
                            dates.append(d)
                            break
                        except ValueError:
                            continue
                except Exception:
                    continue
        return dates

    def _is_subscription_related(self, text: str) -> Tuple[bool, float]:
        """Check if text is subscription-related and return confidence."""
        text_lower = text.lower()
        keyword_count = sum(1 for kw in SUBSCRIPTION_KEYWORDS if kw in text_lower)
        if keyword_count == 0:
            return False, 0.0
        confidence = min(0.5 + (keyword_count * 0.1), 1.0)
        return True, confidence

    def _detect_merchant(self, text: str) -> Optional[Tuple[str, Dict, float]]:
        """Detect merchant from text. Returns (merchant_key, info, confidence)."""
        text_lower = text.lower()
        for pattern, merchant_key in self.merchant_patterns:
            if pattern.search(text_lower):
                info = KNOWN_MERCHANTS[merchant_key]
                confidence = 0.9
                return merchant_key, info, confidence

        # Fallback: try to find capitalized service names
        matches = re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b", text)
        for match in matches:
            if len(match) > 3:
                return match.lower(), {
                    "name": match,
                    "category": "other",
                    "logo": None,
                    "website": None,
                }, 0.6
        return None

    def detect_from_email(self, email_subject: str, email_body: str, email_id: str = "") -> Optional[DetectedSubscription]:
        """Detect subscription from email content."""
        combined_text = f"{email_subject} {email_body}"

        is_sub, keyword_confidence = self._is_subscription_related(combined_text)
        if not is_sub:
            return None

        merchant_result = self._detect_merchant(combined_text)
        if not merchant_result:
            return None

        merchant_key, merchant_info, merchant_confidence = merchant_result
        amount = self._extract_amount(combined_text)
        if amount is None:
            return None

        currency = self._extract_currency(combined_text)
        billing_cycle = self._extract_billing_cycle(combined_text)
        dates = self._extract_dates(combined_text)

        next_billing_date = None
        last_billed_date = None
        if dates:
            today = date.today()
            future_dates = [d for d in dates if d >= today]
            past_dates = [d for d in dates if d < today]
            if future_dates:
                next_billing_date = min(future_dates)
            if past_dates:
                last_billed_date = max(past_dates)

        confidence = (keyword_confidence + merchant_confidence) / 2

        return DetectedSubscription(
            merchant=merchant_info["name"],
            name=merchant_info["name"],
            amount=amount,
            currency=currency,
            billing_cycle=billing_cycle,
            category=merchant_info.get("category", "other"),
            confidence=confidence,
            source="email",
            next_billing_date=next_billing_date,
            last_billed_date=last_billed_date,
            logo_url=merchant_info.get("logo"),
            website_url=merchant_info.get("website"),
            raw_text=combined_text[:1000],
            detection_source_id=email_id,
            notes=f"Detected from email: {email_subject[:100]}",
        )

    def detect_from_transaction(self, description: str, amount: float, txn_date: date, txn_id: str = "") -> Optional[DetectedSubscription]:
        """Detect subscription from bank/card transaction."""
        desc_lower = description.lower()

        # Skip non-subscription transactions
        skip_keywords = ["atm", "cash", "fuel", "petrol", "grocery", "restaurant"]
        if any(kw in desc_lower for kw in skip_keywords):
            return None

        merchant_result = self._detect_merchant(description)
        if not merchant_result:
            # Try pattern matching for recurring transactions
            is_sub, confidence = self._is_subscription_related(description)
            if not is_sub or confidence < 0.6:
                return None
            merchant_key = description.strip()[:50]
            merchant_info = {"name": description.strip()[:50], "category": "other", "logo": None, "website": None}
            merchant_confidence = confidence
        else:
            merchant_key, merchant_info, merchant_confidence = merchant_result

        currency = self._extract_currency(description)
        billing_cycle = self._extract_billing_cycle(description)

        # Estimate next billing date
        next_billing_date = None
        if billing_cycle == "monthly":
            next_billing_date = txn_date.replace(day=txn_date.day)
            # Add one month
            if txn_date.month == 12:
                next_billing_date = txn_date.replace(year=txn_date.year + 1, month=1)
            else:
                next_billing_date = txn_date.replace(month=txn_date.month + 1)
        elif billing_cycle == "annual":
            next_billing_date = txn_date.replace(year=txn_date.year + 1)

        return DetectedSubscription(
            merchant=merchant_info["name"],
            name=merchant_info["name"],
            amount=amount,
            currency=currency,
            billing_cycle=billing_cycle,
            category=merchant_info.get("category", "other"),
            confidence=merchant_confidence,
            source="bank",
            next_billing_date=next_billing_date,
            last_billed_date=txn_date,
            logo_url=merchant_info.get("logo"),
            website_url=merchant_info.get("website"),
            raw_text=description,
            detection_source_id=txn_id,
            notes=f"Detected from bank transaction on {txn_date}",
        )

    def detect_from_sms(self, sms_text: str, sms_id: str = "") -> Optional[DetectedSubscription]:
        """Detect subscription from SMS."""
        is_sub, confidence = self._is_subscription_related(sms_text)
        if not is_sub:
            return None

        merchant_result = self._detect_merchant(sms_text)
        amount = self._extract_amount(sms_text)

        if amount is None:
            return None

        if merchant_result:
            merchant_key, merchant_info, merchant_confidence = merchant_result
        else:
            merchant_info = {"name": "Unknown Service", "category": "other", "logo": None, "website": None}
            merchant_confidence = 0.5

        currency = self._extract_currency(sms_text)
        billing_cycle = self._extract_billing_cycle(sms_text)
        dates = self._extract_dates(sms_text)

        return DetectedSubscription(
            merchant=merchant_info["name"],
            name=merchant_info["name"],
            amount=amount,
            currency=currency,
            billing_cycle=billing_cycle,
            category=merchant_info.get("category", "other"),
            confidence=min(confidence, merchant_confidence),
            source="sms",
            next_billing_date=dates[0] if dates else None,
            logo_url=merchant_info.get("logo"),
            website_url=merchant_info.get("website"),
            raw_text=sms_text[:500],
            detection_source_id=sms_id,
            notes="Detected from SMS notification",
        )

    def find_duplicates(self, subscriptions: List[Dict]) -> List[Tuple[str, str, str]]:
        """Find duplicate/overlapping subscriptions. Returns list of (id1, id2, reason)."""
        duplicates = []
        categories_seen: Dict[str, List] = {}

        # Group by category
        for sub in subscriptions:
            cat = sub.get("category", "other")
            if cat not in categories_seen:
                categories_seen[cat] = []
            categories_seen[cat].append(sub)

        # Check for duplicates within same category
        duplicate_categories = ["streaming", "music", "cloud_storage", "security"]
        for cat in duplicate_categories:
            subs = categories_seen.get(cat, [])
            if len(subs) > 1:
                for i in range(len(subs)):
                    for j in range(i + 1, len(subs)):
                        duplicates.append((
                            str(subs[i]["id"]),
                            str(subs[j]["id"]),
                            f"Both are {cat} services - consider if you need both",
                        ))

        return duplicates
