"""Payment and subscription Pydantic schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CheckoutSessionCreate(BaseModel):
    """Request to create a Stripe checkout session."""

    success_url: Optional[str] = Field(
        default=None,
        description="URL to redirect to after successful payment. If not provided, defaults to app URL",
    )
    cancel_url: Optional[str] = Field(
        default=None,
        description="URL to redirect to if user cancels. If not provided, defaults to app URL",
    )


class CheckoutSessionResponse(BaseModel):
    """Response containing Stripe checkout session URL."""

    session_id: str = Field(description="Stripe checkout session ID")
    session_url: str = Field(description="URL to redirect user to for payment")


class SubscriptionStatus(BaseModel):
    """User's current subscription information."""

    subscription_status: str = Field(
        description="Current subscription status: free, active, canceled, past_due"
    )
    subscription_tier: str = Field(description="Subscription tier: free or premium")
    todo_count: int = Field(description="Current number of todos")
    todo_limit: Optional[int] = Field(
        description="Maximum todos allowed (None for premium users)"
    )
    can_create_todos: bool = Field(description="Whether user can create more todos")
    stripe_customer_id: Optional[str] = Field(default=None)
    stripe_subscription_id: Optional[str] = Field(default=None)
    subscription_start_date: Optional[datetime] = Field(default=None)
    subscription_end_date: Optional[datetime] = Field(default=None)


class PaymentIntentResponse(BaseModel):
    """Response for payment intent operations."""

    payment_intent_id: str
    status: str
    amount: int
    currency: str


class CustomerPortalResponse(BaseModel):
    """Response containing Stripe customer portal URL."""

    portal_url: str = Field(description="URL to Stripe customer portal")


class WebhookEventResponse(BaseModel):
    """Response for webhook events."""

    received: bool = Field(default=True, description="Whether webhook was received")
    event_type: str = Field(description="Type of webhook event processed")
    message: str = Field(description="Processing result message")
