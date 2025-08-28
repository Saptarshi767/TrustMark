"""
WSGI entry point for Vercel deployment
"""
import os
import sys
import traceback

def create_application():
    """Create Flask application with robust error handling"""
    try:
        # Load environment variables first
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import and create the main app
        from main import create_app
        app = create_app()
        
        return app
        
    except Exception as e:
        print(f"Error creating main app: {e}")
        traceback.print_exc()
        
        # Create a fallback Flask app with error info
        from flask import Flask, jsonify, render_template_string
        
        fallback_app = Flask(__name__)
        fallback_app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret")
        
        @fallback_app.route('/')
        def fallback_home():
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>TrustMark - Initializing</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .error { background: #fee; border: 1px solid #fcc; padding: 15px; border-radius: 4px; margin: 20px 0; }
                    .success { background: #efe; border: 1px solid #cfc; padding: 15px; border-radius: 4px; margin: 20px 0; }
                    pre { background: #f8f8f8; padding: 10px; border-radius: 4px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔧 TrustMark - System Status</h1>
                    <div class="error">
                        <h3>Application Initialization Error</h3>
                        <p><strong>Error:</strong> {{ error_message }}</p>
                        <p>The application is running in fallback mode while we resolve this issue.</p>
                    </div>
                    
                    <h3>Environment Status</h3>
                    <ul>
                        <li>DATABASE_URL: {{ 'Set' if env_vars.DATABASE_URL else 'Missing' }}</li>
                        <li>ETHERSCAN_API_KEY: {{ 'Set' if env_vars.ETHERSCAN_API_KEY else 'Missing' }}</li>
                        <li>SESSION_SECRET: {{ 'Set' if env_vars.SESSION_SECRET else 'Missing' }}</li>
                    </ul>
                    
                    <h3>Available Endpoints</h3>
                    <ul>
                        <li><a href="/health">/health</a> - System health check</li>
                        <li><a href="/debug">/debug</a> - Detailed debug information</li>
                    </ul>
                </div>
            </body>
            </html>
            ''', 
            error_message=str(e),
            env_vars={
                'DATABASE_URL': bool(os.environ.get('DATABASE_URL')),
                'ETHERSCAN_API_KEY': bool(os.environ.get('ETHERSCAN_API_KEY')),
                'SESSION_SECRET': bool(os.environ.get('SESSION_SECRET'))
            })
        
        @fallback_app.route('/health')
        def fallback_health():
            return jsonify({
                'status': 'fallback_mode',
                'error': str(e),
                'environment': {
                    'DATABASE_URL': 'set' if os.environ.get('DATABASE_URL') else 'missing',
                    'ETHERSCAN_API_KEY': 'set' if os.environ.get('ETHERSCAN_API_KEY') else 'missing',
                    'SESSION_SECRET': 'set' if os.environ.get('SESSION_SECRET') else 'missing'
                }
            })
        
        @fallback_app.route('/debug')
        def fallback_debug():
            return jsonify({
                'status': 'error',
                'main_app_error': str(e),
                'traceback': traceback.format_exc(),
                'python_version': sys.version,
                'environment_variables': {
                    'DATABASE_URL': 'set' if os.environ.get('DATABASE_URL') else 'missing',
                    'ETHERSCAN_API_KEY': 'set' if os.environ.get('ETHERSCAN_API_KEY') else 'missing',
                    'SESSION_SECRET': 'set' if os.environ.get('SESSION_SECRET') else 'missing'
                }
            })
        
        return fallback_app

# Create the application
app = create_application()

if __name__ == "__main__":
    app.run(debug=True)