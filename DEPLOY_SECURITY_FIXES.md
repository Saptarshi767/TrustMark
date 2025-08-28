# 🛡️ Deploy Security Fixes for TrustMark

## 🚨 **Chrome Security Warning Fix**

The Chrome security warning was caused by **overly permissive CORS policy** (`Access-Control-Allow-Origin: *`). 

## ✅ **Security Fixes Applied**

1. **Restricted CORS Policy** - Only allows requests from:
   - `https://trust-mark.vercel.app` (your domain)
   - `chrome-extension://` (Chrome extensions)

2. **Added Security Headers**:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `X-XSS-Protection: 1; mode=block`
   - `Strict-Transport-Security` for HTTPS
   - `Content-Security-Policy` to prevent XSS

3. **Updated Extension Package**:
   - Fixed backend URL consistency
   - Created: `static/trustmark_chrome_extension_production.zip`

## 🚀 **Deployment Steps**

### Option 1: Vercel CLI (Recommended)
```bash
# Initialize Vercel project (if not done)
vercel

# Deploy to production
vercel --prod
```

### Option 2: Vercel Dashboard
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Import your GitHub repository
3. Deploy automatically

### Option 3: Git Push (if connected)
```bash
git add .
git commit -m "Fix Chrome security warning - restrict CORS policy"
git push origin main
```

## 🔧 **Environment Variables**

Make sure these are set in Vercel dashboard:
- `DATABASE_URL` - Your Neon PostgreSQL URL
- `ETHERSCAN_API_KEY` - Your Etherscan API key  
- `SESSION_SECRET` - Random secret for sessions

## 📦 **Chrome Extension Installation**

1. Download: `static/trustmark_chrome_extension_production.zip`
2. Extract the ZIP file
3. Open Chrome → Extensions → Developer mode ON
4. Click "Load unpacked" → Select extracted folder
5. Test on https://trust-mark.vercel.app/

## 🧪 **Testing the Fix**

After deployment:

1. **Visit your site**: https://trust-mark.vercel.app/
2. **Chrome should NOT show security warning** ✅
3. **Install the extension** from production ZIP
4. **Test extension** on live site

## 🔍 **Verify Security**

Run this to test the deployed version:
```bash
python verify_security_fixes.py
```

Expected results:
- ✅ CORS restricted (no more wildcard)
- ✅ Security headers present
- ✅ Extension works with new security

## ⚠️ **If Chrome Still Shows Warning**

1. **Clear browser cache** and cookies
2. **Wait 5-10 minutes** for DNS propagation
3. **Check browser console** for errors
4. **Verify deployment** completed successfully

## 🎉 **Success Indicators**

- Chrome loads your site without security warning
- Extension popup shows purple theme
- Address badges appear on websites
- API calls work from extension

---

**The security warning will disappear once these fixes are deployed!** 🔒✨