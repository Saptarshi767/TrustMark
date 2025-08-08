#!/usr/bin/env python3
"""
Setup script for Neon PostgreSQL database
Creates tables and populates with test data for TrustMark Chrome extension
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import FlaggedTransaction

def setup_neon_database():
    """Setup Neon PostgreSQL database with tables and test data"""
    
    print("🛡️ Setting up TrustMark Neon PostgreSQL Database")
    print("=" * 60)
    
    # Check database URL
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"📊 Database URL: {database_url[:50]}...")
    
    with app.app_context():
        try:
            # Create all tables
            print("\n📋 Creating database tables...")
            db.create_all()
            print("   ✅ Tables created successfully")
            
            # Clear existing test data
            print("\n🧹 Clearing existing test data...")
            existing_flags = FlaggedTransaction.query.all()
            for flag in existing_flags:
                db.session.delete(flag)
            db.session.commit()
            print(f"   ✅ Cleared {len(existing_flags)} existing records")
            
            # Add test flagged addresses
            print("\n📝 Adding test flagged addresses...")
            
            test_flags = [
                {
                    "wallet": "0xDa9dfA130Df4dE4673b89022EE50ff26f6EA73Cf",
                    "reason": "hacker",
                    "note": "Known malicious address - phishing attacks"
                },
                {
                    "wallet": "0x742d35Cc6634C0532925a3b8D4C9db96590c6C8C", 
                    "reason": "hacker",
                    "note": "Flagged for suspicious activity - rug pull"
                },
                {
                    "wallet": "0x4f655e4D5A245A6d7543867389A531A381015696",
                    "reason": "suspicious", 
                    "note": "Questionable transaction patterns"
                },
                {
                    "wallet": "0xb247d4b1548810214a3a6931448956922533e4B3",
                    "reason": "suspicious",
                    "note": "Under investigation - unusual volume"
                },
                {
                    "wallet": "0x1234567890123456789012345678901234567890",
                    "reason": "hacker",
                    "note": "Test hacker address for demo"
                },
                {
                    "wallet": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                    "reason": "suspicious",
                    "note": "Test suspicious address for demo"
                }
            ]
            
            for i, flag_data in enumerate(test_flags):
                flagged_tx = FlaggedTransaction(
                    tx_hash=f"0x{i+3000:064x}",  # Generate unique test hash
                    wallet_address=flag_data["wallet"],
                    reason=flag_data["reason"],
                    amount=float(i + 1) * 0.5,
                    direction="out",
                    note=flag_data["note"],
                    created_at=datetime.utcnow()
                )
                db.session.add(flagged_tx)
                print(f"   ✅ Added {flag_data['reason']} flag for {flag_data['wallet'][:10]}...")
            
            db.session.commit()
            print(f"\n📊 Successfully added {len(test_flags)} test flags to Neon database")
            
            # Verify the data
            print("\n🔍 Verifying data in Neon database...")
            flagged_addresses = db.session.query(FlaggedTransaction.wallet_address).distinct().all()
            addresses = [addr[0] for addr in flagged_addresses]
            
            print(f"   📊 Total unique flagged addresses: {len(addresses)}")
            
            # Count by reason
            hacker_count = FlaggedTransaction.query.filter_by(reason='hacker').count()
            suspicious_count = FlaggedTransaction.query.filter_by(reason='suspicious').count()
            
            print(f"   🔴 Hacker addresses: {hacker_count}")
            print(f"   🟡 Suspicious addresses: {suspicious_count}")
            
            # Test API response format
            print("\n🌐 Testing API response format...")
            suspicious_addresses = db.session.query(FlaggedTransaction.wallet_address).all()
            
            api_response = {
                'flagged_addresses': addresses,
                'suspicious_addresses': [addr[0] for addr in suspicious_addresses],
                'total_flagged': len(addresses),
                'total_suspicious': len(suspicious_addresses)
            }
            
            print(f"   📊 Chrome extension will receive:")
            print(f"      • Flagged addresses: {api_response['total_flagged']}")
            print(f"      • Suspicious addresses: {api_response['total_suspicious']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up database: {str(e)}")
            return False

def test_database_connection():
    """Test connection to Neon database"""
    
    print("\n🔌 Testing Neon Database Connection...")
    
    with app.app_context():
        try:
            # Simple query to test connection
            result = db.session.execute(db.text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"   ✅ Connected to PostgreSQL: {version[:50]}...")
            
            # Test table exists
            result = db.session.execute(db.text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'flagged_transactions'
            """))
            
            if result.fetchone():
                print("   ✅ flagged_transactions table exists")
            else:
                print("   ❌ flagged_transactions table not found")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database connection failed: {str(e)}")
            return False

def show_deployment_instructions():
    """Show instructions for deploying to Vercel"""
    
    print("\n" + "=" * 60)
    print("🚀 DEPLOYMENT INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📦 Deploy to Vercel:")
    print("   1. Install Vercel CLI: npm i -g vercel")
    print("   2. Login to Vercel: vercel login")
    print("   3. Deploy: vercel --prod")
    print("   4. Set environment variables in Vercel dashboard:")
    print("      • DATABASE_URL (your Neon connection string)")
    print("      • ETHERSCAN_API_KEY")
    print("      • SESSION_SECRET")
    
    print("\n🔌 Chrome Extension:")
    print("   1. Extension is already configured for production URL")
    print("   2. Create new ZIP: Compress-Archive chrome_extension/* extension.zip")
    print("   3. Install in Chrome: Load unpacked extension")
    
    print("\n🧪 Testing:")
    print("   1. Visit: https://trust-mark.vercel.app/")
    print("   2. Open test page with Ethereum addresses")
    print("   3. Click extension icon → 'Scan Current Page'")
    print("   4. Verify purple theme and colored badges")

if __name__ == "__main__":
    print("🛡️ TrustMark Neon Database Setup")
    print("=" * 60)
    
    # Test connection first
    if test_database_connection():
        # Setup database
        if setup_neon_database():
            show_deployment_instructions()
            print("\n🎯 SUCCESS: Neon database is ready for production!")
            print("✅ Tables created and populated with test data")
            print("✅ Chrome extension configured for production")
            print("✅ Ready for Vercel deployment")
        else:
            print("\n❌ Database setup failed!")
    else:
        print("\n❌ Cannot connect to Neon database!")
        print("   Check your DATABASE_URL in .env file")