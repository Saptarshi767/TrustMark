"""
WSGI entry point for Vercel deployment
"""
import os
from main import create_app

app = create_app()

# Initialize database tables for production
if os.environ.get('DATABASE_URL'):
    from main import init_db
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization warning: {e}")

if __name__ == "__main__":
    app.run()