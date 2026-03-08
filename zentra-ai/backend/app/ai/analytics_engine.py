"""
Zentra AI - Analytics Engine

Provides spending analytics, trend analysis, and forecasting.
"""
from datetime import date, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
import calendar


class AnalyticsEngine:
    """Computes spending analytics for users."""

    def _monthly_amount(self, amount: float, billing_cycle: str) -> float:
        """Convert any billing cycle to monthly equivalent."""
        if billing_cycle == "annual":
            return amount / 12
        if billing_cycle == "quarterly":
            return amount / 3
        if billing_cycle == "semi_annual":
            return amount / 6
        if billing_cycle == "weekly":
            return amount * 4.33
        if billing_cycle == "daily":
            return amount * 30
        return amount  # monthly

    def compute_summary(self, subscriptions: List[Dict]) -> Dict:
        """Compute overall spending summary."""
        active = [s for s in subscriptions if s.get("status") == "active"]
        paused = [s for s in subscriptions if s.get("status") == "paused"]
        cancelled = [s for s in subscriptions if s.get("status") == "cancelled"]
        trial = [s for s in subscriptions if s.get("status") == "trial"]

        total_monthly = sum(
            self._monthly_amount(s.get("amount", 0), s.get("billing_cycle", "monthly"))
            for s in active
        )

        total_annual = total_monthly * 12

        return {
            "active_count": len(active),
            "paused_count": len(paused),
            "cancelled_count": len(cancelled),
            "trial_count": len(trial),
            "total_count": len(subscriptions),
            "total_monthly_spend": round(total_monthly, 2),
            "total_annual_spend": round(total_annual, 2),
            "average_per_subscription": round(total_monthly / len(active), 2) if active else 0,
        }

    def compute_category_breakdown(self, subscriptions: List[Dict]) -> List[Dict]:
        """Break down spending by category."""
        active = [s for s in subscriptions if s.get("status") == "active"]
        category_data: Dict[str, Dict] = defaultdict(lambda: {"amount": 0.0, "count": 0, "services": []})

        for sub in active:
            cat = sub.get("category", "other")
            monthly = self._monthly_amount(sub.get("amount", 0), sub.get("billing_cycle", "monthly"))
            category_data[cat]["amount"] += monthly
            category_data[cat]["count"] += 1
            category_data[cat]["services"].append(sub.get("name", sub.get("merchant", "?")))

        total = sum(d["amount"] for d in category_data.values()) or 1

        result = [
            {
                "category": cat,
                "monthly_amount": round(data["amount"], 2),
                "count": data["count"],
                "percentage": round((data["amount"] / total) * 100, 1),
                "services": data["services"],
            }
            for cat, data in category_data.items()
        ]
        return sorted(result, key=lambda x: x["monthly_amount"], reverse=True)

    def compute_monthly_trend(
        self,
        subscriptions: List[Dict],
        months: int = 6,
    ) -> List[Dict]:
        """Compute monthly spending trend for the past N months."""
        today = date.today()
        trend = []

        for i in range(months - 1, -1, -1):
            # Go back i months
            target_month = today.month - i
            target_year = today.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1

            month_start = date(target_year, target_month, 1)
            month_end = date(target_year, target_month, calendar.monthrange(target_year, target_month)[1])

            # Which subscriptions were active during this month?
            active_in_month = []
            for sub in subscriptions:
                start = sub.get("start_date")
                if isinstance(start, str):
                    try:
                        start = date.fromisoformat(start)
                    except Exception:
                        start = None

                cancel = sub.get("cancellation_date")
                if isinstance(cancel, str):
                    try:
                        cancel = date.fromisoformat(cancel)
                    except Exception:
                        cancel = None

                if start and start > month_end:
                    continue
                if cancel and cancel < month_start:
                    continue
                active_in_month.append(sub)

            total = sum(
                self._monthly_amount(s.get("amount", 0), s.get("billing_cycle", "monthly"))
                for s in active_in_month
                if s.get("status") in ("active", "trial")
            )

            trend.append({
                "month": month_start.strftime("%b %Y"),
                "year": target_year,
                "month_num": target_month,
                "total_spend": round(total, 2),
                "subscription_count": len(active_in_month),
            })

        return trend

    def compute_upcoming_renewals(self, subscriptions: List[Dict], days: int = 30) -> List[Dict]:
        """Get subscriptions renewing in the next N days."""
        today = date.today()
        cutoff = today + timedelta(days=days)
        upcoming = []

        for sub in subscriptions:
            if sub.get("status") not in ("active", "trial"):
                continue

            next_billing = sub.get("next_billing_date")
            if isinstance(next_billing, str):
                try:
                    next_billing = date.fromisoformat(next_billing)
                except Exception:
                    next_billing = None

            if next_billing and today <= next_billing <= cutoff:
                days_until = (next_billing - today).days
                upcoming.append({
                    "subscription_id": str(sub.get("id", "")),
                    "name": sub.get("name", sub.get("merchant", "?")),
                    "amount": sub.get("amount", 0),
                    "currency": sub.get("currency", "INR"),
                    "billing_cycle": sub.get("billing_cycle", "monthly"),
                    "next_billing_date": str(next_billing),
                    "days_until_renewal": days_until,
                    "category": sub.get("category", "other"),
                    "logo_url": sub.get("logo_url"),
                })

        return sorted(upcoming, key=lambda x: x["days_until_renewal"])

    def compute_savings_potential(self, subscriptions: List[Dict], usage_data: Dict) -> Dict:
        """Compute total potential savings."""
        unused_savings = 0.0
        duplicate_savings = 0.0
        total_monthly = 0.0

        active = [s for s in subscriptions if s.get("status") == "active"]
        for sub in active:
            monthly = self._monthly_amount(sub.get("amount", 0), sub.get("billing_cycle", "monthly"))
            total_monthly += monthly

            sub_id = str(sub.get("id", ""))
            usage = usage_data.get(sub_id, {})
            days_since = usage.get("days_since_last_use")
            if days_since and days_since >= 30:
                unused_savings += monthly

            if sub.get("is_duplicate"):
                duplicate_savings += monthly

        return {
            "total_monthly_spend": round(total_monthly, 2),
            "unused_savings": round(unused_savings, 2),
            "duplicate_savings": round(duplicate_savings, 2),
            "total_potential_savings": round(unused_savings + duplicate_savings, 2),
            "savings_percentage": round(
                ((unused_savings + duplicate_savings) / total_monthly * 100) if total_monthly else 0, 1
            ),
        }
