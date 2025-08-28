"""
WSGI entry point for Vercel deployment
"""
import os
import sys
import traceback

def create_application():
    """Create Flask application with error handling"""
    try:
        from main import create_app
        app = create_app()
        
        # Add a simple health check that doesn't require database
        @app.route('/status')
        def status():
            return {'status': 'ok', 'message': 'App is running'}
        
        return app
    except Exception as e:
        print(f"Error creating app: {e}")
        traceback.print_exc()
        # Return a minimal Flask app for debugging
        from flask import Flask, jsonify
        debug_app = Flask(__name__)
        
        @debug_app.route('/')
        def debug_home():
            return jsonify({
                'error': 'App initialization failed',
                'message': str(e),
                'env_vars': {
                    'DATABASE_URL': 'set' if os.environ.get('DATABASE_URL') else 'missing',
                    'ETHERSCAN_API_KEY': 'set' if os.environ.get('ETHERSCAN_API_KEY') else 'missing',
                    'SESSION_SECRET': 'set' if os.environ.get('SESSION_SECRET') else 'missing'
                }
            })
        
        return debug_app

# Create the app
app = create_application()

if __name__ == "__main__":
    app.run(debug=True)