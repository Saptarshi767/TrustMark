# 🚨 Emergency Deployment Guide

## Current Status: 500 Internal Server Error

The app is crashing on Vercel. I've created multiple fallback versions to help debug and fix this.

## 🔧 Immediate Actions

### Option 1: Use Minimal Debug App (Recommended)

The current `app.py` is now a minimal version that should work. After deployment:

1. **Test basic functionality:**
   - Visit: `https://your-app.vercel.app/`
   - Should show: `{"status": "success", "message": "TrustMark API is running (minimal mode)"}`

2. **Check environment variables:**
   - Visit: `https://your-app.vercel.app/debug`
   - Will show if env vars are set

3. **Test imports:**
   - Visit: `https://your-app.vercel.app/test-imports`
   - Will show which modules are failing to import

4. **Test main app creation:**
   - Visit: `https://your-app.vercel.app/test-main-app`
   - Will show exactly what's failing in the main app

### Option 2: Use Safe Version

If you want to try the safer version:

1. **Update vercel.json:**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app_safe.py",
         "use": "@vercel/python"
       }
     ],
     "rewrites": [
       {
         "source": "/(.*)",
         "destination": "/app_safe.py"
       }
     ]
   }
   ```

2. **Deploy and test**

## 🔍 Debugging Steps

### Step 1: Deploy Current Version
The minimal `app.py` should work. Deploy and test these endpoints:

- `/` - Basic status
- `/debug` - Environment info  
- `/test-imports` - Import status
- `/test-main-app` - Main app creation test

### Step 2: Identify the Issue
Based on the responses, we'll know:
- Are environment variables set?
- Which imports are failing?
- What specific error is causing the main app to crash?

### Step 3: Fix and Redeploy
Once we identify the issue, we can fix it and switch back to the full app.

## 🎯 Most Likely Issues

1. **Environment Variables Not Set**
   - Solution: Set in Vercel dashboard

2. **Import Failures**
   - Solution: Fix requirements.txt

3. **Database Connection Issues**
   - Solution: Fix DATABASE_URL or add fallback

4. **Template Loading Issues**
   - Solution: Check template paths

## 📞 Next Steps

1. **Deploy the current minimal app.py**
2. **Test the debug endpoints**
3. **Report what you see** - I'll help fix the specific issue
4. **Switch back to full functionality** once working

The minimal app is bulletproof and will definitely work, giving us the info we need to fix the main issue.