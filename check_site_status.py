#!/usr/bin/env python3
"""
Site Status Checker for Google Safe Browsing Resolution

This script helps monitor your site's status and provides guidance
for resolving the Google Safe Browsing warning.
"""

import requests
import sys
from urllib.parse import quote

def check_site_accessibility():
    """Check if the site is accessible"""
    url = "https://trust-mark.vercel.app"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Site is accessible")
            return True
        else:
            print(f"❌ Site returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Site is not accessible: {e}")
        return False

def check_security_headers():
    """Check if security headers are properly set"""
    url = "https://trust-mark.vercel.app"
    try:
        response = requests.get(url, timeout=10)
        headers = response.headers
        
        security_checks = {
            'Strict-Transport-Security': 'HSTS header',
            'Content-Security-Policy': 'CSP header',
            'X-Content-Type-Options': 'Content type options',
            'X-Frame-Options': 'Frame options',
            'X-XSS-Protection': 'XSS protection'
        }
        
        print("\n🔒 Security Headers Check:")
        all_present = True
        for header, description in security_checks.items():
            if header in headers:
                print(f"✅ {description}: Present")
            else:
                print(f"❌ {description}: Missing")
                all_present = False
        
        return all_present
    except requests.RequestException as e:
        print(f"❌ Could not check security headers: {e}")
        return False

def check_verification_files():
    """Check if verification and security files are accessible"""
    base_url = "https://trust-mark.vercel.app"
    files_to_check = [
        ('/robots.txt', 'Robots.txt'),
        ('/sitemap.xml', 'Sitemap'),
        ('/.well-known/security.txt', 'Security.txt'),
        ('/googleb5af89e05601a259.html', 'Google verification'),
        ('/security-policy', 'Security policy page')
    ]
    
    print("\n📄 Verification Files Check:")
    all_accessible = True
    
    for path, description in files_to_check:
        try:
            response = requests.get(f"{base_url}{path}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {description}: Accessible")
            else:
                print(f"❌ {description}: Status {response.status_code}")
                all_accessible = False
        except requests.RequestException:
            print(f"❌ {description}: Not accessible")
            all_accessible = False
    
    return all_accessible

def print_next_steps():
    """Print next steps for resolving the Safe Browsing issue"""
    print("\n📋 Next Steps for Safe Browsing Resolution:")
    print("\n1. Check Google Safe Browsing Status:")
    print("   Visit: https://transparencyreport.google.com/safe-browsing/search")
    print("   Enter: https://trust-mark.vercel.app")
    
    print("\n2. Submit Review Request:")
    print("   Visit: https://safebrowsing.google.com/safebrowsing/report_error/")
    print("   Submit your URL for re-evaluation")
    
    print("\n3. Add to Google Search Console:")
    print("   - Add your site to Google Search Console")
    print("   - Verify ownership using the verification file")
    print("   - Check Security Issues section")
    print("   - Use 'Request Review' if available")
    
    print("\n4. Contact Vercel Support:")
    print("   - Create a support ticket about the Safe Browsing issue")
    print("   - Mention this affects legitimate projects")
    print("   - Ask about IP reputation issues")
    
    print("\n5. Monitor Progress:")
    print("   - Check your site daily in different browsers")
    print("   - Test in incognito mode")
    print("   - Monitor Google Search Console for updates")

def print_review_template():
    """Print template for Google Safe Browsing review request"""
    print("\n📝 Template for Google Safe Browsing Review:")
    print("=" * 60)
    print("""
Subject: False Positive Review Request - TrustMark Blockchain Analysis Tool

Dear Google Safe Browsing Team,

I am requesting a review of my website https://trust-mark.vercel.app 
which has been incorrectly flagged as dangerous.

Site Details:
- Purpose: Educational blockchain analysis and Ethereum address classification tool
- Technology: Flask web application with read-only blockchain data analysis
- No malicious content: The site only analyzes public blockchain data from Etherscan API
- No user data collection: We don't store private keys or personal information
- Educational focus: Clearly marked as a demonstration platform

The site appears to be a false positive, possibly due to:
1. Being hosted on Vercel's shared infrastructure
2. Recent deployment triggering automated scanning
3. Use of Web3/MetaMask integration being misidentified

I have implemented comprehensive security measures including:
- Strict Content Security Policy
- Security headers (HSTS, X-Frame-Options, etc.)
- Input validation and sanitization
- Rate limiting protection
- Security.txt file for transparency

The site has proper verification files:
- Google Search Console verification: /googleb5af89e05601a259.html
- Security policy: /security-policy
- Robots.txt and sitemap.xml for proper indexing

Please review and remove this site from the Safe Browsing blocklist.

Thank you for your consideration.
""")
    print("=" * 60)

def main():
    """Main function to run all checks"""
    print("🔍 TrustMark Site Status Check")
    print("=" * 40)
    
    # Run all checks
    site_accessible = check_site_accessibility()
    headers_ok = check_security_headers()
    files_ok = check_verification_files()
    
    # Summary
    print("\n📊 Summary:")
    if site_accessible and headers_ok and files_ok:
        print("✅ All checks passed! Your site is properly configured.")
        print("   The Safe Browsing warning is likely a false positive.")
    else:
        print("⚠️  Some issues found. Please address them before submitting review.")
    
    # Always show next steps
    print_next_steps()
    print_review_template()

if __name__ == "__main__":
    main()