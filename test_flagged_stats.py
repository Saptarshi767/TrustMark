#!/usr/bin/env python3
"""
Test flagged stats page
"""
from main import app

def test_flagged_stats():
    """Test flagged stats with logged in session"""
    with app.test_client() as client:
        # Set session
        with client.session_transaction() as sess:
            sess['wallet_address'] = '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'
        
        # Test flagged stats
        response = client.get('/flagged_stats')
        content = response.get_data(as_text=True)
        
        print(f"Flagged Stats Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Has Bootstrap 5: {'bootstrap@5.3.0' in content}")
            print(f"Has dark theme: {'linear-gradient(135deg, #181c2b' in content}")
            print(f"Has glass cards: {'rgba(22, 27, 34, 0.5)' in content}")

if __name__ == "__main__":
    test_flagged_stats()