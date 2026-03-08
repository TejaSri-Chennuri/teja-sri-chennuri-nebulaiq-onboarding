import uuid
from datetime import datetime, date
from sqlalchemy import Column, Float, DateTime, Date, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class SpendingSnapshot(Base):
    __tablename__ = "spending_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    snapshot_date = Column(Date, nullable=False)
    period_month = Column(Integer, nullable=False)    # 1-12
    period_year = Column(Integer, nullable=False)

    total_monthly_spend = Column(Float, default=0.0)
    total_annual_spend = Column(Float, default=0.0)
    active_subscriptions_count = Column(Integer, default=0)
    cancelled_this_period = Column(Integer, default=0)
    new_this_period = Column(Integer, default=0)

    # Category breakdown stored as JSON
    category_breakdown = Column(JSON, nullable=True)    # {"streaming": 500, "music": 200, ...}
    top_services = Column(JSON, nullable=True)          # [{"name": "Netflix", "amount": 649}]
    potential_savings = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="spending_snapshots")
