"""User database model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class User(Base):
    """User model for authentication and ownership."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Subscription fields
    subscription_status: Mapped[str] = mapped_column(
        String(50), default="free", nullable=False, index=True
    )  # 'free', 'active', 'canceled', 'past_due'
    subscription_tier: Mapped[str] = mapped_column(
        String(50), default="free", nullable=False
    )  # 'free', 'premium'
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    subscription_start_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    subscription_end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    trial_end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    todo_lists: Mapped[list["TodoList"]] = relationship(
        "TodoList", back_populates="user", cascade="all, delete-orphan"
    )
    payment_transactions: Mapped[list["PaymentTransaction"]] = relationship(
        "PaymentTransaction", back_populates="user", cascade="all, delete-orphan"
    )
    subscription_events: Mapped[list["SubscriptionEvent"]] = relationship(
        "SubscriptionEvent", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
