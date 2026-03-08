"""
Zentra AI - Backend Tests
"""
import pytest
from datetime import date, timedelta
from app.ai.subscription_detector import SubscriptionDetector
from app.ai.recommendation_engine import RecommendationEngine
from app.ai.analytics_engine import AnalyticsEngine


# ─── Subscription Detector Tests ──────────────────────────────────────────────

class TestSubscriptionDetector:
    detector = SubscriptionDetector()

    def test_detect_netflix_from_email(self):
        result = self.detector.detect_from_email(
            email_subject="Netflix Monthly Subscription Renewed - ₹649",
            email_body="Your Netflix subscription has been renewed. Amount charged: ₹649.",
            email_id="test_001",
        )
        assert result is not None
        assert "netflix" in result.merchant.lower()
        assert result.amount == 649.0
        assert result.currency == "INR"
        assert result.source == "email"

    def test_detect_spotify_from_email(self):
        result = self.detector.detect_from_email(
            email_subject="Spotify Premium - Payment Successful",
            email_body="Your Spotify Premium subscription payment of ₹119 was successful.",
            email_id="test_002",
        )
        assert result is not None
        assert result.amount == 119.0

    def test_detect_from_bank_transaction(self):
        result = self.detector.detect_from_transaction(
            description="Netflix Monthly Subscription",
            amount=649.0,
            txn_date=date.today() - timedelta(days=10),
            txn_id="txn_001",
        )
        assert result is not None
        assert result.amount == 649.0
        assert result.source == "bank"

    def test_no_detection_non_subscription_email(self):
        result = self.detector.detect_from_email(
            email_subject="Weekend Sale - 50% off",
            email_body="Shop now and save big on all items this weekend.",
            email_id="test_003",
        )
        assert result is None

    def test_no_detection_atm_transaction(self):
        result = self.detector.detect_from_transaction(
            description="ATM Cash Withdrawal",
            amount=5000.0,
            txn_date=date.today(),
            txn_id="txn_002",
        )
        assert result is None

    def test_detect_from_sms(self):
        result = self.detector.detect_from_sms(
            sms_text="Your Netflix subscription payment of ₹649 was successful. Auto-renewal enabled.",
            sms_id="sms_001",
        )
        assert result is not None
        assert result.amount == 649.0
        assert result.source == "sms"

    def test_find_duplicates(self):
        subscriptions = [
            {"id": "1", "category": "streaming", "status": "active"},
            {"id": "2", "category": "streaming", "status": "active"},
            {"id": "3", "category": "music", "status": "active"},
        ]
        duplicates = self.detector.find_duplicates(subscriptions)
        assert len(duplicates) >= 1
        assert duplicates[0][0] == "1"
        assert duplicates[0][1] == "2"

    def test_extract_billing_cycle_annual(self):
        result = self.detector.detect_from_email(
            email_subject="Amazon Prime Annual Membership Renewed",
            email_body="Your Amazon Prime annual subscription has been renewed for ₹1499. Yearly plan.",
            email_id="test_005",
        )
        assert result is not None
        assert result.billing_cycle == "annual"


# ─── Recommendation Engine Tests ──────────────────────────────────────────────

class TestRecommendationEngine:
    engine = RecommendationEngine()

    def _make_sub(self, **kwargs):
        default = {
            "id": "sub_1",
            "name": "Netflix",
            "merchant": "Netflix",
            "amount": 649.0,
            "billing_cycle": "monthly",
            "category": "streaming",
            "status": "active",
            "next_billing_date": None,
        }
        default.update(kwargs)
        return default

    def test_recommend_cancel_unused(self):
        sub = self._make_sub()
        # 45 days inactive → medium priority; 60+ days → high priority
        usage_data = {"sub_1": {"days_since_last_use": 65, "usage_score": 0}}
        recs = self.engine.generate_recommendations([sub], usage_data)
        cancel_recs = [r for r in recs if r.action == "cancel"]
        assert len(cancel_recs) >= 1
        assert cancel_recs[0].priority == "high"
        assert cancel_recs[0].potential_savings > 0

    def test_recommend_annual_plan(self):
        sub = self._make_sub(amount=649.0)
        usage_data = {"sub_1": {"days_since_last_use": 1, "usage_score": 80}}
        recs = self.engine.generate_recommendations([sub], usage_data)
        annual_recs = [r for r in recs if r.action == "downgrade"]
        assert len(annual_recs) >= 1

    def test_recommend_duplicate_streaming(self):
        sub1 = self._make_sub(id="sub_1", name="Netflix", amount=649)
        sub2 = self._make_sub(id="sub_2", name="Amazon Prime", amount=299)
        usage_data = {}
        recs = self.engine.generate_recommendations([sub1, sub2], usage_data)
        dup_recs = [r for r in recs if "streaming" in r.category and r.subscription_id is None]
        assert len(dup_recs) >= 1

    def test_recommend_renewal_reminder(self):
        tomorrow = date.today() + timedelta(days=1)
        sub = self._make_sub(next_billing_date=tomorrow)
        recs = self.engine.generate_recommendations([sub], {})
        review_recs = [r for r in recs if r.action == "review"]
        assert len(review_recs) >= 1
        assert review_recs[0].priority == "high"

    def test_no_recs_for_cancelled(self):
        sub = self._make_sub(status="cancelled")
        recs = self.engine.generate_recommendations([sub], {})
        assert len(recs) == 0

    def test_spending_insight(self):
        subs = [
            self._make_sub(id="s1", amount=649, billing_cycle="monthly"),
            self._make_sub(id="s2", name="Spotify", amount=119, billing_cycle="monthly"),
        ]
        insight = self.engine.generate_spending_insight(subs)
        assert insight["total_monthly_spend"] == pytest.approx(649 + 119, 0.01)
        assert insight["total_annual_spend"] == pytest.approx((649 + 119) * 12, 0.01)
        assert len(insight["insights"]) > 0

    def test_potential_savings_from_switch(self):
        sub = self._make_sub(name="Spotify", amount=179)
        recs = self.engine.generate_recommendations([sub], {})
        switch_recs = [r for r in recs if r.action == "switch"]
        assert len(switch_recs) >= 1
        assert switch_recs[0].potential_savings > 0


