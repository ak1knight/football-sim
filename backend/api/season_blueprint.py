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
        season_year = data.get('season_year', 2024)
        seed = data.get('seed')
        
        result = season_api.create_season(season_year=season_year, seed=seed)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error creating season: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/status', methods=['GET'])
def get_season_status():
    """Get current season status."""
    try:
        result = season_api.get_season_status()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting season status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/teams', methods=['GET'])
def get_all_teams():
    """Get all available teams."""
    try:
        result = season_api.get_all_teams()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting teams: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/next-games', methods=['GET'])
def get_next_games():
    """Get next games ready for simulation."""
    try:
        limit = request.args.get('limit', 16, type=int)
        result = season_api.get_next_games(limit=limit)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting next games: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/week/<int:week>', methods=['GET'])
def get_week_games(week: int):
    """Get all games for a specific week."""
    try:
        result = season_api.get_week_games(week)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting week {week} games: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/standings', methods=['GET'])
def get_standings():
    """Get current league standings."""
    try:
        by_division = request.args.get('by_division', 'true').lower() == 'true'
        result = season_api.get_standings(by_division=by_division)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting standings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/team/<team_abbreviation>/schedule', methods=['GET'])
def get_team_schedule(team_abbreviation: str):
    """Get complete schedule for a specific team."""
    try:
        result = season_api.get_team_schedule(team_abbreviation.upper())
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting team schedule: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/playoffs', methods=['GET'])
def get_playoff_picture():
    """Get current playoff picture."""
    try:
        result = season_api.get_playoff_picture()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting playoff picture: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/playoffs/bracket', methods=['GET'])
def get_playoff_bracket():
    """Get the complete playoff bracket."""
    try:
        result = season_api.get_playoff_bracket()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting playoff bracket: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/playoffs/next-games', methods=['GET'])
def get_next_playoff_games():
    """Get next playoff games ready for simulation."""
    try:
        result = season_api.get_next_playoff_games()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting next playoff games: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/playoffs/simulate-game', methods=['POST'])
