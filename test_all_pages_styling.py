#!/usr/bin/env python3
"""
Test styling for all pages
"""
from main import app

def test_all_pages():
    """Test that all pages have proper styling"""
    with app.test_client() as client:
        print("🎨 Testing All Pages Styling...")
        
        pages = [
            ('/', 'Home Page'),
            ('/login', 'Login Page'),
            ('/dashboard', 'Dashboard'),
            ('/search', 'Search Page'),
            ('/extension-guide', 'Extension Guide'),
            ('/flagged-stats', 'Flagged Stats')
        ]
        
        for url, name in pages:
            try:
                response = client.get(url)
                content = response.get_data(as_text=True)
                
                # Check styling components
                has_bootstrap5 = "bootstrap@5.3.0" in content
                has_custom_css = "style.css" in content
                has_dark_theme = "linear-gradient(135deg, #181c2b" in content
                has_glass_cards = "rgba(22, 27, 34, 0.5)" in content
                
                status = "✅" if response.status_code == 200 else "❌"
                bootstrap_status = "✅" if has_bootstrap5 else "❌"
                css_status = "✅" if has_custom_css else "❌"
                theme_status = "✅" if has_dark_theme else "❌"
                glass_status = "✅" if has_glass_cards else "❌"
                
                print(f"\n📄 {name} ({url})")
                print(f"  {status} Page Load: {response.status_code}")
                print(f"  {bootstrap_status} Bootstrap 5")
                print(f"  {css_status} Custom CSS")
                print(f"  {theme_status} Dark Theme")
                print(f"  {glass_status} Glass Cards")
                
            except Exception as e:
                print(f"\n❌ {name} ({url}): Error - {e}")
        
        print("\n🎉 All pages styling test completed!")

if __name__ == "__main__":
    test_all_pages()