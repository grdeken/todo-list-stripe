# Quick Deployment Guide

## Step 1: Deploy Backend (5 minutes)

1. **Go to**: https://vercel.com/new
2. **Import**: Click "Import Git Repository"
3. **Select**: `grdeken/todo-list-stripe` from GitHub
4. **Configure**:
   - Project Name: `todo-list-backend` (or your choice)
   - Framework Preset: **Other**
   - Root Directory: **`fastapi-backend`**
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

5. **Add Environment Variables** (click "Environment Variables"):

```
DATABASE_URL=sqlite:///./todos.db
SECRET_KEY=your-secret-key-here
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_PREMIUM_PRICE_ID=price_your_price_id_here
ALLOWED_ORIGINS=["http://localhost:5173"]
FREE_TIER_TODO_LIMIT=5
```

**Important**:
- Generate a new `SECRET_KEY` by running: `openssl rand -hex 32`
- Get your Stripe keys from: https://dashboard.stripe.com/test/apikeys
- Copy the values from your local `.env` file in `fastapi-backend/`
- We'll update `ALLOWED_ORIGINS` after deploying the frontend

6. **Click "Deploy"**

7. **Copy your backend URL**: e.g., `https://todo-list-backend-xxx.vercel.app`

---

## Step 2: Deploy Frontend (3 minutes)

1. **Go to**: https://vercel.com/new
2. **Import**: Same repository `grdeken/todo-list-stripe`
3. **Configure**:
   - Project Name: `todo-list-app` (or your choice)
   - Framework Preset: **Vite**
   - Root Directory: **`todo-app`**
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Add Environment Variable**:

```
VITE_API_URL=https://your-backend-url.vercel.app/api/v1
```

Replace `your-backend-url.vercel.app` with the URL from Step 1

5. **Click "Deploy"**

6. **Copy your frontend URL**: e.g., `https://todo-list-app-xxx.vercel.app`

---

## Step 3: Update Backend CORS (2 minutes)

1. **Go to your backend project** in Vercel Dashboard
2. **Settings** → **Environment Variables**
3. **Edit** `ALLOWED_ORIGINS`:
   ```json
   ["https://your-frontend-url.vercel.app"]
   ```
   Replace with your actual frontend URL

4. **Go to Deployments** → Click **...** → **Redeploy**

---

## Step 4: Configure Stripe Webhook (3 minutes)

### Option A: For Testing (use Stripe CLI)
```bash
stripe listen --forward-to https://your-backend-url.vercel.app/api/v1/subscription/webhook
```

### Option B: For Production
1. **Go to**: https://dashboard.stripe.com/webhooks
2. **Add endpoint**: `https://your-backend-url.vercel.app/api/v1/subscription/webhook`
3. **Select events**:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. **Reveal signing secret** and copy it
5. **Update** backend environment variable `STRIPE_WEBHOOK_SECRET` with new value
6. **Redeploy** backend

---

## Step 5: Configure Stripe Customer Portal (2 minutes)

1. **Go to**: https://dashboard.stripe.com/test/settings/billing/portal
2. **Click** "Activate test link"
3. **Enable**:
   - ✅ Subscription cancellation
   - ✅ Update payment method
   - ✅ Invoice history
4. **Save**

---

## Testing Your Deployment

1. Visit your frontend URL
2. Register a new account
3. Create 5 todos (hit the limit)
4. Click "Upgrade to Premium"
5. Use test card: `4242 4242 4242 4242`
6. Verify premium features work!

---

## Important Notes

⚠️ **Database**: The current SQLite setup won't persist data on Vercel. For production:
- Use Vercel Postgres: https://vercel.com/docs/storage/vercel-postgres
- Or Supabase: https://supabase.com
- Or Neon: https://neon.tech

🔐 **Security**:
- Generate a new `SECRET_KEY` for production
- Never commit `.env` files
- Use Stripe live keys for production (start with `sk_live_`)

📊 **Monitoring**:
- Backend logs: Vercel Dashboard → Backend Project → Logs
- Stripe events: https://dashboard.stripe.com/test/events

---

## Finding Your Stripe Configuration

**Get your Stripe test keys from**:
1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your "Publishable key" (starts with `pk_test_`)
3. Reveal and copy your "Secret key" (starts with `sk_test_`)
4. Find your Premium price ID at https://dashboard.stripe.com/test/products
   - Look for your Premium subscription product
   - Copy the Price ID (starts with `price_`)

**Note**: Your local `.env` files already contain these values if you've set them up.

---

## Need Help?

- Vercel Support: https://vercel.com/support
- Stripe Support: https://support.stripe.com
- Full deployment guide: See `DEPLOYMENT.md`

**Total Time: ~15 minutes**
