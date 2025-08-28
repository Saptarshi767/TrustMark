#!/usr/bin/env python3
"""
Test dashboard with session
"""
from main import app

def test_dashboard():
    """Test dashboard with logged in session"""
    with app.test_client() as client:
        # Set session
        with client.session_transaction() as sess:
            sess['wallet_address'] = '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'
        
        # Test dashboard
        response = client.get('/dashboard')
        content = response.get_data(as_text=True)
        
        print(f"Dashboard Status: {response.status_code}")
        print(f"Has Bootstrap 5: {'bootstrap@5.3.0' in content}")
        print(f"Has dark theme: {'linear-gradient(135deg, #181c2b' in content}")
        print(f"Has glass cards: {'rgba(22, 27, 34, 0.5)' in content}")

if __name__ == "__main__":
    test_dashboard()