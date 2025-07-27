#!/usr/bin/env python3
"""
Setup script to add test flagged addresses for Chrome extension testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import FlaggedTransaction
from dotenv import load_dotenv

load_dotenv()

def setup_test_flags():
    """Add test flagged addresses to database for extension testing"""
    
    print("🛡️ Setting up test flagged addresses for Chrome extension")
    print("=" * 60)
    
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        
        # Test addresses to flag
        test_flags = [
            {
                "wallet": "0xDa9dfA130Df4dE4673b89022EE50ff26f6EA73Cf",
                "reason": "hacker",
                "note": "Known malicious address"
            },
            {
                "wallet": "0x742d35Cc6634C0532925a3b8D4C9db96590c6C8C", 
                "reason": "hacker",
                "note": "Flagged for suspicious activity"
            },
            {
                "wallet": "0x4f655e4D5A245A6d7543867389A531A381015696",
                "reason": "suspicious", 
                "note": "Questionable transaction patterns"
            },
            {
                "wallet": "0xb247d4b1548810214a3a6931448956922533e4B3",
                "reason": "suspicious",
                "note": "Under investigation"
            }
        ]
        
        print("📝 Adding test flagged addresses...")
        
        # Clear existing test flags
        for flag_data in test_flags:
            existing = FlaggedTransaction.query.filter_by(wallet_address=flag_data["wallet"]).all()
            for tx in existing:
                db.session.delete(tx)
        db.session.commit()
        
        # Add new test flags
        for i, flag_data in enumerate(test_flags):
            flagged_tx = FlaggedTransaction(
                tx_hash=f"0x{i+1000:064x}",  # Generate unique test hash
                wallet_address=flag_data["wallet"],
                reason=flag_data["reason"],
                amount=float(i + 1) * 0.5,
                direction="out",
                note=flag_data["note"]
            )
            db.session.add(flagged_tx)
            print(f"   ✅ Added {flag_data['reason']} flag for {flag_data['wallet']}")
        
        db.session.commit()
        print(f"\n📊 Successfully added {len(test_flags)} test flags to database")
        
        # Verify the flags were added
        print("\n🔍 Verifying flagged addresses in database...")
        flagged_addresses = db.session.query(FlaggedTransaction.wallet_address).distinct().all()
        addresses = [addr[0] for addr in flagged_addresses]
        
        print(f"   📊 Total flagged addresses in database: {len(addresses)}")
        
        for flag_data in test_flags:
            if flag_data["wallet"] in addresses:
                flags = FlaggedTransaction.query.filter_by(wallet_address=flag_data["wallet"]).all()
                print(f"   ✅ {flag_data['wallet']}: {len(flags)} flag(s) ({flag_data['reason']})")
            else:
                print(f"   ❌ {flag_data['wallet']}: Not found!")
        
        # Test API response format
        print("\n🌐 Testing Chrome extension API response...")
        suspicious_addresses = db.session.query(FlaggedTransaction.wallet_address).all()
        
        api_response = {
            'flagged_addresses': addresses,
            'suspicious_addresses': [addr[0] for addr in suspicious_addresses],
            'total_flagged': len(addresses),
            'total_suspicious': len(suspicious_addresses)
        }
        
        print(f"   📊 API will return:")
        print(f"      • Flagged addresses: {api_response['total_flagged']}")
        print(f"      • Suspicious addresses: {api_response['total_suspicious']}")
        
        return True

def show_test_instructions():
    """Show instructions for testing the Chrome extension"""
    
    print("\n" + "=" * 60)
    print("🧪 CHROME EXTENSION TESTING INSTRUCTIONS")
    print("=" * 60)
    print("1. 🚀 Start the Flask server:")
    print("   python main.py")
    print()
    print("2. 🌐 Open the test page:")
    print("   Open test_extension_purple.html in your browser")
    print()
    print("3. 🔌 Install the Chrome extension:")
    print("   - Go to chrome://extensions/")
    print("   - Enable Developer mode")
    print("   - Click 'Load unpacked'")
    print("   - Select the chrome_extension folder")
    print()
    print("4. 🧪 Test the extension:")
    print("   - Click the TrustMark extension icon")
    print("   - Click 'Scan Current Page'")
    print("   - Verify purple theme and colored badges")
    print()
    print("5. ✅ Expected results:")
    print("   - Purple extension popup background")
    print("   - Red badges on flagged addresses")
    print("   - Yellow badges on suspicious addresses") 
    print("   - Purple badges on normal addresses")

if __name__ == "__main__":
    success = setup_test_flags()
    
    if success:
        show_test_instructions()
        print("\n🎯 READY FOR TESTING!")
        print("✅ Database has been populated with test flagged addresses")
        print("✅ Chrome extension should now detect and highlight addresses")
        print("✅ Purple theme is applied to extension UI")
    else:
        print("\n❌ Setup failed!")