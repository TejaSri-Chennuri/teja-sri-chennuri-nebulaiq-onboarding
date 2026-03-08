"""
Zentra AI - Recommendation Engine

Analyzes subscription data to generate personalized recommendations
for cost optimization, cancellations, and service management.
"""
from datetime import date, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Recommendation:
    id: str
    subscription_id: Optional[str]
    title: str
    message: str
    action: str                # "cancel", "pause", "downgrade", "switch", "review"
    potential_savings: float
    priority: str              # "high", "medium", "low"
    category: str
    reason: str
    metadata: Dict = field(default_factory=dict)


class RecommendationEngine:
    """Generates personalized subscription optimization recommendations."""

    def __init__(self):
        self.cheaper_alternatives = {
            "Netflix": [
                {"name": "JioCinema", "amount": 0, "note": "Free with JioFiber / basic content available for free"},
                {"name": "SonyLIV", "amount": 299, "note": "Similar content at lower price"},
            ],
            "Spotify": [
                {"name": "JioSaavn", "amount": 0, "note": "Free tier with ads, or ₹99/month for premium"},
                {"name": "Gaana", "amount": 99, "note": "Similar music at ₹99/month"},
            ],
            "Amazon Prime": [
                {"name": "Hotstar Basic", "amount": 299, "note": "Cheaper streaming option"},
            ],
            "Coursera Plus": [
                {"name": "YouTube Learning", "amount": 0, "note": "Many free courses available"},
                {"name": "Udemy", "amount": 499, "note": "Buy individual courses when on sale"},
            ],
        }

    def analyze_usage(self, subscription: Dict, usage_logs: List[Dict]) -> Dict:
        """Analyze subscription usage pattern."""
        if not usage_logs:
            return {
                "last_used": None,
                "usage_frequency": 0,
                "usage_score": 0,
                "days_since_last_use": None,
            }

        today = date.today()
        last_used = max(
            [log.get("logged_at", today) for log in usage_logs],
            default=None,
        )

        # Count usage in last 30 days
        thirty_days_ago = today - timedelta(days=30)
        recent_uses = [
            log for log in usage_logs
            if log.get("logged_at") and log["logged_at"] >= thirty_days_ago
        ]

        days_since = None
        if last_used:
            if hasattr(last_used, "date"):
                last_used = last_used.date()
            days_since = (today - last_used).days

        # Usage score: 100 = uses every day, 0 = never used in 30 days
        usage_score = min(len(recent_uses) * 3.33, 100)

        return {
            "last_used": last_used,
            "usage_frequency": len(recent_uses),
            "usage_score": usage_score,
            "days_since_last_use": days_since,
        }

    def generate_recommendations(
        self,
        subscriptions: List[Dict],
        usage_data: Dict[str, Dict],
        monthly_budget: Optional[float] = None,
    ) -> List[Recommendation]:
        """Generate all recommendations for a user's subscriptions."""
        recommendations = []
        rec_id = 0

        for sub in subscriptions:
            if sub.get("status") != "active":
                continue

            sub_id = str(sub.get("id", ""))
            usage = usage_data.get(sub_id, {})
            usage_score = sub.get("usage_score", usage.get("usage_score", 0))
            days_since = usage.get("days_since_last_use")
            amount = sub.get("amount", 0)
            name = sub.get("name", sub.get("merchant", "Unknown"))
            billing_cycle = sub.get("billing_cycle", "monthly")

            # Monthly equivalent
            monthly_amount = amount
            if billing_cycle == "annual":
                monthly_amount = amount / 12
            elif billing_cycle == "quarterly":
                monthly_amount = amount / 3

            # --- Unused subscription ---
            if days_since is not None and days_since >= 30:
                rec_id += 1
                recommendations.append(Recommendation(
                    id=f"rec_{rec_id}",
                    subscription_id=sub_id,
                    title=f"Cancel unused {name}",
                    message=f"You haven't used {name} in {days_since} days. "
                            f"Cancelling it would save you ₹{monthly_amount:.0f}/month.",
                    action="cancel",
                    potential_savings=monthly_amount,
                    priority="high" if days_since >= 60 else "medium",
                    category=sub.get("category", "other"),
                    reason=f"No usage detected for {days_since} days",
                    metadata={"days_inactive": days_since},
                ))
            elif usage_score < 20 and usage_score > 0:
                rec_id += 1
                recommendations.append(Recommendation(
                    id=f"rec_{rec_id}",
                    subscription_id=sub_id,
                    title=f"Low usage detected on {name}",
                    message=f"You're barely using {name} (usage score: {usage_score:.0f}/100). "
                            f"Consider pausing or cancelling to save ₹{monthly_amount:.0f}/month.",
                    action="pause",
                    potential_savings=monthly_amount,
                    priority="medium",
                    category=sub.get("category", "other"),
                    reason=f"Low usage score of {usage_score:.0f}/100",
                    metadata={"usage_score": usage_score},
                ))

            # --- Upcoming renewal reminder ---
            next_billing = sub.get("next_billing_date")
            if next_billing:
                if hasattr(next_billing, "date"):
                    next_billing = next_billing.date()
                elif isinstance(next_billing, str):
                    try:
                        next_billing = date.fromisoformat(next_billing)
                    except Exception:
                        next_billing = None

            if next_billing:
                days_until_renewal = (next_billing - date.today()).days
                if 0 < days_until_renewal <= 3:
                    rec_id += 1
                    recommendations.append(Recommendation(
                        id=f"rec_{rec_id}",
                        subscription_id=sub_id,
                        title=f"{name} renews in {days_until_renewal} day(s)",
                        message=f"Your {name} subscription renews on {next_billing} for ₹{amount:.0f}. "
                                f"Review before it auto-renews.",
                        action="review",
                        potential_savings=0,
                        priority="high",
                        category=sub.get("category", "other"),
                        reason=f"Renewal in {days_until_renewal} days",
                        metadata={"renewal_date": str(next_billing), "days_until": days_until_renewal},
                    ))

            # --- Cheaper alternatives ---
            alternatives = self.cheaper_alternatives.get(name, [])
            for alt in alternatives:
                if alt["amount"] < monthly_amount:
                    savings = monthly_amount - alt["amount"]
                    rec_id += 1
                    recommendations.append(Recommendation(
                        id=f"rec_{rec_id}",
                        subscription_id=sub_id,
                        title=f"Switch from {name} to {alt['name']}",
                        message=f"{alt['note']}. Save ₹{savings:.0f}/month by switching.",
                        action="switch",
                        potential_savings=savings,
                        priority="low",
                        category=sub.get("category", "other"),
                        reason="Cheaper alternative available",
                        metadata={"alternative": alt["name"], "alternative_amount": alt["amount"]},
                    ))

            # --- Annual plan discount ---
            if billing_cycle == "monthly" and amount > 200:
                annual_equivalent = amount * 12
                estimated_annual_price = annual_equivalent * 0.75  # typical 25% discount
                savings = annual_equivalent - estimated_annual_price
                rec_id += 1
                recommendations.append(Recommendation(
                    id=f"rec_{rec_id}",
                    subscription_id=sub_id,
                    title=f"Switch {name} to annual plan",
                    message=f"Switching to an annual plan for {name} could save you ~₹{savings:.0f}/year "
                            f"(typically 20-30% off monthly price).",
                    action="downgrade",
                    potential_savings=savings / 12,
                    priority="low",
                    category=sub.get("category", "other"),
                    reason="Annual plans are typically cheaper",
                    metadata={"potential_annual_savings": savings},
                ))

        # --- Duplicate services ---
        category_subs: Dict[str, List] = {}
        for sub in subscriptions:
            if sub.get("status") != "active":
                continue
            cat = sub.get("category", "other")
            if cat not in category_subs:
                category_subs[cat] = []
            category_subs[cat].append(sub)

        overlap_categories = ["streaming", "music", "cloud_storage"]
        for cat in overlap_categories:
            cat_list = category_subs.get(cat, [])
            if len(cat_list) > 1:
                names = [s.get("name", s.get("merchant", "?")) for s in cat_list]
                total_spend = sum(s.get("amount", 0) for s in cat_list)
                cheapest = min(cat_list, key=lambda s: s.get("amount", 0))
                savings = total_spend - cheapest.get("amount", 0)
                rec_id += 1
                recommendations.append(Recommendation(
                    id=f"rec_{rec_id}",
                    subscription_id=None,
                    title=f"You have {len(cat_list)} {cat} services",
                    message=f"You're paying for: {', '.join(names)}. "
                            f"Consider keeping only one to save ₹{savings:.0f}/month.",
                    action="cancel",
                    potential_savings=savings,
                    priority="medium",
                    category=cat,
                    reason=f"Multiple {cat} subscriptions detected",
                    metadata={"services": names, "total_spend": total_spend},
                ))

        # Sort by potential savings descending
        recommendations.sort(key=lambda r: r.potential_savings, reverse=True)
        return recommendations

    def generate_spending_insight(self, subscriptions: List[Dict]) -> Dict:
        """Generate spending insights summary."""
        active_subs = [s for s in subscriptions if s.get("status") == "active"]

        total_monthly = 0.0
        category_breakdown = {}

        for sub in active_subs:
            amount = sub.get("amount", 0)
            billing_cycle = sub.get("billing_cycle", "monthly")
            cat = sub.get("category", "other")

            monthly_amount = amount
            if billing_cycle == "annual":
                monthly_amount = amount / 12
            elif billing_cycle == "quarterly":
                monthly_amount = amount / 3

            total_monthly += monthly_amount
            category_breakdown[cat] = category_breakdown.get(cat, 0) + monthly_amount

        total_annual = total_monthly * 12

        # Find top services by cost
        top_services = sorted(
            [
                {"name": s.get("name", s.get("merchant", "?")), "amount": s.get("amount", 0)}
                for s in active_subs
            ],
            key=lambda x: x["amount"],
            reverse=True,
        )[:5]

        return {
            "total_monthly_spend": round(total_monthly, 2),
            "total_annual_spend": round(total_annual, 2),
            "active_count": len(active_subs),
            "category_breakdown": {k: round(v, 2) for k, v in category_breakdown.items()},
            "top_services": top_services,
            "insights": [
                f"You are spending ₹{total_monthly:.0f} per month on {len(active_subs)} subscriptions",
                f"That's ₹{total_annual:.0f} per year",
                *[
                    f"You spend ₹{v:.0f}/month on {k} services"
                    for k, v in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
                ],
            ],
        }
