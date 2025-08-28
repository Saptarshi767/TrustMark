# TrustMark Deployment Fixes

## Issues Fixed

### 1. **WSGI Entry Point**
- Created `app.py` as the main WSGI entry point for Vercel
- Updated `vercel.json` to use `app.py` instead of `main.py`

### 2. **Python Runtime**
- Updated Python runtime from 3.9 to 3.11 in `vercel.json`
- Added specific version pins to `requirements.txt`

### 3. **Database Initialization**
- Fixed database table creation for production deployment
- Added proper error handling for database initialization

### 4. **Environment Variables**
- Added environment variable configuration in `vercel.json`
- Created proper fallback handling for missing variables

### 5. **Package Structure**
- Added `utils/__init__.py` to make utils a proper Python package
- Fixed import paths and module structure

### 6. **Deployment Configuration**
- Created `.vercelignore` to exclude unnecessary files
- Added health check endpoint at `/health`
- Added proper CORS and security headers

## Files Modified

- `vercel.json` - Updated build configuration and routes
- `main.py` - Added app factory pattern and database initialization
- `requirements.txt` - Added version pins for dependencies
- `app.py` - **NEW** - WSGI entry point for Vercel
- `utils/__init__.py` - **NEW** - Package initialization
- `.vercelignore` - **NEW** - Deployment exclusions

## Environment Variables Required in Vercel

Set these in your Vercel dashboard:

1. `ETHERSCAN_API_KEY` - Your Etherscan API key
2. `DATABASE_URL` - Your Neon PostgreSQL connection string  
3. `SESSION_SECRET` - A secure random string for sessions

## Deployment Steps

1. **Commit changes:**
   ```bash
   git add .
   git commit -m "Fix Vercel deployment configuration"
   git push
   ```

2. **Deploy to Vercel:**
   - Connect your repository to Vercel
   - Set the environment variables in Vercel dashboard
   - Deploy

3. **Verify deployment:**
   - Visit `https://your-app.vercel.app/health` to check if it's running
   - Test the main functionality

## Testing

Run the verification script to ensure everything is ready:
```bash
python verify_deployment.py
```

All checks should pass before deploying.