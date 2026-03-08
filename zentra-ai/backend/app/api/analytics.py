"""
Zentra AI - Analytics API
"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionUsage
from app.services.auth import get_current_user
from app.ai.analytics_engine import AnalyticsEngine
from app.ai.recommendation_engine import RecommendationEngine
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["Analytics"])
analytics_engine = AnalyticsEngine()
recommendation_engine = RecommendationEngine()


def _get_usage_data(user_id, db: Session):
    """Build usage data dict for all user subscriptions."""
    from app.models.subscription import Subscription, SubscriptionUsage
    subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
    usage_data = {}
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    for sub in subs:
        logs = db.query(SubscriptionUsage).filter(
            SubscriptionUsage.subscription_id == sub.id,
        ).order_by(SubscriptionUsage.logged_at.desc()).all()

        last_used = logs[0].logged_at.date() if logs else None
        days_since = None
        if last_used:
            days_since = (datetime.utcnow().date() - last_used).days

        recent_count = sum(
            1 for log in logs if log.logged_at >= thirty_days_ago
        )
        usage_score = min(recent_count * 3.33, 100)

        usage_data[str(sub.id)] = {
            "last_used": last_used,
            "days_since_last_use": days_since,
            "usage_score": usage_score,
        }
    return usage_data


def _subs_to_dicts(subs):
    """Convert SQLAlchemy Subscription objects to dicts for analytics."""
    result = []
    for sub in subs:
        result.append({
            "id": sub.id,
            "name": sub.name,
            "merchant": sub.merchant,
            "amount": sub.amount,
            "currency": sub.currency,
            "billing_cycle": sub.billing_cycle.value if sub.billing_cycle else "monthly",
            "status": sub.status.value if sub.status else "active",
            "category": sub.category.value if sub.category else "other",
            "next_billing_date": sub.next_billing_date,
            "start_date": sub.start_date,
            "cancellation_date": sub.cancellation_date,
            "usage_score": sub.usage_score or 0,
            "is_duplicate": sub.is_duplicate or False,
            "logo_url": sub.logo_url,
        })
    return result


@router.get("/summary")
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get spending summary."""
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    sub_dicts = _subs_to_dicts(subs)
    return analytics_engine.compute_summary(sub_dicts)


@router.get("/category-breakdown")
def get_category_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get spending breakdown by category."""
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    sub_dicts = _subs_to_dicts(subs)
    return analytics_engine.compute_category_breakdown(sub_dicts)


@router.get("/monthly-trend")
def get_monthly_trend(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get monthly spending trend."""
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    sub_dicts = _subs_to_dicts(subs)
    return analytics_engine.compute_monthly_trend(sub_dicts, months=months)


@router.get("/upcoming-renewals")
def get_upcoming_renewals(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get subscriptions renewing in the next N days."""
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    sub_dicts = _subs_to_dicts(subs)
    return analytics_engine.compute_upcoming_renewals(sub_dicts, days=days)


@router.get("/savings-potential")
def get_savings_potential(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get potential savings analysis."""
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    sub_dicts = _subs_to_dicts(subs)
    usage_data = _get_usage_data(current_user.id, db)
    return analytics_engine.compute_savings_potential(sub_dicts, usage_data)


@router.get("/recommendations")
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get AI-powered personalized recommendations."""
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    sub_dicts = _subs_to_dicts(subs)
    usage_data = _get_usage_data(current_user.id, db)

    recommendations = recommendation_engine.generate_recommendations(sub_dicts, usage_data)
    return [
        {
            "id": rec.id,
            "subscription_id": rec.subscription_id,
            "title": rec.title,
            "message": rec.message,
            "action": rec.action,
            "potential_savings": rec.potential_savings,
            "priority": rec.priority,
            "category": rec.category,
            "reason": rec.reason,
            "metadata": rec.metadata,
        }
        for rec in recommendations
    ]


@router.get("/insights")
def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get AI-generated spending insights."""
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    sub_dicts = _subs_to_dicts(subs)
    return recommendation_engine.generate_spending_insight(sub_dicts)


@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all dashboard data in a single call."""
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    sub_dicts = _subs_to_dicts(subs)
    usage_data = _get_usage_data(current_user.id, db)

    summary = analytics_engine.compute_summary(sub_dicts)
    category_breakdown = analytics_engine.compute_category_breakdown(sub_dicts)
    monthly_trend = analytics_engine.compute_monthly_trend(sub_dicts, months=6)
    upcoming_renewals = analytics_engine.compute_upcoming_renewals(sub_dicts, days=30)
    recommendations = recommendation_engine.generate_recommendations(sub_dicts, usage_data)
    insights = recommendation_engine.generate_spending_insight(sub_dicts)

    return {
        "summary": summary,
        "category_breakdown": category_breakdown,
        "monthly_trend": monthly_trend,
        "upcoming_renewals": upcoming_renewals,
        "recommendations": [
            {
                "id": rec.id,
                "title": rec.title,
                "message": rec.message,
                "action": rec.action,
                "potential_savings": rec.potential_savings,
                "priority": rec.priority,
                "category": rec.category,
            }
            for rec in recommendations[:5]  # top 5
        ],
        "insights": insights.get("insights", []),
        "total_monthly_spend": insights.get("total_monthly_spend", 0),
        "total_annual_spend": insights.get("total_annual_spend", 0),
    }
