"""
Minimal WSGI entry point for Vercel deployment - Debug Version
"""
import os
import sys
import traceback
from flask import Flask, jsonify

# Create a minimal Flask app that always works
app = Flask(__name__)

@app.route('/')
def home():
    """Basic home route"""
    return jsonify({
        'status': 'success',
        'message': 'TrustMark API is running (minimal mode)',
        'version': '1.0.0-debug'
    })

@app.route('/debug')
def debug():
    """Debug information"""
    return jsonify({
        'python_version': sys.version,
        'environment_variables': {
            'DATABASE_URL': 'set' if os.environ.get('DATABASE_URL') else 'missing',
            'ETHERSCAN_API_KEY': 'set' if os.environ.get('ETHERSCAN_API_KEY') else 'missing',
            'SESSION_SECRET': 'set' if os.environ.get('SESSION_SECRET') else 'missing'
        },
        'working_directory': os.getcwd(),
        'python_path': sys.path[:3]  # First 3 entries
    })

@app.route('/test-imports')
def test_imports():
    """Test if we can import our modules"""
    results = {}
    
    # Test basic imports
    modules_to_test = [
        'flask',
        'flask_sqlalchemy', 
        'dotenv',
        'web3',
        'psycopg2',
        'requests'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            results[module] = 'success'
        except ImportError as e:
            results[module] = f'failed: {str(e)}'
    
    # Test our custom modules
    try:
        from utils.etherscan_api import get_transaction_history
        results['utils.etherscan_api'] = 'success'
    except Exception as e:
        results['utils.etherscan_api'] = f'failed: {str(e)}'
    
    try:
        from models import db, FlaggedTransaction
        results['models'] = 'success'
    except Exception as e:
        results['models'] = f'failed: {str(e)}'
    
    return jsonify({
        'import_results': results,
        'status': 'completed'
    })

@app.route('/test-main-app')
def test_main_app():
    """Try to create the main app"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Try to import and create main app
        from main import create_app
        main_app = create_app()
        
        return jsonify({
            'status': 'success',
            'message': 'Main app created successfully',
            'app_name': main_app.name
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to create main app: {str(e)}',
            'traceback': traceback.format_exc()
        })

if __name__ == "__main__":
    app.run(debug=True)