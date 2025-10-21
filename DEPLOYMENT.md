# Vercel Deployment Guide

This guide will help you deploy your Todo List application with Stripe integration to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be pushed to GitHub (already done)
3. **Stripe Account**: Get your API keys from [Stripe Dashboard](https://dashboard.stripe.com)
4. **Vercel CLI** (optional): Install with `npm install -g vercel`

## Deployment Architecture

Your application will be deployed as two separate Vercel projects:

1. **Frontend** (`todo-app/`) - React/Vite static site
2. **Backend** (`fastapi-backend/`) - FastAPI serverless functions

## Step 1: Deploy the Backend API

### Option A: Deploy via Vercel Dashboard (Recommended)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository: `grdeken/todo-list-stripe`
3. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: `fastapi-backend`
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty

4. **Add Environment Variables** (click "Environment Variables"):
   ```
   DATABASE_URL=sqlite:///./todos.db
   SECRET_KEY=<generate-a-long-random-secret-key>
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PREMIUM_PRICE_ID=price_...
   ALLOWED_ORIGINS=["https://your-frontend-domain.vercel.app"]
   FREE_TIER_TODO_LIMIT=5
   ```

   **Important Notes**:
   - Generate `SECRET_KEY` with: `openssl rand -hex 32`
   - Get Stripe keys from: https://dashboard.stripe.com/test/apikeys
   - You'll update `ALLOWED_ORIGINS` after deploying frontend
   - For production, use live Stripe keys (start with `sk_live_` and `pk_live_`)

5. Click **Deploy**

6. Once deployed, **copy your backend URL**: `https://your-backend.vercel.app`

### Option B: Deploy via CLI

```bash
cd fastapi-backend
vercel --prod

# Follow prompts and add environment variables when asked
```

## Step 2: Deploy the Frontend

### Option A: Deploy via Vercel Dashboard (Recommended)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository: `grdeken/todo-list-stripe` (again)
3. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `todo-app`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. **Add Environment Variable**:
   ```
   VITE_API_URL=https://your-backend.vercel.app/api/v1
   ```
   (Use the backend URL from Step 1)

5. Click **Deploy**

6. Once deployed, **copy your frontend URL**: `https://your-frontend.vercel.app`

### Option B: Deploy via CLI

```bash
cd todo-app
vercel --prod

# Add environment variable:
# VITE_API_URL=https://your-backend.vercel.app/api/v1
```

## Step 3: Update Backend CORS Settings

After both are deployed, update the backend's `ALLOWED_ORIGINS` environment variable:

1. Go to your backend project in Vercel Dashboard
2. Settings → Environment Variables
3. Edit `ALLOWED_ORIGINS`:
   ```
   ["https://your-frontend-domain.vercel.app"]
   ```
4. Redeploy the backend (Deployments → ... → Redeploy)

## Step 4: Configure Stripe Webhooks

### For Production Deployment

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. **Endpoint URL**: `https://your-backend.vercel.app/api/v1/subscription/webhook`
4. **Events to send**:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. **Reveal** the webhook signing secret
6. Update backend environment variable `STRIPE_WEBHOOK_SECRET` with this value
7. Redeploy backend

### For Testing

Keep using Stripe CLI for local testing:
```bash
stripe listen --forward-to https://your-backend.vercel.app/api/v1/subscription/webhook
```

## Step 5: Configure Stripe Customer Portal

1. Go to https://dashboard.stripe.com/test/settings/billing/portal
2. Click **Activate test link**
3. Enable features:
   - ✅ Subscription cancellation
   - ✅ Update payment method
   - ✅ Invoice history
4. Save settings

For production, do the same at: https://dashboard.stripe.com/settings/billing/portal

## Step 6: Set Stripe Checkout Success/Cancel URLs

Update your Stripe checkout session creation to use production URLs:

In `fastapi-backend/src/api_service/api/v1/endpoints/subscription.py`, the success/cancel URLs should point to:
- Success: `https://your-frontend.vercel.app/?session_id={CHECKOUT_SESSION_ID}`
- Cancel: `https://your-frontend.vercel.app/`

These are already configured to use the frontend domain dynamically.

## Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite database path | `sqlite:///./todos.db` |
| `SECRET_KEY` | JWT secret key | `openssl rand -hex 32` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` or `sk_live_...` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_test_...` or `pk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret | `whsec_...` |
| `STRIPE_PREMIUM_PRICE_ID` | Premium price ID | `price_...` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["https://your-app.vercel.app"]` |
| `FREE_TIER_TODO_LIMIT` | Free tier todo limit | `5` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `https://your-backend.vercel.app/api/v1` |

## Database Considerations

**Important**: SQLite is not recommended for production on Vercel because:
- Vercel uses serverless functions (stateless)
- File system is read-only in production
- Database changes won't persist between deployments

### For Production, Consider:

1. **PostgreSQL** (Recommended):
   - Use [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)
   - Or [Supabase](https://supabase.com)
   - Or [Neon](https://neon.tech)
   - Update `DATABASE_URL` to PostgreSQL connection string
   - Update SQLAlchemy engine configuration for async PostgreSQL

2. **PlanetScale** (MySQL-compatible):
   - Serverless MySQL database
   - Good for Vercel deployments

## Testing the Deployment

1. Visit your frontend URL: `https://your-frontend.vercel.app`
2. Register a new account
3. Try creating todos (should hit 5 limit on free tier)
4. Test upgrade flow with Stripe test card: `4242 4242 4242 4242`
5. Verify premium features work after upgrade

## Troubleshooting

### CORS Errors
- Check `ALLOWED_ORIGINS` in backend env vars
- Must match your frontend domain exactly (including `https://`)
- No trailing slashes

### Database Errors
- Verify `DATABASE_URL` is set correctly
- For production, migrate to PostgreSQL

### Stripe Errors
- Verify all Stripe env vars are set
- Check webhook secret matches Stripe dashboard
- Ensure webhook endpoint is publicly accessible

### API Not Found (404)
- Verify `VITE_API_URL` points to correct backend
- Check backend deployment logs in Vercel

## Monitoring

- **Backend Logs**: Vercel Dashboard → Your Backend Project → Logs
- **Frontend Logs**: Browser console + Vercel Analytics
- **Stripe Events**: https://dashboard.stripe.com/test/events

## Going Live

When ready for production:

1. Switch Stripe to live mode:
   - Use `sk_live_` and `pk_live_` keys
   - Create new webhook with production endpoint
   - Update `STRIPE_WEBHOOK_SECRET`

2. Use production database (PostgreSQL recommended)

3. Update `ALLOWED_ORIGINS` to production domain

4. Enable Stripe Customer Portal in live mode

5. Test thoroughly with real payment methods in test mode first!

## Useful Commands

```bash
# View backend logs
vercel logs <backend-project-url>

# View frontend logs
vercel logs <frontend-project-url>

# Redeploy backend
cd fastapi-backend && vercel --prod

# Redeploy frontend
cd todo-app && vercel --prod
```

## Support

- Vercel Docs: https://vercel.com/docs
- Stripe Docs: https://stripe.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Vite Docs: https://vitejs.dev
