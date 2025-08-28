"""
Safe WSGI entry point using the safe main app
"""
try:
    from main_safe import app
except Exception as e:
    # Ultimate fallback - create the most basic Flask app possible
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def emergency():
        return jsonify({
            'status': 'emergency_mode',
            'error': str(e),
            'message': 'App is running in emergency mode'
        })

if __name__ == "__main__":
    app.run()