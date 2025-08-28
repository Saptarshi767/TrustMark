#!/usr/bin/env python3
"""
Final deployment verification script
"""
import os
import sys
from dotenv import load_dotenv

def main():
    print("🚀 TrustMark Deployment Verification")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check critical files
    critical_files = [
        'app.py',
        'main.py', 
        'models.py',
        'requirements.txt',
        'vercel.json',
        'utils/__init__.py',
        'utils/etherscan_api.py',
        'utils/classifier.py',
        'templates/index.html'
    ]
    
    print("📁 Checking critical files...")
    missing_files = []
    for file in critical_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            missing_files.append(file)
    
    # Check environment variables
    print("\n🔐 Checking environment variables...")
    env_vars = ['ETHERSCAN_API_KEY', 'DATABASE_URL', 'SESSION_SECRET']
    missing_env = []
    for var in env_vars:
        if os.environ.get(var):
            print(f"  ✓ {var}")
        else:
            print(f"  ✗ {var} - MISSING")
            missing_env.append(var)
    
    # Test app creation
    print("\n🏗️  Testing app creation...")
    try:
        from app import app
        print("  ✓ App created successfully")
        app_ok = True
    except Exception as e:
        print(f"  ✗ App creation failed: {e}")
        app_ok = False
    
    # Summary
    print("\n📊 Summary:")
    if missing_files:
        print(f"  ❌ Missing files: {len(missing_files)}")
    if missing_env:
        print(f"  ❌ Missing env vars: {len(missing_env)}")
    if not app_ok:
        print("  ❌ App creation failed")
    
    if not missing_files and not missing_env and app_ok:
        print("  🎉 All checks passed! Ready for deployment.")
        print("\n📝 Next steps:")
        print("  1. Commit all changes to git")
        print("  2. Push to your repository")
        print("  3. Deploy to Vercel")
        print("  4. Set environment variables in Vercel dashboard")
        return True
    else:
        print("  ❌ Some issues found. Please fix before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)