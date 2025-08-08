#!/usr/bin/env python3
"""
Test Neon database connection and API endpoints
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from models import FlaggedTransaction
from dotenv import load_dotenv

load_dotenv()

def test_neon_connection():
    """Test connection to Neon database"""
    
    print("🛡️ Testing TrustMark Neon Database Connection")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Count flagged transactions
            total_flags = FlaggedTransaction.query.count()
            print(f"📊 Total flagged transactions: {total_flags}")
            
            # Get unique addresses
            flagged_addresses = FlaggedTransaction.query.with_entities(FlaggedTransaction.wallet_address).distinct().all()
            unique_addresses = len(flagged_addresses)
            print(f"📊 Unique flagged addresses: {unique_addresses}")
            
            # Count by reason
            hacker_count = FlaggedTransaction.query.filter_by(reason='hacker').count()
            suspicious_count = FlaggedTransaction.query.filter_by(reason='suspicious').count()
            
            print(f"🔴 Hacker addresses: {hacker_count}")
            print(f"🟡 Suspicious addresses: {suspicious_count}")
            
            # Show sample addresses
            print("\n📋 Sample flagged addresses:")
            sample_flags = FlaggedTransaction.query.limit(3).all()
            for flag in sample_flags:
                print(f"   • {flag.wallet_address[:10]}... ({flag.reason})")
            
            print("\n✅ Neon database connection successful!")
            return True
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            return False

if __name__ == "__main__":
    test_neon_connection()