#!/usr/bin/env python3
"""
Script to check Google Safe Browsing status and provide guidance
for resolving false positive warnings.
"""

import requests
import json
import webbrowser
from urllib.parse import quote

def check_site_status():
    """Check various security and reputation services"""
    
    site_url = "https://trust-mark.vercel.app"
    
    print("🔍 TrustMark Security Status Checker")
    print("=" * 50)
    
    # 1. Check if site is accessible
    print("\n1. Testing site accessibility...")
    try:
        response = requests.get(site_url, timeout=10)
        if response.status_code == 200:
            print("✅ Site is accessible (HTTP 200)")
        else:
            print(f"⚠️  Site returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Site accessibility error: {e}")
    
    # 2. Check security headers
    print("\n2. Checking security headers...")
    try:
        response = requests.get(site_url, timeout=10)
        headers = response.headers
        
        security_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy', 
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        
        for header in security_headers:
            if header in headers:
                print(f"✅ {header}: Present")
            else:
                print(f"❌ {header}: Missing")
                
    except Exception as e:
        print(f"❌ Header check error: {e}")
    
    # 3. Provide links for manual checks
    print("\n3. Manual Security Checks")
    print("-" * 30)
    
    checks = [
        {
            'name': 'Google Safe Browsing Transparency Report',
            'url': f'https://transparencyreport.google.com/safe-browsing/search?url={quote(site_url)}',
            'description': 'Check current Safe Browsing status'
        },
        {
            'name': 'Google Safe Browsing Review Request',
            'url': f'https://safebrowsing.google.com/safebrowsing/report_error/?url={quote(site_url)}',
            'description': 'Submit review request if flagged incorrectly'
        },
        {
            'name': 'SSL Labs SSL Test',
            'url': f'https://www.ssllabs.com/ssltest/analyze.html?d=trust-mark.vercel.app',
            'description': 'Check SSL/TLS configuration'
        },
        {
            'name': 'Security Headers Test',
            'url': f'https://securityheaders.com/?q={quote(site_url)}',
            'description': 'Analyze security headers implementation'
        }
    ]
    
    for i, check in enumerate(checks, 1):
        print(f"\n{i}. {check['name']}")
        print(f"   Purpose: {check['description']}")
        print(f"   URL: {check['url']}")
    
    # 4. Provide action steps
    print("\n4. Recommended Actions")
    print("-" * 25)
    
    actions = [
        "✅ Check Google Safe Browsing status using link #1 above",
        "✅ If flagged, submit review request using link #2 above", 
        "✅ Contact Vercel support about potential IP reputation issues",
        "✅ Add site to Google Search Console for monitoring",
        "✅ Verify SSL configuration is optimal using link #3",
        "✅ Confirm security headers are properly set using link #4"
    ]
    
    for action in actions:
        print(f"  {action}")
    
    # 5. Contact templates
    print("\n5. Contact Information")
    print("-" * 22)
    
    print("\nGoogle Safe Browsing Review Template:")
    print("-" * 40)
    template = f"""
Subject: False Positive Review Request - TrustMark Educational Tool

Dear Google Safe Browsing Team,

I am requesting a review of my website {site_url} which has been incorrectly flagged.

Site Details:
- Purpose: Educational blockchain analysis tool for Ethereum addresses
- Technology: Flask web application with read-only blockchain data analysis  
- Content: Only analyzes public data from Etherscan API
- Security: Implements HTTPS, CSP, security headers, input validation
- Educational: Clearly marked as demonstration platform

This appears to be a false positive. The site contains no malicious content and serves an educational purpose in blockchain technology.

Please review and remove from Safe Browsing blocklist.

Thank you.
"""
    print(template)
    
    print("\nVercel Support Template:")
    print("-" * 25)
    vercel_template = f"""
Subject: Google Safe Browsing False Positive - Vercel Domain

Hello Vercel Support,

My project at {site_url} is being flagged by Google Safe Browsing as dangerous.

This is a legitimate educational blockchain analysis tool with no malicious content.
The false positive may be due to shared IP reputation issues.

Could you please:
1. Check for any known IP reputation problems affecting vercel.app
2. Advise on best practices for avoiding false positives
3. Escalate to Google if this is a platform-wide issue

Thank you for your assistance.
"""
    print(vercel_template)

def open_links():
    """Open important links in browser"""
    
    site_url = "https://trust-mark.vercel.app"
    
    links = [
        f'https://transparencyreport.google.com/safe-browsing/search?url={quote(site_url)}',
        f'https://safebrowsing.google.com/safebrowsing/report_error/?url={quote(site_url)}',
        'https://search.google.com/search-console',
        'https://vercel.com/support'
    ]
    
    print("Opening important links in your browser...")
    for link in links:
        webbrowser.open(link)
        print(f"Opened: {link}")

if __name__ == "__main__":
    check_site_status()
    
    print("\n" + "=" * 50)
    print("Would you like to open the important links in your browser? (y/n): ", end="")
    
    try:
        choice = input().lower().strip()
        if choice in ['y', 'yes']:
            open_links()
        else:
            print("You can manually visit the URLs listed above.")
    except KeyboardInterrupt:
        print("\nExiting...")
    
    print("\n🚀 Next steps:")
    print("1. Check the Safe Browsing status using the links above")
    print("2. Submit review requests if your site is flagged")
    print("3. Contact Vercel support using the template provided")
    print("4. Monitor for resolution over the next few days")
    print("\nGood luck resolving the false positive! 🍀")