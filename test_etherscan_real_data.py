#!/usr/bin/env python3
"""
Test script to verify Etherscan API is returning real blockchain data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.etherscan_api import get_transaction_history, get_ether_balance, get_transaction_details
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_real_ethereum_address():
    """Test with Vitalik Buterin's well-known address"""
    vitalik_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    print("🔍 Testing Etherscan API with real Ethereum data...")
    print(f"📍 Testing address: {vitalik_address} (Vitalik Buterin)")
    print("-" * 60)
    
    # Test balance
    print("💰 Testing balance retrieval...")
    balance = get_ether_balance(vitalik_address)
    print(f"   Balance: {balance} ETH")
    
    if balance > 0:
        print("   ✅ Balance API working - returned real data!")
    else:
        print("   ⚠️  Balance is 0 or API error")
    
    print()
    
    # Test transaction history
    print("📜 Testing transaction history...")
    transactions = get_transaction_history(vitalik_address, limit=5)
    
    if transactions:
        print(f"   Found {len(transactions)} transactions")
        print("   ✅ Transaction API working - returned real data!")
        
        print("\n   Recent transactions:")
        for i, tx in enumerate(transactions[:3], 1):
            print(f"   {i}. Hash: {tx['tx_hash'][:10]}...")
            print(f"      Amount: {tx['amount']} ETH")
            print(f"      Direction: {tx['direction']}")
            print(f"      Timestamp: {tx['timestamp']}")
            print(f"      From: {tx['from'][:10]}...")
            print(f"      To: {tx['to'][:10]}...")
            print()
    else:
        print("   ❌ No transactions found or API error")
    
    # Test transaction details
    if transactions:
        print("🔍 Testing transaction details...")
        first_tx_hash = transactions[0]['tx_hash']
        tx_details = get_transaction_details(first_tx_hash)
        
        if tx_details:
            print(f"   Transaction details for {first_tx_hash[:10]}...")
            print(f"   Amount: {tx_details['amount']} ETH")
            print(f"   Gas: {tx_details['gas']}")
            print(f"   Contract call: {tx_details['is_contract_call']}")
            print("   ✅ Transaction details API working!")
        else:
            print("   ❌ Could not fetch transaction details")

def test_random_address():
    """Test with a random address to see behavior with no transactions"""
    random_address = "0x1234567890123456789012345678901234567890"
    
    print("\n" + "=" * 60)
    print("🎲 Testing with random address (should have no transactions)...")
    print(f"📍 Testing address: {random_address}")
    print("-" * 60)
    
    balance = get_ether_balance(random_address)
    transactions = get_transaction_history(random_address, limit=5)
    
    print(f"💰 Balance: {balance} ETH")
    print(f"📜 Transactions found: {len(transactions)}")
    
    if balance == 0 and len(transactions) == 0:
        print("   ✅ Correctly returns empty data for unused address")
    else:
        print("   ⚠️  Unexpected data for random address")

def test_api_key():
    """Test if API key is working"""
    print("\n" + "=" * 60)
    print("🔑 Testing API Key Configuration...")
    print("-" * 60)
    
    api_key = os.environ.get("ETHERSCAN_API_KEY")
    if api_key:
        print(f"   API Key found: {api_key[:10]}...{api_key[-5:]}")
        print("   ✅ API key is configured")
    else:
        print("   ❌ No API key found in environment")

if __name__ == "__main__":
    print("🚀 TrustMark Etherscan API Real Data Test")
    print("=" * 60)
    
    test_api_key()
    test_real_ethereum_address()
    test_random_address()
    
    print("\n" + "=" * 60)
    print("✅ Test completed! Check results above.")