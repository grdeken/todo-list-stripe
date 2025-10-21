"""Payment and subscription event database models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class PaymentTransaction(Base):
    """Payment transaction model for tracking Stripe payments."""

    __tablename__ = "payment_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stripe_payment_intent_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    stripe_charge_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Amount in cents
    currency: Mapped[str] = mapped_column(String(10), default="usd", nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 'pending', 'succeeded', 'failed', 'refunded'
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'card', etc.
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="payment_transactions")

    def __repr__(self) -> str:
        return f"<PaymentTransaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, status='{self.status}')>"


class SubscriptionEvent(Base):
    """Subscription event model for audit trail of subscription changes."""

    __tablename__ = "subscription_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # 'created', 'renewed', 'canceled', 'updated', 'payment_failed'
    stripe_event_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    event_data: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )  # Store raw Stripe webhook data
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="subscription_events")

    def __repr__(self) -> str:
        return f"<SubscriptionEvent(id={self.id}, user_id={self.user_id}, event_type='{self.event_type}')>"
