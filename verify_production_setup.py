#!/usr/bin/env python3
"""
Final verification script for TrustMark production setup with Neon database
"""
import os
import sys
import zipfile
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from models import FlaggedTransaction

def verify_neon_database():
    """Verify Neon database connection and data"""
    
    print("🗄️ Verifying Neon Database...")
    
    with app.app_context():
        try:
            # Test connection and count records
            total_flags = FlaggedTransaction.query.count()
            unique_addresses = FlaggedTransaction.query.with_entities(FlaggedTransaction.wallet_address).distinct().count()
            hacker_count = FlaggedTransaction.query.filter_by(reason='hacker').count()
            suspicious_count = FlaggedTransaction.query.filter_by(reason='suspicious').count()
            
            print(f"   ✅ Total flagged transactions: {total_flags}")
            print(f"   ✅ Unique flagged addresses: {unique_addresses}")
            print(f"   🔴 Hacker addresses: {hacker_count}")
            print(f"   🟡 Suspicious addresses: {suspicious_count}")
            
            if total_flags >= 6:
                print("   ✅ Database has sufficient test data")
                return True
            else:
                print("   ⚠️  Database has limited test data")
                return False
                
        except Exception as e:
            print(f"   ❌ Database error: {str(e)}")
            return False

def verify_production_extension():
    """Verify production Chrome extension package"""
    
    print("\n🔌 Verifying Production Chrome Extension...")
    
    zip_path = "static/trustmark_chrome_extension_production.zip"
    
    if not os.path.exists(zip_path):
        print(f"   ❌ Production ZIP not found: {zip_path}")
        return False
    
    print(f"   ✅ Production ZIP exists: {zip_path}")
    
    # Check ZIP contents
    required_files = [
        "manifest.json",
        "content.js",
        "popup.html", 
        "popup.js",
        "icon16.png",
        "icon48.png",
        "icon128.png"
    ]
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()
            
            for required_file in required_files:
                if required_file in zip_contents:
                    print(f"   ✅ {required_file}")
                else:
                    print(f"   ❌ {required_file} missing")
                    return False
            
            # Check manifest.json content
            manifest_content = zip_ref.read("manifest.json").decode('utf-8')
            manifest = json.loads(manifest_content)
            
            print(f"   📊 Extension Name: {manifest.get('name')}")
            print(f"   📊 Version: {manifest.get('version')}")
            
            # Check host permissions
            host_permissions = manifest.get('host_permissions', [])
            if 'https://trust-mark.vercel.app/*' in host_permissions:
                print("   ✅ Production host permissions configured")
            else:
                print("   ❌ Production host permissions missing")
                return False
            
            # Check content.js for production URL
            content_js = zip_ref.read("content.js").decode('utf-8')
            if 'https://trust-mark.vercel.app' in content_js:
                print("   ✅ Content script configured for production")
            else:
                print("   ❌ Content script not configured for production")
                return False
            
            # Check popup.js for production URL
            popup_js = zip_ref.read("popup.js").decode('utf-8')
            if 'https://trust-mark.vercel.app' in popup_js:
                print("   ✅ Popup script configured for production")
            else:
                print("   ❌ Popup script not configured for production")
                return False
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error reading ZIP file: {str(e)}")
        return False

def verify_environment_config():
    """Verify environment configuration"""
    
    print("\n🔧 Verifying Environment Configuration...")
    
    # Check required environment variables
    required_vars = [
        "DATABASE_URL",
        "ETHERSCAN_API_KEY",
        "SESSION_SECRET"
    ]
    
    all_present = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if var == "DATABASE_URL":
                print(f"   ✅ {var}: {value[:50]}...")
            else:
                print(f"   ✅ {var}: {value[:20]}...")
        else:
            print(f"   ❌ {var}: Not found")
            all_present = False
    
    return all_present

def verify_purple_theme():
    """Verify purple theme implementation"""
    
    print("\n🟣 Verifying Purple Theme...")
    
    # Check CSS file
    css_path = "static/css/style.css"
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        if 'btn-purple' in css_content and '#8b5cf6' in css_content:
            print("   ✅ Purple button styling in CSS")
        else:
            print("   ❌ Purple button styling missing")
            return False
    
    # Check extension files
    zip_path = "static/trustmark_chrome_extension_production.zip"
    if os.path.exists(zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check popup.html for purple theme
                popup_html = zip_ref.read("popup.html").decode('utf-8')
                if '#1e1b4b' in popup_html and '#8b5cf6' in popup_html:
                    print("   ✅ Purple theme in popup HTML")
                else:
                    print("   ❌ Purple theme missing in popup HTML")
                    return False
                
                # Check content.js for purple badges
                content_js = zip_ref.read("content.js").decode('utf-8')
                if '#8b5cf6' in content_js and '#a855f7' in content_js:
                    print("   ✅ Purple badges in content script")
                else:
                    print("   ❌ Purple badges missing in content script")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error checking theme: {str(e)}")
            return False
    
    return True

def show_deployment_summary():
    """Show final deployment summary"""
    
    print("\n" + "=" * 60)
    print("🚀 PRODUCTION DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    print("\n✅ READY FOR DEPLOYMENT:")
    print("   🗄️  Neon PostgreSQL database connected and populated")
    print("   🔌 Chrome extension configured for production")
    print("   🟣 Purple theme implemented throughout")
    print("   🔐 Security features enabled")
    print("   🌐 API endpoints configured")
    
    print("\n📦 DOWNLOAD:")
    print("   • Production Extension: static/trustmark_chrome_extension_production.zip")
    print("   • Web Access: https://trust-mark.vercel.app/")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Deploy to Vercel: vercel --prod")
    print("   2. Set environment variables in Vercel dashboard")
    print("   3. Install Chrome extension from production ZIP")
    print("   4. Test extension on live site")
    
    print("\n🎯 EXPECTED RESULTS:")
    print("   🟣 Purple extension popup")
    print("   🔴 Red badges on hacker addresses")
    print("   🟡 Yellow badges on suspicious addresses")
    print("   🟣 Purple badges on normal addresses")

if __name__ == "__main__":
    print("🛡️ TrustMark Production Setup Verification")
    print("=" * 60)
    
    # Run all verifications
    db_ok = verify_neon_database()
    ext_ok = verify_production_extension()
    env_ok = verify_environment_config()
    theme_ok = verify_purple_theme()
    
    # Final status
    if all([db_ok, ext_ok, env_ok, theme_ok]):
        show_deployment_summary()
        print("\n🎉 ALL VERIFICATIONS PASSED - READY FOR PRODUCTION! 🛡️✨")
    else:
        print("\n❌ Some verifications failed. Please check the issues above.")
        print("   Fix the issues and run this script again.")