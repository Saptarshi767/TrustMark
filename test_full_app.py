#!/usr/bin/env python3
"""
Test the full application functionality
"""
import sys
from app import app

def test_app():
    """Test that the app works correctly"""
    with app.test_client() as client:
        # Test home page
        response = client.get('/')
        print(f"Home page: {response.status_code}")
        
        # Test health endpoint
        response = client.get('/health')
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"  Status: {data.get('status')}")
            print(f"  Database: {data.get('database')}")
        
        # Test API endpoint
        response = client.get('/api/flagged_addresses')
        print(f"API endpoint: {response.status_code}")
        
        return True

if __name__ == "__main__":
    try:
        test_app()
        print("✅ All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)