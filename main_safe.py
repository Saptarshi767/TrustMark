"""
Safe version of main.py with extensive error handling
"""
import os
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application with maximum safety"""
    app = Flask(__name__)
    
    # Basic configuration that should always work
    app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key")
    
    @app.route('/')
    def home():
        return jsonify({
            'message': 'TrustMark API (Safe Mode)',
            'status': 'running'
        })
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'mode': 'safe',
            'environment': {
                'DATABASE_URL': 'set' if os.environ.get('DATABASE_URL') else 'missing',
                'ETHERSCAN_API_KEY': 'set' if os.environ.get('ETHERSCAN_API_KEY') else 'missing',
                'SESSION_SECRET': 'set' if os.environ.get('SESSION_SECRET') else 'missing'
            }
        })
    
    # Try to add database functionality if possible
    try:
        from flask_sqlalchemy import SQLAlchemy
        
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
            app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
            
            db = SQLAlchemy()
            db.init_app(app)
            
            @app.route('/db-test')
            def db_test():
                try:
                    with app.app_context():
                        result = db.session.execute(db.text('SELECT 1'))
                        result.fetchone()
                    return jsonify({'database': 'connected'})
                except Exception as e:
                    return jsonify({'database': f'error: {str(e)}'})
        
        logger.info("Database configuration added successfully")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)