# Phase 3: Production Deployment Guide

This guide covers deploying the Dynamic Pricing Agent to production using free tier services.

## 🚀 Deployment Overview

- **Backend**: Render.com (Free tier)
- **Frontend**: Vercel (Free tier)  
- **Database**: Supabase (Free tier)
- **Monitoring**: Built-in dashboard + health checks
- **Retraining**: Daily cron job via Render

## 📋 Prerequisites

1. **GitHub Repository**: Ensure your code is pushed to GitHub
2. **Accounts Setup**:
   - [Render.com](https://render.com) account
   - [Vercel](https://vercel.com) account
   - [Supabase](https://supabase.com) account (optional)

## 🔧 Backend Deployment (Render.com)

### Step 1: Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository

### Step 2: Configure Build Settings

```yaml
# Basic Settings
Name: dynamic-pricing-api
Environment: Python 3
Region: Oregon (US West)
Branch: main

# Build & Deploy
Build Command: pip install -r backend/requirements.txt
Start Command: uvicorn backend.app:app --host 0.0.0.0 --port $PORT

# Advanced Settings
Auto-Deploy: Yes
Health Check Path: /health
```

### Step 3: Environment Variables

Add these environment variables in Render:

```env
PYTHON_VERSION=3.10.0
LOG_TO_FILE=false
MODEL_UPDATE_THRESHOLD=100
RETRAIN_LOG_LEVEL=INFO
FRONTEND_URL=https://dynamic-pricing.vercel.app
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Note your backend URL: `https://your-app-name.onrender.com`

## 🌐 Frontend Deployment (Vercel)

### Step 1: Import Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository

### Step 2: Configure Build Settings

```yaml
# Framework Preset: Vite
# Root Directory: frontend
# Build Command: npm run build
# Output Directory: dist
# Install Command: npm install
```

### Step 3: Environment Variables

Add these in Vercel project settings:

```env
VITE_API_URL=https://your-render-app.onrender.com
VITE_APP_ENV=production
VITE_APP_VERSION=3.0.0
VITE_ENABLE_ANALYTICS=true
VITE_AB_TEST_ENABLED=true
```

### Step 4: Deploy

1. Click "Deploy"
2. Wait for deployment (2-3 minutes)
3. Your app will be live at: `https://your-app.vercel.app`

## 📊 Database Setup (Optional - Supabase)

### Step 1: Create Project

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create new project
3. Note your project URL and API key

### Step 2: Create Tables

```sql
-- Feedback data table
CREATE TABLE feedback_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    product_id VARCHAR(50),
    location VARCHAR(50),
    price_set DECIMAL(10,2),
    actual_demand DECIMAL(10,2),
    revenue_generated DECIMAL(12,2),
    ab_test_group VARCHAR(20)
);

-- System metrics table
CREATE TABLE system_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    total_requests INTEGER,
    error_rate DECIMAL(5,2),
    avg_response_time DECIMAL(8,2),
    uptime_hours DECIMAL(10,2)
);
```

### Step 3: Update Environment Variables

Add to both Render and Vercel:

```env
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
SUPABASE_URL=https://[project].supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

## 🔄 Retraining Setup

### Option 1: Render Cron Jobs (Paid Plan)

Add to `render.yaml`:

```yaml
jobs:
  - type: cron
    name: daily-retrain
    env: python
    schedule: "0 2 * * *"  # Daily at 2 AM UTC
    buildCommand: pip install -r backend/requirements.txt
    startCommand: python backend/retrain.py
```

### Option 2: External Trigger (Free Tier)

Use GitHub Actions or external cron service:

```yaml
# .github/workflows/retrain.yml
name: Daily Retraining
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  retrain:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Retraining
        run: |
          curl -X POST https://your-app.onrender.com/retrain \
            -H "Authorization: Bearer ${{ secrets.RETRAIN_TOKEN }}"
```

## 📈 Monitoring & Alerts

### Built-in Health Checks

- **Backend Health**: `https://your-app.onrender.com/health`
- **Metrics Dashboard**: `https://your-app.onrender.com/metrics`
- **Frontend Monitoring**: Built into the dashboard

### Setting Up Alerts

1. **Render Notifications**:
   - Go to Service Settings → Notifications
   - Add Slack/Discord webhook for deploy notifications

2. **Uptime Monitoring**:
   - Use services like UptimeRobot (free)
   - Monitor both `/health` endpoints

3. **Error Tracking**:
   - Integrate Sentry for production error tracking
   - Add to both frontend and backend

## 🧪 A/B Testing Verification

### Test the A/B System

1. Visit your deployed frontend
2. Check browser localStorage for `ab_test_user_id`
3. Verify you're assigned to either "test" or "control" group
4. Simulate purchase outcomes to generate feedback data

### Monitor Test Results

- Check the A/B Testing tab in your dashboard
- Verify metrics are being tracked
- Confirm statistical significance calculations

## 🔍 Production Checklist

### Pre-Launch

- [ ] Backend deployed and health check passing
- [ ] Frontend deployed and accessible
- [ ] Environment variables configured correctly
- [ ] Database tables created (if using Supabase)
- [ ] A/B testing system functional
- [ ] Monitoring dashboard accessible

### Post-Launch

- [ ] Monitor error rates < 5%
- [ ] Response times < 800ms P95
- [ ] A/B test data flowing correctly
- [ ] Daily retraining trigger working
- [ ] Feedback loop recording outcomes
- [ ] System metrics updating in real-time

## 🚨 Troubleshooting

### Common Issues

1. **Backend Not Starting**:
   ```bash
   # Check build logs in Render dashboard
   # Verify requirements.txt is in backend/ folder
   # Ensure Python version compatibility
   ```

2. **Frontend API Connection Failed**:
   ```bash
   # Verify VITE_API_URL environment variable
   # Check CORS settings in backend
   # Confirm backend is accessible
   ```

3. **Models Not Loading**:
   ```bash
   # Check PyTorch installation in build logs
   # Verify model files are present
   # Check model loading fallback logic
   ```

4. **Performance Issues**:
   ```bash
   # Monitor response times in /metrics endpoint
   # Check memory usage in Render dashboard
   # Optimize queries and reduce model size if needed
   ```

### Support Resources

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Project GitHub Issues](https://github.com/your-username/dynamic-pricing-agent/issues)

## 🎯 Success Metrics

### Target Performance (Free Tier)

- **Uptime**: > 99.5%
- **Response Time**: P95 < 800ms
- **Error Rate**: < 5%
- **A/B Test Lift**: > 5% revenue improvement

### Business Metrics

- **Model Accuracy**: MAE < 20 for demand forecasting
- **Price Stability**: < 15% variance maintained
- **Revenue Impact**: 25%+ improvement over static pricing
- **Feedback Loop**: > 100 records/week for retraining

---

🎉 **Congratulations!** Your Dynamic Pricing Agent is now live in production with full monitoring, A/B testing, and automated retraining capabilities.
