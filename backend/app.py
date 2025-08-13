"""
Main Flask application for the Football Simulation API.

This serves as the backend for the React frontend, providing APIs for
team data, game simulation, season management, and more.
"""
import logging
from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.exhibition_api import exhibition_bp
from api.teams_blueprint import teams_bp
from api.season_blueprint import season_bp
from api.auth_api import auth_bp
from database.connection import initialize_database_manager

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Initialize the database manager
    initialize_database_manager()
    
    # Enable CORS for the React frontend
    CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
    
    # Register blueprints
    app.register_blueprint(exhibition_bp, url_prefix='/api/exhibition')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(season_bp, url_prefix='/api/season')
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Football Simulation API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'exhibition': '/api/exhibition',
                'teams': '/api/teams',
                'season': '/api/season',
                'auth': '/api/auth'
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
    app.logger.setLevel(logging.DEBUG)
    app.logger.info("Starting Football Simulation API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
