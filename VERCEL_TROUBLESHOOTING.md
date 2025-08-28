# 🔧 Vercel Deployment Troubleshooting

## Current Issue: 500 INTERNAL_SERVER_ERROR

The app deployed successfully but is crashing at runtime. This is typically caused by:

### 1. **Missing Environment Variables** (Most Likely)

**Check if environment variables are set in Vercel:**

1. Go to your Vercel dashboard
2. Select your TrustMark project
3. Go to **Settings** → **Environment Variables**
4. Ensure these are set for **Production**:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql://neondb_owner:npg_eKM8SwmtgyJ7@ep-long-dream-a82i5ypq-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require` |
| `ETHERSCAN_API_KEY` | `IRI57XAY533YXUSDTU9J9TU6ZY9B4IWSRS` |
| `SESSION_SECRET` | `trustmark-production-secret-key` |

**After adding variables:**
- Redeploy the project (or trigger a new deployment)

### 2. **Database Connection Issues**

**Test the health endpoint:**
- Visit: `https://your-app.vercel.app/health`
- This will show database connection status and environment variables

**If database connection fails:**
- Verify the DATABASE_URL is correct
- Check if Neon database is accessible from Vercel's servers
- Test the connection string manually

### 3. **Template Loading Issues**

**Test the root endpoint:**
- Visit: `https://your-app.vercel.app/`
- If templates fail to load, you'll see a JSON response with error details

### 4. **Import/Dependency Issues**

**Check Vercel function logs:**
1. Go to Vercel dashboard → Functions tab
2. Click on your function
3. Check the logs for import errors

## 🔍 Debugging Steps

### Step 1: Check Environment Variables
Visit: `https://your-app.vercel.app/health`

Expected response:
```json
{
  "status": "healthy",
  "message": "TrustMark API is running",
  "database": "connected",
  "environment": {
    "DATABASE_URL": "set",
    "ETHERSCAN_API_KEY": "set", 
    "SESSION_SECRET": "set"
  }
}
```

### Step 2: Test Basic Functionality
If health check passes, test:
- `https://your-app.vercel.app/` (home page)
- `https://your-app.vercel.app/login` (login page)
- `https://your-app.vercel.app/api/flagged_addresses` (API endpoint)

### Step 3: Check Vercel Logs
1. Go to Vercel dashboard
2. Click on your deployment
3. Check the **Functions** tab for error logs
4. Look for specific error messages

## 🚀 Quick Fixes

### Fix 1: Redeploy with Environment Variables
```bash
# After setting env vars in Vercel dashboard
git commit --allow-empty -m "Trigger redeploy"
git push
```

### Fix 2: Test Database Connection
Use the Neon dashboard to verify:
- Database is running
- Connection string is correct
- No connection limits reached

### Fix 3: Fallback to SQLite (Emergency)
If PostgreSQL fails, the app will automatically fall back to SQLite.

## 📞 Next Steps

1. **Set environment variables** in Vercel dashboard
2. **Redeploy** the application
3. **Test** the `/health` endpoint
4. **Check logs** if still failing

The app works perfectly locally, so the issue is environment-specific to Vercel.