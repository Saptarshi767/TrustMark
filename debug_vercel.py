#!/usr/bin/env python3
"""
Debug script to identify Vercel deployment issues
"""
import os
import sys
import traceback

def check_environment():
    """Check environment variables"""
    print("=== Environment Variables ===")
    required_vars = ['DATABASE_URL', 'ETHERSCAN_API_KEY', 'SESSION_SECRET']
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var}: {'*' * min(len(value), 20)}...")
        else:
            print(f"✗ {var}: NOT SET")

def check_imports():
    """Check if all imports work"""
    print("\n=== Import Tests ===")
    
    imports_to_test = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'SQLAlchemy'),
        ('dotenv', 'python-dotenv'),
        ('web3', 'Web3'),
        ('psycopg2', 'psycopg2-binary'),
        ('requests', 'requests')
    ]
    
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")

def check_app_creation():
    """Test app creation"""
    print("\n=== App Creation Test ===")
    
    try:
        # Load environment first
        from dotenv import load_dotenv
        load_dotenv()
        
        # Try to create the app
        from main import create_app
        app = create_app()
        print("✓ App created successfully")
        
        # Test app context
        with app.app_context():
            print("✓ App context works")
            
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        traceback.print_exc()
        return False

def check_database():
    """Test database connection"""
    print("\n=== Database Test ===")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL not set")
        return False
    
    try:
        import psycopg2
        # Try to connect to the database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def main():
    print("🔍 TrustMark Vercel Debug Report")
    print("=" * 50)
    
    check_environment()
    check_imports()
    app_ok = check_app_creation()
    db_ok = check_database()
    
    print("\n" + "=" * 50)
    if app_ok and db_ok:
        print("🎉 All checks passed! App should work on Vercel.")
    else:
        print("❌ Some issues found. Check the errors above.")
        
    print("\n💡 Debugging tips:")
    print("- Check Vercel function logs for detailed error messages")
    print("- Verify environment variables are set in Vercel dashboard")
    print("- Test the /health endpoint first")

if __name__ == "__main__":
    main()