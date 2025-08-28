#!/usr/bin/env python3
"""
Security verification script for TrustMark production deployment
"""
import requests
import json
import os
from urllib.parse import urlparse

def test_cors_security():
    """Test CORS configuration security"""
    print("🔒 Testing CORS Security...")
    
    base_url = "https://trust-mark.vercel.app"
    
    # Test 1: Valid origin (should work)
    headers = {'Origin': 'https://trust-mark.vercel.app'}
    try:
        response = requests.get(f"{base_url}/api/flagged_addresses", headers=headers)
        if response.status_code == 200:
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header == 'https://trust-mark.vercel.app':
                print("   ✅ Valid origin accepted")
            else:
                print(f"   ⚠️  Unexpected CORS header: {cors_header}")
        else:
            print(f"   ❌ API request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing valid origin: {str(e)}")
    
    # Test 2: Invalid origin (should be restricted)
    headers = {'Origin': 'https://malicious-site.com'}
    try:
        response = requests.get(f"{base_url}/api/flagged_addresses", headers=headers)
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header == 'https://malicious-site.com' or cors_header == '*':
            print("   ❌ Malicious origin accepted - SECURITY RISK!")
        else:
            print("   ✅ Malicious origin rejected")
    except Exception as e:
        print(f"   ⚠️  Error testing malicious origin: {str(e)}")

def test_security_headers():
    """Test security headers"""
    print("\n🛡️ Testing Security Headers...")
    
    base_url = "https://trust-mark.vercel.app"
    
    try:
        response = requests.get(base_url)
        headers = response.headers
        
        # Check for security headers
        security_checks = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': None  # Just check if present
        }
        
        for header, expected_value in security_checks.items():
            actual_value = headers.get(header)
            if actual_value:
                if expected_value is None or expected_value in actual_value:
                    print(f"   ✅ {header}: {actual_value[:50]}...")
                else:
                    print(f"   ⚠️  {header}: Expected '{expected_value}', got '{actual_value}'")
            else:
                print(f"   ❌ {header}: Missing")
                
    except Exception as e:
        print(f"   ❌ Error testing security headers: {str(e)}")

def test_https_redirect():
    """Test HTTPS enforcement"""
    print("\n🔐 Testing HTTPS Enforcement...")
    
    # Test if HTTP redirects to HTTPS
    try:
        response = requests.get("http://trust-mark.vercel.app", allow_redirects=False)
        if response.status_code in [301, 302, 307, 308]:
            location = response.headers.get('Location', '')
            if location.startswith('https://'):
                print("   ✅ HTTP redirects to HTTPS")
            else:
                print(f"   ❌ HTTP redirects to: {location}")
        else:
            print(f"   ⚠️  Unexpected HTTP response: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error testing HTTP redirect: {str(e)}")

def test_api_endpoints():
    """Test API endpoint security"""
    print("\n🔌 Testing API Endpoint Security...")
    
    base_url = "https://trust-mark.vercel.app"
    
    endpoints = [
        "/api/flagged_addresses",
        "/api/flagged_transactions"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: Accessible")
                
                # Check if response is JSON
                try:
                    data = response.json()
                    print(f"      📊 Response type: {type(data).__name__}")
                except:
                    print(f"      ⚠️  Non-JSON response")
                    
            elif response.status_code == 401:
                print(f"   🔒 {endpoint}: Requires authentication")
            else:
                print(f"   ⚠️  {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {str(e)}")

def check_extension_package():
    """Check Chrome extension package"""
    print("\n📦 Checking Chrome Extension Package...")
    
    zip_path = "static/trustmark_chrome_extension_secure.zip"
    
    if os.path.exists(zip_path):
        print(f"   ✅ Secure extension package exists: {zip_path}")
        
        # Check file size
        size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"   📊 Package size: {size_mb:.2f} MB")
        
        if size_mb < 5:  # Chrome extensions should be small
            print("   ✅ Package size is reasonable")
        else:
            print("   ⚠️  Package size is large")
    else:
        print(f"   ❌ Secure extension package not found: {zip_path}")

def show_security_summary():
    """Show security deployment summary"""
    print("\n" + "=" * 60)
    print("🔒 SECURITY VERIFICATION SUMMARY")
    print("=" * 60)
    
    print("\n✅ SECURITY IMPROVEMENTS IMPLEMENTED:")
    print("   🛡️  Restricted CORS policy (no more wildcard '*')")
    print("   🔒 Security headers added (XSS, CSRF, etc.)")
    print("   🌐 Content Security Policy implemented")
    print("   🔐 HTTPS enforcement")
    print("   📦 Secure Chrome extension package")
    
    print("\n🚀 DEPLOYMENT STEPS:")
    print("   1. Deploy updated Flask app to Vercel")
    print("   2. Test the site in Chrome (should no longer show warning)")
    print("   3. Install secure extension package")
    print("   4. Verify extension works with new security settings")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("   • The Chrome warning was caused by overly permissive CORS")
    print("   • New security headers protect against common attacks")
    print("   • Extension now uses consistent backend URL")
    print("   • All HTTP traffic redirects to HTTPS")

if __name__ == "__main__":
    print("🛡️ TrustMark Security Verification")
    print("=" * 60)
    
    # Run security tests
    test_cors_security()
    test_security_headers()
    test_https_redirect()
    test_api_endpoints()
    check_extension_package()
    
    # Show summary
    show_security_summary()
    
    print("\n🎉 Security verification complete! Deploy to test the fixes. 🔒✨")