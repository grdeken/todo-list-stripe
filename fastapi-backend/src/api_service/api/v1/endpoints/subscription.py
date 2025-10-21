"""Subscription and payment endpoints."""
from fastapi import APIRouter, HTTPException, status, Request, Header
from sqlalchemy import select
import stripe

from ....core.config import settings
from ....models.user import User
from ....schemas.payment import (
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    SubscriptionStatus,
    CustomerPortalResponse,
    WebhookEventResponse,
)
from ....services import stripe_service, subscription, webhook_handlers
from ...deps import CurrentUser, DatabaseSession

router = APIRouter()

# Initialize Stripe on module load
stripe_service.initialize_stripe()


@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> SubscriptionStatus:
    """
    Get the current user's subscription status and todo limits.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Subscription status with todo count and limits
    """
    info = await subscription.get_subscription_info(
        current_user, db, free_tier_limit=settings.FREE_TIER_TODO_LIMIT
    )

    return SubscriptionStatus(**info)


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    checkout_data: CheckoutSessionCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> CheckoutSessionResponse:
    """
    Create a Stripe checkout session for upgrading to premium.

    Args:
        checkout_data: Checkout session configuration
        db: Database session
        current_user: Current authenticated user

    Returns:
        Checkout session with URL to redirect user

    Raises:
        HTTPException: If user is already premium or Stripe error occurs
    """
    # Check if user is already premium
    if current_user.subscription_tier == "premium":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has premium subscription",
        )

    try:
        # Create or retrieve Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe_service.create_customer(
                email=current_user.email,
                name=current_user.username,
                metadata={"user_id": str(current_user.id)},
            )
            current_user.stripe_customer_id = customer.id
            await db.commit()
        else:
            customer_id = current_user.stripe_customer_id

        # Set default URLs if not provided
        success_url = checkout_data.success_url or f"{settings.ALLOWED_ORIGINS[0]}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = checkout_data.cancel_url or f"{settings.ALLOWED_ORIGINS[0]}/subscription/cancel"

        # Create checkout session
        session = stripe_service.create_checkout_session(
            customer_id=current_user.stripe_customer_id,
            price_id=settings.STRIPE_PREMIUM_PRICE_ID,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": str(current_user.id)},
        )

        return CheckoutSessionResponse(
            session_id=session.id,
            session_url=session.url,
        )

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}",
        )


@router.post("/cancel")
async def cancel_subscription(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict:
    """
    Cancel the current user's subscription (at end of billing period).

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Cancellation confirmation

    Raises:
        HTTPException: If user has no active subscription or Stripe error occurs
    """
    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel",
        )

    try:
        # Cancel subscription at period end
        subscription_obj = stripe_service.cancel_subscription(
            current_user.stripe_subscription_id,
            at_period_end=True,
        )

        # Update user status
        current_user.subscription_status = "canceled"
        await db.commit()

        return {
            "message": "Subscription will be canceled at end of billing period",
            "cancel_at": subscription_obj.cancel_at,
        }

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}",
        )


@router.get("/portal", response_model=CustomerPortalResponse)
async def get_customer_portal(
    current_user: CurrentUser,
) -> CustomerPortalResponse:
    """
    Get Stripe customer portal URL for subscription management.

    Args:
        current_user: Current authenticated user

    Returns:
        Customer portal URL

    Raises:
        HTTPException: If user has no Stripe customer ID or Stripe error occurs
    """
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found",
        )

    try:
        return_url = f"{settings.ALLOWED_ORIGINS[0]}/settings"
        portal_session = stripe_service.create_customer_portal_session(
            customer_id=current_user.stripe_customer_id,
            return_url=return_url,
        )

        return CustomerPortalResponse(portal_url=portal_session.url)

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}",
        )


@router.post("/webhook", response_model=WebhookEventResponse)
async def stripe_webhook(
    request: Request,
    db: DatabaseSession,
    stripe_signature: str = Header(None, alias="stripe-signature"),
) -> WebhookEventResponse:
    """
    Handle Stripe webhook events.

    This endpoint receives and processes webhook events from Stripe.
    No authentication required, but signature verification is performed.

    Args:
        request: FastAPI request object
        db: Database session
        stripe_signature: Stripe signature from headers

    Returns:
        Webhook processing result

    Raises:
        HTTPException: If signature verification fails or processing error occurs
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header",
        )

    # Get raw body
    payload = await request.body()

    try:
        # Verify webhook signature and construct event
        event = stripe_service.verify_webhook_signature(
            payload=payload,
            signature=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )

        # Process event
        result = await webhook_handlers.process_webhook_event(event, db)

        return WebhookEventResponse(
            received=True,
            event_type=event.type,
            message=result.get("message", "Event processed"),
        )

    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid signature: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing error: {str(e)}",
        )
