"""
Main Flask application for the Football Simulation API.

This serves as the backend for the React frontend, providing APIs for
team data, game simulation, season management, and more.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.exhibition_api import exhibition_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Enable CORS for the React frontend
    CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
    
    # Register blueprints
    app.register_blueprint(exhibition_bp, url_prefix='/api/exhibition')
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Football Simulation API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'exhibition': '/api/exhibition'
            }
        })
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Football Simulation API is running'
        })
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
