"""
Zentra AI - Subscriptions API
"""
import json
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.subscription import (
    Subscription, SubscriptionUsage,
    BillingCycle, SubscriptionStatus, SubscriptionCategory, SubscriptionSource,
)
from app.services.auth import get_current_user
from app.services.gmail_scanner import GmailScanner
from app.services.bank_scanner import BankScanner
from app.ai.subscription_detector import SubscriptionDetector

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])
detector = SubscriptionDetector()


class SubscriptionCreate(BaseModel):
    name: str
    merchant: str
    amount: float
    currency: str = "INR"
    billing_cycle: str = "monthly"
    category: str = "other"
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    start_date: Optional[date] = None
    next_billing_date: Optional[date] = None
    notify_before_days: int = 3


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    billing_cycle: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    next_billing_date: Optional[date] = None
    description: Optional[str] = None
    notify_before_days: Optional[int] = None


class SubscriptionResponse(BaseModel):
    id: str
    name: str
    merchant: str
    amount: float
    currency: str
    billing_cycle: str
    status: str
    category: str
    source: str
    description: Optional[str]
    logo_url: Optional[str]
    website_url: Optional[str]
    start_date: Optional[date]
    next_billing_date: Optional[date]
    last_billed_date: Optional[date]
    usage_score: float
    ai_confidence: float
    is_duplicate: bool
    notify_before_days: int
    ai_notes: Optional[str]

    class Config:
        from_attributes = True


class UsageLogRequest(BaseModel):
    usage_type: str = "session"
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


def _to_response(sub: Subscription) -> SubscriptionResponse:
    return SubscriptionResponse(
        id=str(sub.id),
        name=sub.name,
        merchant=sub.merchant,
        amount=sub.amount,
        currency=sub.currency,
        billing_cycle=sub.billing_cycle.value if sub.billing_cycle else "monthly",
        status=sub.status.value if sub.status else "active",
        category=sub.category.value if sub.category else "other",
        source=sub.source.value if sub.source else "manual",
        description=sub.description,
        logo_url=sub.logo_url,
        website_url=sub.website_url,
        start_date=sub.start_date,
        next_billing_date=sub.next_billing_date,
        last_billed_date=sub.last_billed_date,
        usage_score=sub.usage_score or 0.0,
        ai_confidence=sub.ai_confidence or 1.0,
        is_duplicate=sub.is_duplicate or False,
        notify_before_days=sub.notify_before_days or 3,
        ai_notes=sub.ai_notes,
    )


