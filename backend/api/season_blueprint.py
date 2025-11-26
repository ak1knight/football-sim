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

# Game result submission endpoint
@season_bp.route('/submit-game-result', methods=['POST'])
def submit_game_result():
    """Submit the result of a completed game."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401

        data = request.get_json()
        season_id = data.get('season_id')
        game_id = data.get('game_id')
        home_score = data.get('home_score')
        away_score = data.get('away_score')
        overtime = data.get('overtime', False)
        game_stats = data.get('game_stats')

        if not all([season_id, game_id, home_score is not None, away_score is not None]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        result = season_api.submit_game_result(
            season_id=season_id,
            user_id=user_id,
            game_id=game_id,
            home_score=home_score,
            away_score=away_score,
            overtime=overtime,
            game_stats=game_stats
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error submitting game result: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Simulation endpoints
@season_bp.route('/simulate-game', methods=['POST'])
def simulate_game():
    """Simulate a single game."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401

        data = request.get_json()
        game_id = data.get('game_id')
        seed = data.get('seed')
        season_id = data.get('season_id')

        if not game_id:
            return jsonify({'success': False, 'error': 'game_id is required'}), 400

        result = season_api.simulate_game(
            season_id=season_id,
            game_id=game_id,
            seed=seed,
            user_id=user_id
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error simulating game: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@season_bp.route('/simulate-week', methods=['POST'])
def simulate_week():
    """Simulate all games for a week."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401

        data = request.get_json()
        week = data.get('week')
        seed = data.get('seed')
        season_id = data.get('season_id')

        if not season_id:
            return jsonify({'success': False, 'error': 'season_id is required'}), 400

        result = season_api.simulate_week(
            season_id=season_id,
            week=week,
            seed=seed,
            user_id=user_id
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error simulating week: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@season_bp.route('/simulate-to-week', methods=['POST'])
def simulate_to_week():
    """Simulate games up to a target week."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401

        data = request.get_json()
        target_week = data.get('target_week')
        seed = data.get('seed')
        season_id = data.get('season_id')

        if not all([season_id, target_week]):
            return jsonify({'success': False, 'error': 'season_id and target_week are required'}), 400

        result = season_api.simulate_to_week(
            season_id=season_id,
            target_week=target_week,
            seed=seed,
            user_id=user_id
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error simulating to week: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@season_bp.route('/simulate-season', methods=['POST'])
def simulate_season():
    """Simulate the entire season."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401

        data = request.get_json()
        season_id = data.get('season_id')
        seed = data.get('seed')

        if not season_id:
            return jsonify({'success': False, 'error': 'season_id is required'}), 400

        result = season_api.simulate_season(
            season_id=season_id,
            seed=seed,
            user_id=user_id
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error simulating season: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Second standings endpoint removed - duplicate

# Playoff endpoints
@season_bp.route('/playoffs/bracket', methods=['GET'])
def get_playoff_bracket():
    """Get current playoff bracket."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401

        season_id = request.args.get('season_id')
        if not season_id:
            return jsonify({'success': False, 'error': 'season_id is required'}), 400

        result = season_api.get_playoff_bracket(
            season_id=season_id,
            user_id=user_id
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting playoff bracket: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@season_bp.route('/playoffs/next-games', methods=['GET'])
def get_next_playoff_games():
    """Get next playoff games ready to be played."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401

        season_id = request.args.get('season_id')
        if not season_id:
            return jsonify({'success': False, 'error': 'season_id is required'}), 400

        result = season_api.get_next_playoff_games(
            season_id=season_id,
            user_id=user_id
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting next playoff games: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@season_bp.route('/playoffs/simulate-game', methods=['POST'])
def simulate_playoff_game():
    """Simulate a playoff game."""
    try:
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401

        data = request.get_json()
        game_id = data.get('game_id')
        seed = data.get('seed')
        season_id = data.get('season_id')

        if not game_id:
            return jsonify({'success': False, 'error': 'game_id is required'}), 400

        result = season_api.simulate_playoff_game(
            season_id=season_id,
            game_id=game_id,
            seed=seed,
            user_id=user_id
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error simulating playoff game: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

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