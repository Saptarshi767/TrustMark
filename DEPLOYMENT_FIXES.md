# TrustMark Deployment Fixes

## Issues Fixed

### 1. **Runtime Configuration Error**
- **CRITICAL FIX**: Fixed invalid runtime specification in `vercel.json`
- Changed from `functions` with `runtime: "python3.11"` to `builds` with `use: "@vercel/python"`
- Added `runtime.txt` to specify Python version explicitly
- This was the main cause of deployment failure

### 2. **WSGI Entry Point**
- Created `app.py` as the main WSGI entry point for Vercel
- Updated `vercel.json` to use `functions` instead of `builds`

### 3. **Python Runtime**
- Updated Python runtime from 3.9 to 3.11 in `vercel.json`
- Added specific version pins to `requirements.txt`

### 4. **Database Initialization**
- Fixed database table creation for production deployment
- Added proper error handling for database initialization

### 5. **Package Structure**
- Added `utils/__init__.py` to make utils a proper Python package
- Fixed import paths and module structure

### 6. **Deployment Configuration**
- Created `.vercelignore` to exclude unnecessary files
- Added health check endpoint at `/health`
- Separated CORS and security headers properly

## Files Modified

- `vercel.json` - **CRITICAL**: Fixed runtime configuration error, updated to use proper `@vercel/python` runtime
- `runtime.txt` - **NEW** - Specifies Python 3.11 version explicitly
- `main.py` - Added app factory pattern, removed duplicate security headers
- `requirements.txt` - Added version pins for dependencies
- `app.py` - **NEW** - WSGI entry point for Vercel
- `utils/__init__.py` - **NEW** - Package initialization
- `.vercelignore` - **NEW** - Deployment exclusions

## Environment Variables Required in Vercel

Set these in your Vercel dashboard (not in vercel.json):

1. `ETHERSCAN_API_KEY` - Your Etherscan API key
2. `DATABASE_URL` - Your Neon PostgreSQL connection string  
3. `SESSION_SECRET` - A secure random string for sessions

**Note**: Don't use the `@variable_name` syntax in vercel.json - set these directly in Vercel dashboard.

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