def simulate_playoff_game():
    """Simulate a playoff game and advance the bracket."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        game_id = data.get('game_id')
        seed = data.get('seed')
        
        if not game_id:
            return jsonify({'success': False, 'error': 'game_id is required'}), 400
        
        # Get the playoff game details
        if not season_api.current_season or not season_api.current_season.playoff_engine:
            return jsonify({'success': False, 'error': 'No active playoffs'}), 400
        
        # Find the playoff game
        playoff_games = season_api.current_season.get_next_playoff_games()
        game_data = None
        for pg in playoff_games:
            if pg.get('game_id') == game_id:
                game_data = pg
                break
        
        if not game_data or not game_data.get('is_ready_to_play'):
            return jsonify({'success': False, 'error': f'Playoff game {game_id} not found or not ready'}), 404
        
        # Get teams for simulation
        home_team = None
        away_team = None
        
        for team in season_api.teams:
            if team.abbreviation == game_data['home_team']['abbreviation']:
                home_team = team
            elif team.abbreviation == game_data['away_team']['abbreviation']:
                away_team = team
        
        if not home_team or not away_team:
            return jsonify({'success': False, 'error': 'Could not find teams for simulation'}), 400
        
        # Simulate the game
        engine = GameEngine(seed=seed) if seed else GameEngine()
        game_result = engine.simulate_game(home_team, away_team)
        
        # Submit the result
        result = season_api.simulate_playoff_game(
            game_id=game_id,
            home_score=game_result.home_score,
            away_score=game_result.away_score,
            overtime=game_result.duration > 60
        )
        
        if result['success']:
            # Add simulation details to response
            result['simulation_details'] = {
                'home_team': {
                    'name': game_result.home_team.full_name,
                    'abbreviation': game_result.home_team.abbreviation,
                    'score': game_result.home_score
                },
                'away_team': {
                    'name': game_result.away_team.full_name,
                    'abbreviation': game_result.away_team.abbreviation,
                    'score': game_result.away_score
                },
                'winner': game_result.winner.abbreviation if game_result.winner else None,
                'duration_minutes': game_result.duration,
                'weather': {
                    'conditions': str(game_result.weather) if game_result.weather else None,
                    'severity': game_result.weather.get_severity_rating() if game_result.weather else None
                }
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error simulating playoff game: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/simulate-game', methods=['POST'])
def simulate_single_game():
    """Simulate a single game and update season records."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        game_id = data.get('game_id')
        seed = data.get('seed')
        
        if not game_id:
            return jsonify({'success': False, 'error': 'game_id is required'}), 400
        
        # Get the game details from season API
        if not season_api.current_season:
            return jsonify({'success': False, 'error': 'No active season'}), 400
        
        # Find the game in the current season
        game = None
        for scheduled_game in season_api.current_season.schedule:
            if scheduled_game.game_id == game_id:
                game = scheduled_game
                break
        
        if not game:
            return jsonify({'success': False, 'error': f'Game {game_id} not found'}), 404
            
        if game.is_completed:
            return jsonify({'success': False, 'error': f'Game {game_id} is already completed'}), 400
        
        # Simulate the game
        engine = GameEngine(seed=seed) if seed else GameEngine()
        game_result = engine.simulate_game(game.home_team, game.away_team)
        
        # Submit the result to the season
        result = season_api.submit_game_result(
            game_id=game_id,
            home_score=game_result.home_score,
            away_score=game_result.away_score,
            overtime=game_result.duration > 60,
            game_duration=game_result.duration
        )
        
        if result['success']:
            # Add game simulation details to the response
            result['simulation_details'] = {
                'home_team': {
                    'name': game_result.home_team.full_name,
                    'abbreviation': game_result.home_team.abbreviation,
                    'score': game_result.home_score
                },
                'away_team': {
                    'name': game_result.away_team.full_name,
                    'abbreviation': game_result.away_team.abbreviation,
                    'score': game_result.away_score
                },
                'winner': game_result.winner.abbreviation if game_result.winner else None,
                'duration_minutes': game_result.duration,
                'weather': {
                    'conditions': str(game_result.weather) if game_result.weather else None,
                    'severity': game_result.weather.get_severity_rating() if game_result.weather else None
                }
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error simulating game: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/simulate-week', methods=['POST'])
def simulate_week():
    """Simulate all games in the current week."""
    try:
        data = request.get_json() or {}
        week = data.get('week')
        seed = data.get('seed')
        
        if not season_api.current_season:
            return jsonify({'success': False, 'error': 'No active season'}), 400
        
        # Use current week if not specified
        if week is None:
            week = season_api.current_season.current_week
        
        # Get all games for the week
        week_games_result = season_api.get_week_games(week)
        if not week_games_result['success']:
            return jsonify(week_games_result), 400
        
        games_to_simulate = [
            game for game in week_games_result['games'] 
            if game['status'] == 'scheduled'
        ]
        
        if not games_to_simulate:
            return jsonify({
                'success': True,
                'message': f'No games to simulate in week {week}',
                'week': week,
                'simulated_games': [],
                'season_status': season_api.get_season_status()
            })
        
        simulated_games = []
        
        for i, game_data in enumerate(games_to_simulate):
            game_id = game_data['game_id']
            
            # Find the actual game object
            game = None
            for scheduled_game in season_api.current_season.schedule:
                if scheduled_game.game_id == game_id:
                    game = scheduled_game
                    break
            
            if not game:
                continue
            
            # Create game engine with consistent seed if provided
            game_seed = seed + i if seed else None
            engine = GameEngine(seed=game_seed) if game_seed else GameEngine()
            
            # Simulate the game
            game_result = engine.simulate_game(game.home_team, game.away_team)
            
            # Submit result to season
            season_result = season_api.submit_game_result(
                game_id=game_id,
                home_score=game_result.home_score,
                away_score=game_result.away_score,
                overtime=game_result.duration > 60,
                game_duration=game_result.duration
            )
            
            if season_result['success']:
                simulated_games.append({
                    'game_id': game_id,
                    'home_team': {
                        'name': game_result.home_team.full_name,
                        'abbreviation': game_result.home_team.abbreviation,
                        'score': game_result.home_score
                    },
                    'away_team': {
                        'name': game_result.away_team.full_name,
                        'abbreviation': game_result.away_team.abbreviation,
                        'score': game_result.away_score
                    },
                    'winner': game_result.winner.abbreviation if game_result.winner else None,
                    'duration_minutes': game_result.duration
                })
        
        return jsonify({
            'success': True,
            'message': f'Simulated {len(simulated_games)} games in week {week}',
            'week': week,
            'simulated_games': simulated_games,
            'season_status': season_api.get_season_status()
        })
        
    except Exception as e:
        logger.error(f"Error simulating week: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/simulate-to-week', methods=['POST'])
def simulate_to_week():
    """Simulate all games from current week through target week."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        target_week = data.get('target_week')
        seed = data.get('seed')
        
        if not target_week:
            return jsonify({'success': False, 'error': 'target_week is required'}), 400
        
        if not season_api.current_season:
            return jsonify({'success': False, 'error': 'No active season'}), 400
        
        # Get simulation plan
        plan_result = season_api.simulate_through_week(target_week)
        if not plan_result['success']:
            return jsonify(plan_result), 400
        
        games_to_simulate = plan_result['games_to_simulate']
        
        if not games_to_simulate:
            return jsonify({
                'success': True,
                'message': f'No games to simulate through week {target_week}',
                'target_week': target_week,
                'weeks_simulated': [],
                'simulated_games': [],
                'season_status': season_api.get_season_status()
            })
        
        simulated_games = []
        weeks_simulated = set()
        
        for i, game_data in enumerate(games_to_simulate):
            game_id = game_data['game_id']
            week = game_data['week']
            weeks_simulated.add(week)
            
            # Find the actual game object
            game = None
            for scheduled_game in season_api.current_season.schedule:
                if scheduled_game.game_id == game_id:
                    game = scheduled_game
                    break
            
            if not game:
                continue
            
            # Create game engine with consistent seed if provided
            game_seed = seed + i if seed else None
            engine = GameEngine(seed=game_seed) if game_seed else GameEngine()
            
            # Simulate the game
            game_result = engine.simulate_game(game.home_team, game.away_team)
            
            # Submit result to season
            season_result = season_api.submit_game_result(
                game_id=game_id,
                home_score=game_result.home_score,
                away_score=game_result.away_score,
                overtime=game_result.duration > 60,
                game_duration=game_result.duration
            )
            
            if season_result['success']:
                simulated_games.append({
                    'game_id': game_id,
                    'week': week,
                    'home_team': {
                        'name': game_result.home_team.full_name,
                        'abbreviation': game_result.home_team.abbreviation,
                        'score': game_result.home_score
                    },
                    'away_team': {
                        'name': game_result.away_team.full_name,
                        'abbreviation': game_result.away_team.abbreviation,
                        'score': game_result.away_score
                    },
                    'winner': game_result.winner.abbreviation if game_result.winner else None,
                    'duration_minutes': game_result.duration
                })
        
        return jsonify({
            'success': True,
            'message': f'Simulated {len(simulated_games)} games through week {target_week}',
            'target_week': target_week,
            'weeks_simulated': sorted(list(weeks_simulated)),
            'simulated_games': simulated_games,
            'season_status': season_api.get_season_status()
        })
        
    except Exception as e:
        logger.error(f"Error simulating to week: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@season_bp.route('/simulate-season', methods=['POST'])
def simulate_full_season():
    """Simulate the entire remaining season."""
    try:
        data = request.get_json() or {}
        seed = data.get('seed')
        
        if not season_api.current_season:
            return jsonify({'success': False, 'error': 'No active season'}), 400
        
        # Simulate through week 18 (full regular season)
        return simulate_to_week_internal(18, seed)
        
    except Exception as e:
        logger.error(f"Error simulating full season: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def simulate_to_week_internal(target_week: int, seed: Optional[int] = None):
    """Internal helper for simulating to a target week."""
    # Get simulation plan
    plan_result = season_api.simulate_through_week(target_week)
    if not plan_result['success']:
        return jsonify(plan_result), 400
    
    games_to_simulate = plan_result['games_to_simulate']
    
    if not games_to_simulate:
        return jsonify({
            'success': True,
            'message': f'Season simulation complete - no games remaining',
            'target_week': target_week,
            'weeks_simulated': [],
            'simulated_games': [],
            'season_status': season_api.get_season_status()
        })
    
    simulated_games = []
    weeks_simulated = set()
    
    for i, game_data in enumerate(games_to_simulate):
        game_id = game_data['game_id']
        week = game_data['week']
        weeks_simulated.add(week)
        
        # Find the actual game object
        game = None
        for scheduled_game in season_api.current_season.schedule:
            if scheduled_game.game_id == game_id:
                game = scheduled_game
                break
        
        if not game:
            continue
        
        # Create game engine with consistent seed if provided
        game_seed = seed + i if seed else None
        engine = GameEngine(seed=game_seed) if game_seed else GameEngine()
        
        # Simulate the game
        game_result = engine.simulate_game(game.home_team, game.away_team)
        
        # Submit result to season
        season_result = season_api.submit_game_result(
            game_id=game_id,
            home_score=game_result.home_score,
            away_score=game_result.away_score,
            overtime=game_result.duration > 60,
            game_duration=game_result.duration
        )
        
        if season_result['success']:
            simulated_games.append({
                'game_id': game_id,
                'week': week,
                'home_team': {
                    'name': game_result.home_team.full_name,
                    'abbreviation': game_result.home_team.abbreviation,
                    'score': game_result.home_score
                },
                'away_team': {
                    'name': game_result.away_team.full_name,
                    'abbreviation': game_result.away_team.abbreviation,
                    'score': game_result.away_score
                },
                'winner': game_result.winner.abbreviation if game_result.winner else None,
                'duration_minutes': game_result.duration
            })
    
    return jsonify({
        'success': True,
        'message': f'Simulated {len(simulated_games)} games through week {target_week}',
        'target_week': target_week,
        'weeks_simulated': sorted(list(weeks_simulated)),
        'simulated_games': simulated_games,
        'season_status': season_api.get_season_status()
    })