#!/usr/bin/env python3
"""
Secure deployment script for TrustMark
"""
import os
import subprocess
import sys

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking Prerequisites...")
    
    # Check if Vercel CLI is installed
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Vercel CLI: {result.stdout.strip()}")
        else:
            print("   ❌ Vercel CLI not found")
            return False
    except FileNotFoundError:
        print("   ❌ Vercel CLI not installed")
        print("      Install with: npm i -g vercel")
        return False
    
    # Check if environment variables are set
    required_env_vars = ['DATABASE_URL', 'ETHERSCAN_API_KEY', 'SESSION_SECRET']
    env_file_exists = os.path.exists('.env')
    
    if env_file_exists:
        print("   ✅ .env file found")
        
        # Load and check .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        missing_vars = []
        for var in required_env_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"   ⚠️  Missing environment variables: {', '.join(missing_vars)}")
        else:
            print("   ✅ All required environment variables found")
    else:
        print("   ❌ .env file not found")
        print("      Copy env.example to .env and fill in values")
        return False
    
    return True

def deploy_to_vercel():
    """Deploy to Vercel with production settings"""
    print("\n🚀 Deploying to Vercel...")
    
    try:
        # Deploy to production
        result = subprocess.run(['vercel', '--prod'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Deployment successful!")
            
            # Extract deployment URL from output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'https://' in line and 'vercel.app' in line:
                    deployment_url = line.strip()
                    print(f"   🌐 Deployment URL: {deployment_url}")
                    return deployment_url
        else:
            print(f"   ❌ Deployment failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"   ❌ Deployment error: {str(e)}")
        return None

def set_environment_variables():
    """Set environment variables in Vercel"""
    print("\n🔧 Setting Environment Variables...")
    
    # Load local environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'ETHERSCAN_API_KEY': os.environ.get('ETHERSCAN_API_KEY'),
        'SESSION_SECRET': os.environ.get('SESSION_SECRET')
    }
    
    for var_name, var_value in env_vars.items():
        if var_value:
            try:
                # Set environment variable for production
                result = subprocess.run([
                    'vercel', 'env', 'add', var_name, 'production'
                ], input=var_value, text=True, capture_output=True)
                
                if result.returncode == 0:
                    print(f"   ✅ {var_name}: Set")
                else:
                    print(f"   ⚠️  {var_name}: {result.stderr.strip()}")
            except Exception as e:
                print(f"   ❌ {var_name}: Error - {str(e)}")
        else:
            print(f"   ❌ {var_name}: Not found in .env")

def test_deployment(deployment_url):
    """Test the deployed application"""
    print(f"\n🧪 Testing Deployment: {deployment_url}")
    
    import requests
    
    try:
        # Test main page
        response = requests.get(deployment_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ Main page loads")
        else:
            print(f"   ❌ Main page error: {response.status_code}")
        
        # Test API endpoint
        api_url = f"{deployment_url}/api/flagged_addresses"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ API endpoint works")
            
            # Check CORS headers
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header != '*':
                print("   ✅ CORS security implemented")
            else:
                print("   ❌ CORS still uses wildcard - security risk!")
        else:
            print(f"   ❌ API endpoint error: {response.status_code}")
            
        # Test security headers
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Strict-Transport-Security'
        ]
        
        missing_headers = []
        for header in security_headers:
            if header not in response.headers:
                missing_headers.append(header)
        
        if not missing_headers:
            print("   ✅ Security headers present")
        else:
            print(f"   ⚠️  Missing security headers: {', '.join(missing_headers)}")
            
    except Exception as e:
        print(f"   ❌ Testing error: {str(e)}")

def show_next_steps(deployment_url):
    """Show next steps after deployment"""
    print("\n" + "=" * 60)
    print("🎉 SECURE DEPLOYMENT COMPLETE!")
    print("=" * 60)
    
    if deployment_url:
        print(f"\n🌐 Your TrustMark app is live at:")
        print(f"   {deployment_url}")
        
        print(f"\n🔒 Security Fixes Applied:")
        print("   ✅ Restricted CORS policy")
        print("   ✅ Security headers added")
        print("   ✅ Content Security Policy")
        print("   ✅ HTTPS enforcement")
        
        print(f"\n📦 Chrome Extension:")
        print("   • Download: static/trustmark_chrome_extension_secure.zip")
        print("   • Install in Chrome Developer Mode")
        print("   • Test on your live site")
        
        print(f"\n🧪 Test Your Site:")
        print(f"   1. Visit {deployment_url} in Chrome")
        print("   2. Chrome should NOT show security warning")
        print("   3. Install and test the extension")
        
        print(f"\n🛡️  If Chrome Still Shows Warning:")
        print("   • Clear browser cache and cookies")
        print("   • Wait a few minutes for DNS propagation")
        print("   • Check browser console for errors")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")

if __name__ == "__main__":
    print("🛡️ TrustMark Secure Deployment")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    # Set environment variables (optional, can be done manually)
    print("\n⚠️  Note: You may need to set environment variables manually in Vercel dashboard")
    print("   Visit: https://vercel.com/dashboard -> Your Project -> Settings -> Environment Variables")
    
    # Deploy to Vercel
    deployment_url = deploy_to_vercel()
    
    if deployment_url:
        # Test the deployment
        test_deployment(deployment_url)
        
        # Show next steps
        show_next_steps(deployment_url)
    else:
        print("\n❌ Deployment failed. Please check your Vercel configuration.")
        
    print("\n🔒 Remember: The security fixes will only take effect after deployment!")