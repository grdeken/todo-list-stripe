"""Stripe webhook event handlers."""
from datetime import datetime
import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..models.payment import PaymentTransaction, SubscriptionEvent


async def handle_checkout_session_completed(
    event: stripe.Event, db: AsyncSession
) -> dict:
    """
    Handle checkout.session.completed event.

    This is called when a customer successfully completes checkout.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Result dictionary with status and message
    """
    session = event.data.object
    customer_id = session.customer
    subscription_id = session.subscription

    # Find user by Stripe customer ID
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"status": "error", "message": f"User not found for customer {customer_id}"}

    # Update user subscription
    user.subscription_status = "active"
    user.subscription_tier = "premium"
    user.stripe_subscription_id = subscription_id
    user.subscription_start_date = datetime.utcnow()

    # Log event
    event_log = SubscriptionEvent(
        user_id=user.id,
        event_type="checkout_completed",
        stripe_event_id=event.id,
        subscription_id=subscription_id,
        event_data=dict(session),
    )
    db.add(event_log)

    await db.commit()

    return {"status": "success", "message": f"User {user.id} upgraded to premium"}


async def handle_customer_subscription_created(
    event: stripe.Event, db: AsyncSession
) -> dict:
    """
    Handle customer.subscription.created event.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Result dictionary with status and message
    """
    subscription = event.data.object
    customer_id = subscription.customer
    subscription_id = subscription.id

    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"status": "error", "message": f"User not found for customer {customer_id}"}

    user.subscription_status = "active"
    user.subscription_tier = "premium"
    user.stripe_subscription_id = subscription_id
    user.subscription_start_date = datetime.fromtimestamp(subscription.current_period_start)

    event_log = SubscriptionEvent(
        user_id=user.id,
        event_type="subscription_created",
        stripe_event_id=event.id,
        subscription_id=subscription_id,
        event_data=dict(subscription),
    )
    db.add(event_log)

    await db.commit()

    return {"status": "success", "message": f"Subscription created for user {user.id}"}


async def handle_customer_subscription_updated(
    event: stripe.Event, db: AsyncSession
) -> dict:
    """
    Handle customer.subscription.updated event.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Result dictionary with status and message
    """
    subscription = event.data.object
    subscription_id = subscription.id

    result = await db.execute(
        select(User).where(User.stripe_subscription_id == subscription_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"status": "error", "message": f"User not found for subscription {subscription_id}"}

    # Update subscription status based on Stripe status
    stripe_status = subscription.status
    if stripe_status == "active":
        user.subscription_status = "active"
        user.subscription_tier = "premium"
    elif stripe_status == "canceled":
        user.subscription_status = "canceled"
        user.subscription_tier = "free"
        user.subscription_end_date = datetime.utcnow()
    elif stripe_status == "past_due":
        user.subscription_status = "past_due"
    elif stripe_status == "unpaid":
        user.subscription_status = "past_due"

    # Check for cancellation scheduled at period end
    if subscription.cancel_at_period_end:
        user.subscription_status = "canceled"
        user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)

    event_log = SubscriptionEvent(
        user_id=user.id,
        event_type="subscription_updated",
        stripe_event_id=event.id,
        subscription_id=subscription_id,
        event_data=dict(subscription),
    )
    db.add(event_log)

    await db.commit()

    return {"status": "success", "message": f"Subscription updated for user {user.id}"}


async def handle_customer_subscription_deleted(
    event: stripe.Event, db: AsyncSession
) -> dict:
    """
    Handle customer.subscription.deleted event.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Result dictionary with status and message
    """
    subscription = event.data.object
    subscription_id = subscription.id

    result = await db.execute(
        select(User).where(User.stripe_subscription_id == subscription_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"status": "error", "message": f"User not found for subscription {subscription_id}"}

    # Downgrade user to free tier
    user.subscription_status = "canceled"
    user.subscription_tier = "free"
    user.subscription_end_date = datetime.utcnow()
    user.stripe_subscription_id = None

    event_log = SubscriptionEvent(
        user_id=user.id,
        event_type="subscription_deleted",
        stripe_event_id=event.id,
        subscription_id=subscription_id,
        event_data=dict(subscription),
    )
    db.add(event_log)

    await db.commit()

    return {"status": "success", "message": f"User {user.id} downgraded to free tier"}


async def handle_invoice_payment_succeeded(
    event: stripe.Event, db: AsyncSession
) -> dict:
    """
    Handle invoice.payment_succeeded event.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Result dictionary with status and message
    """
    invoice = event.data.object
    customer_id = invoice.customer
    payment_intent_id = invoice.payment_intent
    subscription_id = invoice.subscription

    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"status": "error", "message": f"User not found for customer {customer_id}"}

    # Log payment transaction
    payment = PaymentTransaction(
        user_id=user.id,
        stripe_payment_intent_id=payment_intent_id,
        amount=invoice.amount_paid,
        currency=invoice.currency,
        status="succeeded",
        payment_method="card",
    )
    db.add(payment)

    # Update subscription status to active
    if user.subscription_status == "past_due":
        user.subscription_status = "active"

    event_log = SubscriptionEvent(
        user_id=user.id,
        event_type="payment_succeeded",
        stripe_event_id=event.id,
        subscription_id=subscription_id,
        event_data=dict(invoice),
    )
    db.add(event_log)

    await db.commit()

    return {"status": "success", "message": f"Payment logged for user {user.id}"}


async def handle_invoice_payment_failed(
    event: stripe.Event, db: AsyncSession
) -> dict:
    """
    Handle invoice.payment_failed event.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Result dictionary with status and message
    """
    invoice = event.data.object
    customer_id = invoice.customer
    payment_intent_id = invoice.payment_intent
    subscription_id = invoice.subscription

    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"status": "error", "message": f"User not found for customer {customer_id}"}

    # Log failed payment
    payment = PaymentTransaction(
        user_id=user.id,
        stripe_payment_intent_id=payment_intent_id or f"failed_{event.id}",
        amount=invoice.amount_due,
        currency=invoice.currency,
        status="failed",
        payment_method="card",
    )
    db.add(payment)

    # Update subscription status to past_due
    user.subscription_status = "past_due"

    event_log = SubscriptionEvent(
        user_id=user.id,
        event_type="payment_failed",
        stripe_event_id=event.id,
        subscription_id=subscription_id,
        event_data=dict(invoice),
    )
    db.add(event_log)

    await db.commit()

    return {"status": "success", "message": f"Payment failure logged for user {user.id}"}


# Event handler mapping
EVENT_HANDLERS = {
    "checkout.session.completed": handle_checkout_session_completed,
    "customer.subscription.created": handle_customer_subscription_created,
    "customer.subscription.updated": handle_customer_subscription_updated,
    "customer.subscription.deleted": handle_customer_subscription_deleted,
    "invoice.payment_succeeded": handle_invoice_payment_succeeded,
    "invoice.payment_failed": handle_invoice_payment_failed,
}


async def process_webhook_event(event: stripe.Event, db: AsyncSession) -> dict:
    """
    Process a Stripe webhook event by routing to appropriate handler.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Result dictionary with status and message
    """
    event_type = event.type
    handler = EVENT_HANDLERS.get(event_type)

    if not handler:
        return {
            "status": "ignored",
            "message": f"No handler for event type: {event_type}",
        }

    return await handler(event, db)
