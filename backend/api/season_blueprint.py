"""
Flask blueprint for season simulation endpoints.

Provides REST endpoints for season management, game scheduling,
standings tracking, and season simulation.
"""
from flask import Blueprint, jsonify, request
from typing import Optional
import logging

from api.season_api import SeasonAPI
from api.simulation_api import SimulationAPI
from simulation.game_engine import GameEngine
from data.team_loader import load_sample_teams
from api.auth_api import get_user_id_from_jwt

# Create blueprint
season_bp = Blueprint('season', __name__)

# Initialize API instances
season_api = SeasonAPI()
simulation_api = SimulationAPI()
game_engine = GameEngine()

# Set up logging
logger = logging.getLogger(__name__)

@season_bp.route('/create', methods=['POST'])
def create_season():
    """Create a new season."""
    try:
        data = request.get_json() or {}
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        season_name = data.get('season_name')
        season_year = data.get('season_year', 2024)
        selected_teams = data.get('selected_teams')
        if not season_name:
            return jsonify({'success': False, 'error': 'season_name is required'}), 400

        result = season_api.create_season(
            user_id=user_id,
            season_name=season_name,
            season_year=season_year,
            selected_teams=selected_teams
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error creating season: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@season_bp.route('/status', methods=['GET'])
def get_season_status():
    """Get current season status."""
    try:
        user_id = get_user_id_from_jwt(request)
        season_id = request.args.get('season_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        if not season_id:
            return jsonify({'success': False, 'error': 'season_id is required'}), 400
        result = season_api.get_season_status(season_id=season_id, user_id=user_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting season status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Removed /teams endpoint: no such method in SeasonAPI

@season_bp.route('/next-games', methods=['GET'])
def get_next_games():
    """Get next games ready for simulation."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        season_id = request.args.get('season_id')
        if not season_id:
            return jsonify({'success': False, 'error': 'season_id is required'}), 400
        limit = request.args.get('limit', 16, type=int)
        result = season_api.get_next_games(season_id=season_id, user_id=user_id, limit=limit)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting next games: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@season_bp.route('/week/<int:week>', methods=['GET'])
def get_week_games(week: int):
    """Get all games for a specific week."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        season_id = request.args.get('season_id')
        if not season_id:
            return jsonify({'success': False, 'error': 'season_id is required'}), 400
        result = season_api.get_week_games(season_id=season_id, user_id=user_id, week=week)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting week {week} games: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@season_bp.route('/standings', methods=['GET'])
def get_standings():
    """Get current league standings."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        season_id = request.args.get('season_id')
        if not season_id:
            return jsonify({'success': False, 'error': 'season_id is required'}), 400
        by_division = request.args.get('by_division', 'true').lower() == 'true'
        result = season_api.get_standings(season_id=season_id, user_id=user_id, by_division=by_division)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting standings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@season_bp.route('/team/<team_id>/schedule', methods=['GET'])
def get_team_schedule(team_id: str):
    """Get complete schedule for a specific team."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        season_id = request.args.get('season_id')
        if not season_id:
            return jsonify({'success': False, 'error': 'season_id is required'}), 400
        result = season_api.get_team_schedule(season_id=season_id, user_id=user_id, team_id=team_id)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting team schedule: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ... (other endpoints should be similarly updated to extract user_id from JWT and pass to season_api)

@season_bp.route('/get_user_seasons', methods=['GET'])
def get_user_seasons():
    """
    Get all seasons for the current user.
    Returns a list of all seasons with relevant metadata for frontend selection.
    """
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        result = season_api.get_user_seasons(user_id=user_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting user seasons: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500