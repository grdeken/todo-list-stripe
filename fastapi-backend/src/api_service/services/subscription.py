"""Subscription business logic and todo limit checking."""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from ..models.user import User
from ..models.todo import Todo
from . import stripe_service


async def get_user_todo_count(user_id: int, db: AsyncSession) -> int:
    """
    Count all todos across all lists for a user.

    Args:
        user_id: The user's ID
        db: Database session

    Returns:
        Total number of todos for the user
    """
    result = await db.execute(
        select(func.count(Todo.id))
        .join(Todo.todo_list)
        .filter(Todo.todo_list.has(user_id=user_id))
    )
    count = result.scalar_one()
    return count


async def check_todo_limit(user: User, db: AsyncSession, free_tier_limit: int = 5) -> bool:
    """
    Check if a user can create more todos based on their subscription tier.

    Args:
        user: The user object
        db: Database session
        free_tier_limit: Maximum todos allowed for free tier users

    Returns:
        True if user can create more todos, False otherwise
    """
    # Premium users have unlimited todos
    if user.subscription_tier == "premium":
        return True

    # Free tier users are limited
    if user.subscription_tier == "free":
        current_count = await get_user_todo_count(user.id, db)
        return current_count < free_tier_limit

    # Default to allowing if status is unknown
    return True


async def can_create_todos(user: User, db: AsyncSession, free_tier_limit: int = 5) -> bool:
    """
    Alias for check_todo_limit for clarity in API responses.

    Args:
        user: The user object
        db: Database session
        free_tier_limit: Maximum todos allowed for free tier users

    Returns:
        True if user can create more todos, False otherwise
    """
    return await check_todo_limit(user, db, free_tier_limit)


async def get_subscription_info(user: User, db: AsyncSession, free_tier_limit: int = 5) -> dict:
    """
    Get comprehensive subscription information for a user.

    Args:
        user: The user object
        db: Database session
        free_tier_limit: Maximum todos allowed for free tier users

    Returns:
        Dictionary with subscription status, tier, todo count, and limits
    """
    todo_count = await get_user_todo_count(user.id, db)
    can_create = await check_todo_limit(user, db, free_tier_limit)

    # Initialize billing info
    monthly_amount: Optional[int] = None
    next_billing_date: Optional[datetime] = None

    # Fetch billing info from Stripe for premium users
    if user.subscription_tier == "premium" and user.stripe_subscription_id:
        try:
            subscription = stripe_service.get_subscription(user.stripe_subscription_id)

            # Get the amount from the subscription
            if subscription.items and subscription.items.data:
                price = subscription.items.data[0].price
                monthly_amount = price.unit_amount  # Amount in cents

            # Get next billing date from current_period_end
            if subscription.current_period_end:
                next_billing_date = datetime.fromtimestamp(subscription.current_period_end)
        except Exception as e:
            # Log error but don't fail the entire request
            print(f"Error fetching Stripe subscription details: {e}")

    return {
        "subscription_status": user.subscription_status,
        "subscription_tier": user.subscription_tier,
        "todo_count": todo_count,
        "todo_limit": None if user.subscription_tier == "premium" else free_tier_limit,
        "can_create_todos": can_create,
        "stripe_customer_id": user.stripe_customer_id,
        "stripe_subscription_id": user.stripe_subscription_id,
        "subscription_start_date": user.subscription_start_date,
        "subscription_end_date": user.subscription_end_date,
        "monthly_amount": monthly_amount,
        "next_billing_date": next_billing_date,
    }