@router.get("", response_model=List[SubscriptionResponse])
def list_subscriptions(
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all subscriptions for the current user."""
    query = db.query(Subscription).filter(Subscription.user_id == current_user.id)
    if status_filter:
        query = query.filter(Subscription.status == status_filter)
    if category:
        query = query.filter(Subscription.category == category)
    subs = query.order_by(Subscription.created_at.desc()).all()
    return [_to_response(s) for s in subs]


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    request: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually add a subscription."""
    try:
        billing_cycle = BillingCycle(request.billing_cycle)
        category = SubscriptionCategory(request.category)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    sub = Subscription(
        user_id=current_user.id,
        name=request.name,
        merchant=request.merchant,
        amount=request.amount,
        currency=request.currency,
        billing_cycle=billing_cycle,
        category=category,
        status=SubscriptionStatus.ACTIVE,
        source=SubscriptionSource.MANUAL,
        description=request.description,
        logo_url=request.logo_url,
        website_url=request.website_url,
        start_date=request.start_date,
        next_billing_date=request.next_billing_date,
        notify_before_days=request.notify_before_days,
        ai_confidence=1.0,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return _to_response(sub)


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific subscription."""
    sub = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return _to_response(sub)


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: str,
    request: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a subscription."""
    sub = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if request.name is not None:
        sub.name = request.name
    if request.amount is not None:
        sub.amount = request.amount
    if request.billing_cycle is not None:
        try:
            sub.billing_cycle = BillingCycle(request.billing_cycle)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid billing_cycle: {request.billing_cycle}")
    if request.category is not None:
        try:
            sub.category = SubscriptionCategory(request.category)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid category: {request.category}")
    if request.status is not None:
        try:
            sub.status = SubscriptionStatus(request.status)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status: {request.status}")
    if request.next_billing_date is not None:
        sub.next_billing_date = request.next_billing_date
    if request.description is not None:
        sub.description = request.description
    if request.notify_before_days is not None:
        sub.notify_before_days = request.notify_before_days

    db.commit()
    db.refresh(sub)
    return _to_response(sub)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a subscription."""
    sub = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(sub)
    db.commit()


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark subscription as cancelled."""
    sub = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub.status = SubscriptionStatus.CANCELLED
    sub.cancellation_date = date.today()
    db.commit()
    db.refresh(sub)
    return _to_response(sub)


@router.post("/{subscription_id}/log-usage", status_code=status.HTTP_201_CREATED)
def log_usage(
    subscription_id: str,
    request: UsageLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log usage for a subscription (helps AI gauge if service is being used)."""
    sub = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    usage = SubscriptionUsage(
        subscription_id=sub.id,
        usage_type=request.usage_type,
        duration_minutes=request.duration_minutes,
        notes=request.notes,
    )
    db.add(usage)

    # Update usage score (simple rolling average)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_count = db.query(SubscriptionUsage).filter(
        SubscriptionUsage.subscription_id == sub.id,
        SubscriptionUsage.logged_at >= thirty_days_ago,
    ).count()
    sub.usage_score = min(recent_count * 3.33, 100)

    db.commit()
    return {"message": "Usage logged", "usage_score": sub.usage_score}


@router.post("/scan/gmail")
def scan_gmail(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Scan Gmail for subscription emails and auto-detect subscriptions."""
    scanner = GmailScanner(
        access_token=current_user.gmail_access_token or "mock",
        refresh_token=current_user.gmail_refresh_token,
    )
    emails = scanner.scan_emails()
    detected = []

    for email in emails:
        result = detector.detect_from_email(
            email_subject=email["subject"],
            email_body=email["body"],
            email_id=email["id"],
        )
        if result and result.confidence >= 0.5:
            # Check if already exists
            existing = db.query(Subscription).filter(
                Subscription.user_id == current_user.id,
                Subscription.merchant == result.merchant,
                Subscription.detection_source_id == result.detection_source_id,
            ).first()
            if not existing:
                try:
                    billing_cycle = BillingCycle(result.billing_cycle)
                    category = SubscriptionCategory(result.category)
                except ValueError:
                    billing_cycle = BillingCycle.MONTHLY
                    category = SubscriptionCategory.OTHER

                sub = Subscription(
                    user_id=current_user.id,
                    name=result.name,
                    merchant=result.merchant,
                    amount=result.amount,
                    currency=result.currency,
                    billing_cycle=billing_cycle,
                    category=category,
                    status=SubscriptionStatus.ACTIVE,
                    source=SubscriptionSource.EMAIL,
                    logo_url=result.logo_url,
                    website_url=result.website_url,
                    next_billing_date=result.next_billing_date,
                    last_billed_date=result.last_billed_date,
                    ai_confidence=result.confidence,
                    detection_source_id=result.detection_source_id,
                    ai_notes=result.notes,
                )
                db.add(sub)
                detected.append(result.name)

    db.commit()
    return {
        "message": f"Scanned {len(emails)} emails, detected {len(detected)} new subscriptions",
        "detected": detected,
    }


@router.post("/scan/bank")
def scan_bank(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Scan bank transactions for subscription payments."""
    scanner = BankScanner(access_token=current_user.plaid_access_token)
    transactions = scanner.get_transactions()
    detected = []

    for txn in transactions:
        result = detector.detect_from_transaction(
            description=txn["description"],
            amount=txn["amount"],
            txn_date=txn["date"] if isinstance(txn["date"], date) else date.today(),
            txn_id=txn["id"],
        )
        if result and result.confidence >= 0.5:
            existing = db.query(Subscription).filter(
                Subscription.user_id == current_user.id,
                Subscription.merchant == result.merchant,
                Subscription.detection_source_id == result.detection_source_id,
            ).first()
            if not existing:
                try:
                    billing_cycle = BillingCycle(result.billing_cycle)
                    category = SubscriptionCategory(result.category)
                except ValueError:
                    billing_cycle = BillingCycle.MONTHLY
                    category = SubscriptionCategory.OTHER

                sub = Subscription(
                    user_id=current_user.id,
                    name=result.name,
                    merchant=result.merchant,
                    amount=result.amount,
                    currency=result.currency,
                    billing_cycle=billing_cycle,
                    category=category,
                    status=SubscriptionStatus.ACTIVE,
                    source=SubscriptionSource.BANK,
                    logo_url=result.logo_url,
                    website_url=result.website_url,
                    next_billing_date=result.next_billing_date,
                    last_billed_date=result.last_billed_date,
                    ai_confidence=result.confidence,
                    detection_source_id=result.detection_source_id,
                    ai_notes=result.notes,
                )
                db.add(sub)
                detected.append(result.name)

    db.commit()
    return {
        "message": f"Scanned {len(transactions)} transactions, detected {len(detected)} new subscriptions",
        "detected": detected,
    }
