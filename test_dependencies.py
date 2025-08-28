#!/usr/bin/env python3
"""
Test script to verify all dependencies can be imported
"""
import sys

def test_dependencies():
    """Test that all required dependencies can be imported"""
    dependencies = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('dotenv', 'python-dotenv'),
        ('web3', 'web3'),
        ('requests', 'requests'),
        ('gunicorn', 'gunicorn')
    ]
    
    failed = []
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")
            failed.append(name)
    
    # Test psycopg2 separately as it might not be needed locally
    try:
        import psycopg2
        print("✓ psycopg2-binary")
    except ImportError:
        print("⚠ psycopg2-binary (not available locally, but should work on Vercel)")
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        return False
    else:
        print("\n🎉 All core dependencies available!")
        return True

if __name__ == "__main__":
    success = test_dependencies()
    sys.exit(0 if success else 1)