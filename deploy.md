# 🚀 TrustMark Deployment Guide

## 📋 Prerequisites
- GitHub account
- Vercel account (free)
- Etherscan API key (already provided: `IRI57XAY533YXUSDTU9J9TU6ZY9B4IWSRS`)

---

## 🗄️ Step 1: Create Free Postgres Database

### Option A: Neon (Recommended - Best Free Tier)
1. **Visit** [neon.tech](https://neon.tech)
2. **Sign up** with GitHub or Google
3. **Create New Project**:
   - Project name: `trustmark-db`
   - Region: Choose closest to you
   - Click "Create Project"
4. **Copy Connection String**:
   - Go to "Connection Details"
   - Copy the connection string (looks like: `postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require`)

### Option B: Supabase (Alternative)
1. **Visit** [supabase.com](https://supabase.com)
2. **Sign up** and create new project
3. **Go to** Settings → Database
4. **Copy** the connection string

### Option C: Railway (Alternative)
1. **Visit** [railway.app](https://railway.app)
2. **Sign up** and create new project
3. **Add** Postgres database
4. **Copy** the connection string

---

## 🔧 Step 2: Generate Session Secret
Run this command to generate a secure session secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output (64-character hex string).

---

## 📤 Step 3: Deploy to Vercel

### 3.1 Push to GitHub
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 3.2 Deploy on Vercel
1. **Visit** [vercel.com](https://vercel.com)
2. **Sign up/Login** with GitHub
3. **Import Project**:
   - Click "New Project"
   - Import your GitHub repository
   - Framework Preset: Other
   - Root Directory: `./`
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`

### 3.3 Set Environment Variables
In Vercel dashboard, go to your project → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `ETHERSCAN_API_KEY` | `IRI57XAY533YXUSDTU9J9TU6ZY9B4IWSRS` |
| `SESSION_SECRET` | `[Your generated secret from Step 2]` |
| `POSTGRES_URL` | `[Your Postgres connection string from Step 1]` |

### 3.4 Deploy
Click "Deploy" and wait for deployment to complete.

---

## 🔗 Step 4: Update Chrome Extension

### 4.1 Get Your Vercel URL
After deployment, Vercel will give you a URL like:
`https://your-project-name.vercel.app`

### 4.2 Update Extension Files
Update these two files with your Vercel URL:

**File: `chrome_extension/content.js`**
```javascript
const BACKEND_URL = 'https://your-project-name.vercel.app';
```

**File: `chrome_extension/popup.js`**
```javascript
const BACKEND_URL = 'https://your-project-name.vercel.app';
```

### 4.3 Recreate Extension ZIP
```bash
cd chrome_extension
zip -r ../static/chrome_extension.zip .
cd ..
```

---

## 🧪 Step 5: Test Your Deployment

### 5.1 Test Web App
1. Visit your Vercel URL
2. Test login with an Ethereum address
3. Test dashboard functionality
4. Test transaction flagging
5. Test search functionality

### 5.2 Test Chrome Extension
1. Download the updated extension ZIP
2. Install in Chrome (Developer mode)
3. Test on pages with Ethereum addresses
4. Verify it connects to your deployed backend

---

## ✅ Step 6: Verify Everything Works

### Checklist:
- [ ] Web app loads on Vercel URL
- [ ] Can login with Ethereum address
- [ ] Dashboard shows transactions
- [ ] Can flag transactions
- [ ] Flagged transactions persist in database
- [ ] Chrome extension connects to backend
- [ ] Extension highlights addresses correctly
- [ ] Search functionality works
- [ ] Statistics page works

---

## 🎉 Success!
Your TrustMark app is now live and ready for public use!

**Your app URL:** `https://your-project-name.vercel.app`

**Users can:**
- Visit your app and analyze Ethereum addresses
- Download and install the Chrome extension
- Flag suspicious transactions
- View real-time reputation data

---

## 🔧 Troubleshooting

### Common Issues:
1. **Database Connection Error**: Check your `POSTGRES_URL` format
2. **Etherscan API Errors**: Verify your API key is correct
3. **Extension Not Working**: Ensure `BACKEND_URL` is updated correctly
4. **Cold Start Issues**: First request might be slow (normal for serverless)

### Support:
- Check Vercel logs in dashboard
- Verify environment variables are set correctly
- Test locally first if needed 