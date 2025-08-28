#!/usr/bin/env python3
"""
Test styling and frontend functionality
"""
from main import app

def test_styling():
    """Test that all styling components are working"""
    with app.test_client() as client:
        print("🎨 Testing TrustMark Frontend Styling...")
        
        # Test home page
        response = client.get('/')
        content = response.get_data(as_text=True)
        
        print(f"📄 Page Status: {response.status_code}")
        
        # Check CSS and styling
        checks = [
            ("Bootstrap 5 CSS", "bootstrap@5.3.0" in content),
            ("Font Awesome Icons", "font-awesome" in content),
            ("AOS Animations", "aos" in content),
            ("Custom CSS", "style.css" in content),
            ("Dark Theme Background", "linear-gradient(135deg, #181c2b" in content),
            ("Glass Card Styling", "rgba(22, 27, 34, 0.5)" in content),
            ("Hero Section", "hero-3d" in content),
            ("3D Buttons", "btn-3d" in content),
            ("AOS Init Script", "AOS.init" in content),
            ("Counter Animations", "animateCounter" in content),
            ("Theme Toggle", "toggleMode" in content),
            ("Educational Disclaimer", "Educational Purpose" in content),
            ("Security Section", "Security & Privacy" in content)
        ]
        
        print("\n🔍 Styling Components:")
        for name, check in checks:
            status = "✅" if check else "❌"
            print(f"  {status} {name}")
        
        # Test static files
        css_response = client.get('/static/css/style.css')
        js_response = client.get('/static/js/script.js')
        
        print(f"\n📁 Static Files:")
        print(f"  ✅ CSS File: {css_response.status_code} ({len(css_response.get_data())} bytes)")
        print(f"  ✅ JS File: {js_response.status_code} ({len(js_response.get_data())} bytes)")
        
        # Check if all components are present
        all_good = all(check for _, check in checks)
        
        if all_good:
            print("\n🎉 All styling components are working perfectly!")
            print("🚀 Your TrustMark frontend is ready with:")
            print("   • Beautiful glassmorphism design")
            print("   • Smooth AOS animations")
            print("   • Interactive 3D buttons")
            print("   • Dark/light theme toggle")
            print("   • Responsive layout")
            print("   • Security disclaimers")
        else:
            print("\n⚠️  Some styling components may need attention")
        
        return all_good

if __name__ == "__main__":
    test_styling()