# ─── Analytics Engine Tests ───────────────────────────────────────────────────

class TestAnalyticsEngine:
    engine = AnalyticsEngine()

    def _sample_subs(self):
        today = date.today()
        return [
            {
                "id": "s1",
                "name": "Netflix",
                "amount": 649.0,
                "billing_cycle": "monthly",
                "status": "active",
                "category": "streaming",
                "start_date": today - timedelta(days=90),
                "next_billing_date": today + timedelta(days=10),
                "cancellation_date": None,
            },
            {
                "id": "s2",
                "name": "Spotify",
                "amount": 119.0,
                "billing_cycle": "monthly",
                "status": "active",
                "category": "music",
                "start_date": today - timedelta(days=60),
                "next_billing_date": today + timedelta(days=5),
                "cancellation_date": None,
            },
            {
                "id": "s3",
                "name": "Amazon Prime",
                "amount": 1499.0,
                "billing_cycle": "annual",
                "status": "active",
                "category": "streaming",
                "start_date": today - timedelta(days=180),
                "next_billing_date": today + timedelta(days=180),
                "cancellation_date": None,
            },
            {
                "id": "s4",
                "name": "Old Service",
                "amount": 299.0,
                "billing_cycle": "monthly",
                "status": "cancelled",
                "category": "other",
                "start_date": today - timedelta(days=300),
                "next_billing_date": None,
                "cancellation_date": today - timedelta(days=30),
            },
        ]

    def test_summary(self):
        subs = self._sample_subs()
        summary = self.engine.compute_summary(subs)
        assert summary["active_count"] == 3
        assert summary["cancelled_count"] == 1
        assert summary["total_monthly_spend"] == pytest.approx(649 + 119 + 1499 / 12, 0.1)

    def test_category_breakdown(self):
        subs = self._sample_subs()
        breakdown = self.engine.compute_category_breakdown(subs)
        categories = {item["category"] for item in breakdown}
        assert "streaming" in categories
        assert "music" in categories

    def test_monthly_trend(self):
        subs = self._sample_subs()
        trend = self.engine.compute_monthly_trend(subs, months=3)
        assert len(trend) == 3
        assert all("month" in t for t in trend)
        assert all("total_spend" in t for t in trend)

    def test_upcoming_renewals(self):
        subs = self._sample_subs()
        renewals = self.engine.compute_upcoming_renewals(subs, days=30)
        names = [r["name"] for r in renewals]
        assert "Netflix" in names
        assert "Spotify" in names
        assert renewals[0]["days_until_renewal"] <= renewals[-1]["days_until_renewal"]

    def test_upcoming_renewals_excludes_distant(self):
        subs = self._sample_subs()
        renewals = self.engine.compute_upcoming_renewals(subs, days=30)
        names = [r["name"] for r in renewals]
        assert "Amazon Prime" not in names

    def test_savings_potential(self):
        subs = self._sample_subs()
        usage_data = {
            "s1": {"days_since_last_use": 45, "usage_score": 0},
            "s2": {"days_since_last_use": 2, "usage_score": 70},
        }
        savings = self.engine.compute_savings_potential(subs, usage_data)
        assert savings["unused_savings"] > 0
        assert savings["total_monthly_spend"] > 0

    def test_monthly_amount_conversion(self):
        assert self.engine._monthly_amount(1200, "annual") == pytest.approx(100, 0.01)
        assert self.engine._monthly_amount(300, "quarterly") == pytest.approx(100, 0.01)
        assert self.engine._monthly_amount(100, "monthly") == pytest.approx(100, 0.01)
        assert self.engine._monthly_amount(50, "weekly") == pytest.approx(216.5, 1)
