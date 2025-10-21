"""Stripe payment service integration."""
import stripe
from typing import Optional

from ..core.config import settings


def initialize_stripe() -> None:
    """Initialize Stripe with API key."""
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_customer(email: str, name: str, metadata: Optional[dict] = None) -> stripe.Customer:
    """
    Create a Stripe customer.

    Args:
        email: Customer email address
        name: Customer name
        metadata: Optional metadata to attach to customer

    Returns:
        Stripe Customer object
    """
    return stripe.Customer.create(
        email=email,
        name=name,
        metadata=metadata or {},
    )


def create_checkout_session(
    customer_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
    metadata: Optional[dict] = None,
) -> stripe.checkout.Session:
    """
    Create a Stripe Checkout session for subscription.

    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID for the subscription
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
        metadata: Optional metadata to attach to checkout session

    Returns:
        Stripe Checkout Session object
    """
    return stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata or {},
        allow_promotion_codes=True,
    )


def create_subscription(
    customer_id: str, price_id: str, metadata: Optional[dict] = None
) -> stripe.Subscription:
    """
    Create a Stripe subscription directly (without checkout).

    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID for the subscription
        metadata: Optional metadata to attach to subscription

    Returns:
        Stripe Subscription object
    """
    return stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        metadata=metadata or {},
    )


def get_subscription(subscription_id: str) -> stripe.Subscription:
    """
    Retrieve a Stripe subscription.

    Args:
        subscription_id: Stripe subscription ID

    Returns:
        Stripe Subscription object
    """
    return stripe.Subscription.retrieve(subscription_id)


def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> stripe.Subscription:
    """
    Cancel a Stripe subscription.

    Args:
        subscription_id: Stripe subscription ID
        at_period_end: If True, cancel at end of billing period. If False, cancel immediately.

    Returns:
        Cancelled Stripe Subscription object
    """
    if at_period_end:
        return stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
    else:
        return stripe.Subscription.delete(subscription_id)


def get_customer(customer_id: str) -> stripe.Customer:
    """
    Retrieve a Stripe customer.

    Args:
        customer_id: Stripe customer ID

    Returns:
        Stripe Customer object
    """
    return stripe.Customer.retrieve(customer_id)


def create_customer_portal_session(customer_id: str, return_url: str) -> stripe.billing_portal.Session:
    """
    Create a Stripe customer portal session for subscription management.

    Args:
        customer_id: Stripe customer ID
        return_url: URL to return to after leaving portal

    Returns:
        Stripe Billing Portal Session object
    """
    return stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> stripe.Event:
    """
    Verify Stripe webhook signature and construct event.

    Args:
        payload: Request body bytes
        signature: Stripe signature from headers
        secret: Webhook signing secret

    Returns:
        Stripe Event object

    Raises:
        stripe.error.SignatureVerificationError: If signature verification fails
    """
    return stripe.Webhook.construct_event(payload, signature, secret)


def construct_event(payload: str, signature: str) -> stripe.Event:
    """
    Construct a Stripe event from webhook payload.

    Args:
        payload: Request body as string
        signature: Stripe signature from headers

    Returns:
        Stripe Event object

    Raises:
        stripe.error.SignatureVerificationError: If signature verification fails
    """
    return stripe.Webhook.construct_event(
        payload, signature, settings.STRIPE_WEBHOOK_SECRET
    )
