#!/usr/bin/env python3
"""
Script to help with Google Safe Browsing review submission
"""

import webbrowser
import time

def main():
    print("🔍 Google Safe Browsing Review Helper")
    print("=" * 50)
    
    site_url = "https://trust-mark.vercel.app"
    
    print(f"Site URL: {site_url}")
    print()
    
    # Step 1: Check current status
    print("Step 1: Check your site's current status")
    print("-" * 40)
    transparency_url = f"https://transparencyreport.google.com/safe-browsing/search?url={site_url}"
    print(f"Opening: {transparency_url}")
    webbrowser.open(transparency_url)
    
    input("Press Enter after checking the status...")
    
    # Step 2: Submit review request
    print("\nStep 2: Submit review request")
    print("-" * 40)
    review_url = "https://safebrowsing.google.com/safebrowsing/report_error/"
    print(f"Opening: {review_url}")
    webbrowser.open(review_url)
    
    print("\nWhen submitting the review, use this information:")
    print("=" * 50)
    print(f"URL: {site_url}")
    print("Category: Website incorrectly blocked")
    print("Description:")
    print("""
This is a legitimate educational blockchain analysis platform that helps users 
understand Ethereum transaction patterns. The site:

- Only analyzes public blockchain data from Etherscan API
- Does not handle private keys or financial transactions  
- Is designed for educational and demonstration purposes
- Implements proper security measures (HTTPS, CSP, security headers)
- Has a clear security policy at /security-policy

This appears to be a false positive, possibly due to:
1. Being hosted on Vercel's shared infrastructure
2. Recent deployment triggering automated scanning
3. Web3/blockchain content being misidentified

Please review and remove from the blocklist. Thank you.
    """)
    
    input("Press Enter after submitting the review...")
    
    # Step 3: Google Search Console
    print("\nStep 3: Google Search Console (if you have access)")
    print("-" * 40)
    console_url = "https://search.google.com/search-console"
    print(f"Opening: {console_url}")
    webbrowser.open(console_url)
    
    print("\nIf you have Search Console access:")
    print("1. Add your site if not already added")
    print("2. Check Security Issues section")
    print("3. Use 'Request Review' if available")
    
    input("Press Enter to continue...")
    
    # Step 4: Vercel Support
    print("\nStep 4: Contact Vercel Support")
    print("-" * 40)
    vercel_support_url = "https://vercel.com/help"
    print(f"Opening: {vercel_support_url}")
    webbrowser.open(vercel_support_url)
    
    print("\nSend Vercel support this message:")
    print("=" * 50)
    print("Subject: Google Safe Browsing False Positive on Vercel Domain")
    print("""
Hello Vercel Support,

My legitimate project at https://trust-mark.vercel.app is being flagged by 
Google Safe Browsing as dangerous, likely due to a false positive.

This is affecting the user experience of my educational blockchain analysis tool. 
The site contains no malicious content and implements proper security measures.

Could you please:
1. Check if there are any known IP reputation issues affecting vercel.app domains
2. Advise on best practices for avoiding such false positives  
3. Escalate to Google if this is a platform-wide issue

The project is open source and available for review.

Thank you for your assistance.
    """)
    
    print("\n✅ Review submission process complete!")
    print("\nNext steps:")
    print("- Monitor your site daily for changes")
    print("- Check Google Transparency Report for updates")
    print("- Response typically takes 1-7 days")
    print("- Keep implementing security best practices")

if __name__ == "__main__":
    main()