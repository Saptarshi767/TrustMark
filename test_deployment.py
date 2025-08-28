#!/usr/bin/env python3
"""
Test script to verify deployment readiness
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from web3 import Web3
        import psycopg2
        from utils.etherscan_api import get_transaction_history
        from utils.classifier import classify_address
        from models import db, FlaggedTransaction
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_app_creation():
    """Test that the app can be created"""
    try:
        from main import create_app
        app = create_app()
        print("✓ App creation successful")
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False

def test_environment():
    """Test environment variables"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['ETHERSCAN_API_KEY', 'DATABASE_URL', 'SESSION_SECRET']
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        print(f"✗ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print("✓ All environment variables present")
        return True

if __name__ == "__main__":
    print("Testing deployment readiness...")
    
    tests = [
        test_imports,
        test_environment,
        test_app_creation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    if all(results):
        print("\n🎉 All tests passed! Deployment should work.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Fix issues before deploying.")
        sys.exit(1)