# Paid Todo List - Subscription Setup Guide

This guide will help you set up and test the new subscription feature for your Todo List application.

## Overview

Your todo list now has a **freemium model**:
- **Free Tier**: Up to 5 todos
- **Premium Tier**: Unlimited todos for $9.99/month via Stripe

## What Was Implemented

### Backend Changes (FastAPI)

1. **Database Models** (`fastapi-backend/src/api_service/models/`)
   - Updated `User` model with subscription fields
   - New `PaymentTransaction` model for tracking payments
   - New `SubscriptionEvent` model for audit trail

2. **Business Logic** (`fastapi-backend/src/api_service/services/`)
   - `subscription.py` - Todo limit checking and subscription info
   - `stripe_service.py` - Stripe API integration
   - `webhook_handlers.py` - Process Stripe webhook events

3. **API Endpoints** (`fastapi-backend/src/api_service/api/v1/endpoints/`)
   - `GET /api/v1/subscription/status` - Get subscription status
   - `POST /api/v1/subscription/checkout` - Create Stripe checkout session
   - `POST /api/v1/subscription/cancel` - Cancel subscription
   - `GET /api/v1/subscription/portal` - Get customer portal URL
   - `POST /api/v1/subscription/webhook` - Handle Stripe webhooks
   - Updated `POST /api/v1/todos/` to enforce limits

4. **Configuration Updates**
   - Added Stripe API keys to config
   - Added `FREE_TIER_TODO_LIMIT = 5`

### Frontend Changes (React)

1. **New Components** (`todo-app/src/components/`)
   - `Navigation.jsx` - Top navigation bar
   - `SubscriptionBadge.jsx` - Shows plan and usage
   - `UpgradeButton.jsx` - Premium upgrade CTA
   - `UpgradeModal.jsx` - Upgrade prompt when limit reached
   - `SubscriptionSuccess.jsx` - Post-checkout success page
   - `SubscriptionCancel.jsx` - Checkout cancelled page
   - `SubscriptionSettings.jsx` - Manage subscription

2. **Updated Components**
   - `App.jsx` - Added subscription state and navigation
   - `TodoList.jsx` - Limit checking and upgrade prompts
   - `api.js` - Added subscription API methods

3. **Styling**
   - Added comprehensive CSS for all subscription components
   - Modal, badges, buttons, and result pages

## Setup Instructions

### 1. Install Dependencies

#### Backend
```bash
cd fastapi-backend
pip install stripe>=8.0.0
```

The Stripe package has been added to `requirements.txt`.

### 2. Set Up Stripe Account

1. Go to [https://stripe.com](https://stripe.com) and create an account (or login)
2. Use **Test Mode** for development (toggle in top right)
3. Get your API keys:
   - Dashboard → Developers → API keys
   - Copy **Publishable key** (starts with `pk_test_`)
   - Copy **Secret key** (starts with `sk_test_`)

### 3. Create Stripe Product

1. Go to Dashboard → Products → Create product
2. Set up the product:
   - **Name**: "Premium Todo List"
   - **Description**: "Unlimited todos and premium features"
   - **Pricing**: $9.99 USD / month (recurring)
3. Click "Create product"
4. Copy the **Price ID** (starts with `price_`)

### 4. Set Up Stripe Webhook

1. Go to Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Set **Endpoint URL**: `http://localhost:8000/api/v1/subscription/webhook` (for local testing)
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click "Add endpoint"
6. Copy the **Signing secret** (starts with `whsec_`)

### 5. Configure Environment Variables

Create/update `.env` file in `fastapi-backend/`:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./todos.db

# Security
SECRET_KEY=your-secret-key-change-in-production

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_PREMIUM_PRICE_ID=price_your_price_id_here

# Subscription Settings
FREE_TIER_TODO_LIMIT=5
```

### 6. Run Database Migration

The new fields will be automatically added when you restart the backend. SQLAlchemy will create the new tables and columns.

```bash
cd fastapi-backend
python -m uvicorn src.api_service.main:app --reload
```

### 7. Test Locally with Stripe CLI (Optional but Recommended)

To test webhooks locally:

1. Install Stripe CLI: [https://stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli)
2. Login: `stripe login`
3. Forward webhooks to local server:
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/subscription/webhook
   ```
4. The CLI will give you a webhook signing secret - use this in your `.env` file

### 8. Start the Application

**Backend:**
```bash
cd fastapi-backend
python -m uvicorn src.api_service.main:app --reload
```

**Frontend:**
```bash
cd todo-app
npm run dev
```

## Testing the Subscription Flow

### Test as Free User

1. Register a new account
2. Create todos - you should be able to create up to 5
3. Try to create a 6th todo:
   - Input field should be disabled
   - Warning message appears
   - Clicking "Add" shows upgrade modal

### Test Upgrade Flow

1. Click "Upgrade to Premium" button in nav or modal
2. You'll be redirected to Stripe Checkout
3. Use test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any 3-digit CVC
   - Any ZIP code
4. Complete checkout
5. You'll be redirected back to success page
6. Subscription badge should now show "Premium ⭐"
7. You can now create unlimited todos

### Test Stripe Test Cards

Use these test cards for different scenarios:

- **Success**: `4242 4242 4242 4242`
- **Payment declined**: `4000 0000 0000 0002`
- **Requires authentication**: `4000 0025 0000 3155`

### Test Webhook Events

If using Stripe CLI:
```bash
# Trigger test events
stripe trigger customer.subscription.created
stripe trigger invoice.payment_succeeded
stripe trigger customer.subscription.deleted
```

### Test Subscription Management

1. As a premium user, go to Settings (add a settings page or use portal)
2. Click "Manage Billing" - opens Stripe Customer Portal
3. You can:
   - Update payment method
   - View invoices
   - Cancel subscription

## API Endpoints Reference

### Subscription Endpoints

```
GET    /api/v1/subscription/status
- Returns: subscription info, todo count, limits
- Auth: Required

POST   /api/v1/subscription/checkout
- Body: { success_url?: string, cancel_url?: string }
- Returns: { session_id, session_url }
- Auth: Required

POST   /api/v1/subscription/cancel
- Returns: { message, cancel_at }
- Auth: Required

GET    /api/v1/subscription/portal
- Returns: { portal_url }
- Auth: Required

POST   /api/v1/subscription/webhook
- Body: Stripe event payload
- Headers: stripe-signature
- Auth: None (signature verified)
```

## Deployment Checklist

When deploying to production:

### Backend
1. ✅ Update `DATABASE_URL` to production database
2. ✅ Generate new `SECRET_KEY`
3. ✅ Switch Stripe keys from test to live mode
4. ✅ Update webhook URL to production URL
5. ✅ Set up proper CORS origins
6. ✅ Enable HTTPS (required by Stripe)
7. ✅ Set up monitoring for webhook failures

### Frontend
1. ✅ Update `API_BASE_URL` to production backend
2. ✅ Update success/cancel URLs to production URLs
3. ✅ Test checkout flow end-to-end

### Stripe Dashboard
1. ✅ Switch to Live Mode
2. ✅ Verify product and price are created
3. ✅ Update webhook endpoint to production URL
4. ✅ Configure customer portal settings
5. ✅ Set up email notifications
6. ✅ Configure billing grace period settings

## Troubleshooting

### Todos Not Being Limited
- Check `FREE_TIER_TODO_LIMIT` in config
- Verify user's `subscription_tier` is "free"
- Check backend logs for errors in limit checking

### Checkout Not Working
- Verify Stripe publishable key is correct
- Check browser console for errors
- Ensure CORS is configured correctly
- Verify Price ID is correct

### Webhooks Not Firing
- Check webhook signing secret is correct
- Use Stripe CLI for local testing
- Check webhook logs in Stripe Dashboard
- Verify webhook endpoint is accessible

### Payment Not Activating Subscription
- Check webhook is being received
- Check database for subscription_events entries
- Verify user's stripe_customer_id is set
- Check application logs for webhook processing errors

## Architecture Diagram

```
┌─────────────┐
│   React     │
│  Frontend   │
└──────┬──────┘
       │ API calls
       ▼
┌─────────────┐         ┌──────────────┐
│   FastAPI   │◄────────┤    Stripe    │
│   Backend   │         │   Webhooks   │
└──────┬──────┘         └──────────────┘
       │
       ▼
┌─────────────┐
│   SQLite    │
│  Database   │
└─────────────┘
```

## File Structure

```
fastapi-backend/
├── src/api_service/
│   ├── models/
│   │   ├── user.py (updated)
│   │   └── payment.py (new)
│   ├── schemas/
│   │   ├── user.py (updated)
│   │   └── payment.py (new)
│   ├── services/
│   │   ├── subscription.py (new)
│   │   ├── stripe_service.py (new)
│   │   └── webhook_handlers.py (new)
│   └── api/v1/endpoints/
│       ├── subscription.py (new)
│       └── todos.py (updated)

todo-app/
├── src/
│   ├── components/
│   │   ├── Navigation.jsx (new)
│   │   ├── SubscriptionBadge.jsx (new)
│   │   ├── UpgradeButton.jsx (new)
│   │   ├── UpgradeModal.jsx (new)
│   │   ├── SubscriptionSuccess.jsx (new)
│   │   ├── SubscriptionCancel.jsx (new)
│   │   ├── SubscriptionSettings.jsx (new)
│   │   ├── App.jsx (updated)
│   │   └── TodoList.jsx (updated)
│   ├── api.js (updated)
│   └── App.css (updated)
```

## Support

For issues or questions:
1. Check Stripe logs: Dashboard → Developers → Logs
2. Check webhook attempts: Dashboard → Developers → Webhooks → [Your endpoint]
3. Check application logs for backend errors
4. Review browser console for frontend errors

## Next Steps

Consider these enhancements:
- Annual subscription with discount
- Trial period (7 or 14 days)
- Multiple tiers (Basic, Pro, Enterprise)
- Usage analytics dashboard
- Payment history view
- Team/family plans
- Promotional codes
- Referral program

---

**You're all set!** Your todo list now has a fully functional subscription system powered by Stripe. 🎉
