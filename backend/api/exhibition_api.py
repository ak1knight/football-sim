"""
Exhibition game API for running individual game simulations.

This API allows users to simulate games between any two teams
with customizable conditions like weather.
"""

from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional, List
import logging

from database.connection import get_db_manager
from database.dao import TeamDAO
from simulation.game_engine import GameEngine
from models.weather import Weather, WeatherCondition, WindDirection
from models.team import Team as TeamModel, TeamStats # Import the Team model and TeamStats for GameEngine

exhibition_bp = Blueprint('exhibition', __name__)
logger = logging.getLogger(__name__)


@exhibition_bp.route('/teams', methods=['GET'])
def get_teams():
    """Get all available teams for selection from the database."""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            return jsonify({"success": False, "error": "Database connection not available"}), 500
        
        team_dao = TeamDAO(db_manager)
        teams = team_dao.get_all()
        
        teams_data = []
        for team in teams:
            teams_data.append(_format_team_data(team))
        
        # Sort teams alphabetically by city + name
        teams_data.sort(key=lambda x: f"{x['city']} {x['name']}")
        
        return jsonify({
            'success': True,
            'teams': teams_data,
            'total_teams': len(teams_data)
        })
    
    except Exception as e:
        logger.error(f"Error getting teams: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve teams: {str(e)}'
        }), 500


@exhibition_bp.route('/simulate', methods=['POST'])
def simulate_exhibition_game():
    """
    Simulate an exhibition game between two teams using database-backed team data.
    
    Expected JSON payload:
    {
        "home_team_id": "uuid-of-home-team",
        "away_team_id": "uuid-of-away-team",
        "weather": {
            "condition": "clear",
            "temperature": 72,
            "wind_speed": 5,
            "wind_direction": "N"
        },
        "game_settings": {
            "overtime": true,
            "detailed_stats": true
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['home_team_id', 'away_team_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        home_team_id = data['home_team_id']
        away_team_id = data['away_team_id']
        
        db_manager = get_db_manager()
        if not db_manager:
            return jsonify({"success": False, "error": "Database connection not available"}), 500
        
        team_dao = TeamDAO(db_manager)
        
        # Retrieve teams from the database
        home_team_data = team_dao.get_by_id(home_team_id)
        away_team_data = team_dao.get_by_id(away_team_id)
        
        if not home_team_data:
            return jsonify({
                'success': False,
                'error': f'Home team with ID "{home_team_id}" not found'
            }), 400
        
        if not away_team_data:
            return jsonify({
                'success': False,
                'error': f'Away team with ID "{away_team_id}" not found'
            }), 400
        
        # Convert dictionary data to TeamModel instances for GameEngine
        home_team = TeamModel(
            name=home_team_data['name'],
            city=home_team_data['city'],
            abbreviation=home_team_data['abbreviation'],
            conference=home_team_data['conference'],
            division=home_team_data['division'],
            stats=TeamStats(**home_team_data['team_stats']) # Pass as TeamStats object
        )
        away_team = TeamModel(
            name=away_team_data['name'],
            city=away_team_data['city'],
            abbreviation=away_team_data['abbreviation'],
            conference=away_team_data['conference'],
            division=away_team_data['division'],
            stats=TeamStats(**away_team_data['team_stats']) # Pass as TeamStats object
        )
        
        # Parse weather conditions
        weather_data = data.get('weather', {})
        weather = _create_weather_condition(weather_data)
        
        # Parse game settings
        game_settings = data.get('game_settings', {})
        detailed_stats_requested = game_settings.get('detailed_stats', False)
        
        # Create and run the game simulation
        game_engine = GameEngine(
            weather=weather,
            enable_reporting=detailed_stats_requested,
            verbose=False
        )
        
        # Run the simulation
        result = game_engine.simulate_game(home_team, away_team)
        
        # Format the response
        response_data = {
            'success': True,
            'game_result': {
                'home_team': _format_team_data(home_team_data),
                'away_team': _format_team_data(away_team_data),
                'final_score': f"{result.away_score} - {result.home_score}",
                'winner': _determine_winner(result, home_team, away_team),
                'overtime': False,  # GameResult doesn't track this currently
                'game_duration': result.duration,
                'weather': {
                    'condition': weather.condition.value if weather else 'clear',
                    'temperature': weather.temperature if weather else 72,
                    'wind_speed': weather.wind_speed if weather else 0,
                    'wind_direction': weather.wind_direction.value if weather else 'N'
                }
            }
        }
        
        # Add detailed stats if requested
        if game_settings.get('detailed_stats', False):
            response_data['game_result']['detailed_stats'] = _format_detailed_stats(game_engine, result)
            response_data['game_result']['drive_summary'] = _format_drive_summary(game_engine)
            response_data['game_result']['key_plays'] = _format_key_plays(game_engine)
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error simulating exhibition game: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to simulate game: {str(e)}'
        }), 500


def _format_team_data(team: Dict[str, Any]) -> Dict[str, Any]:
    """Format team data for API response."""
    return {
        'id': team['id'],
        'abbreviation': team['abbreviation'],
        'name': team['name'],
        'city': team['city'],
        'conference': team['conference'],
        'division': team['division'],
        'colors': { # Default colors, could be enhanced from DB if added
            'primary': '#1f2937',
            'secondary': '#6b7280'
        }
    }


def _create_weather_condition(weather_data: Dict[str, Any]) -> Optional[Weather]:
    """Create a Weather object from API data."""
    if not weather_data:
        return None
    
    try:
        # Map condition strings to enum values
        condition_map = {
            'clear': WeatherCondition.CLEAR,
            'cloudy': WeatherCondition.CLOUDY,
            'rainy': WeatherCondition.LIGHT_RAIN,
            'rain': WeatherCondition.LIGHT_RAIN,
            'snowy': WeatherCondition.LIGHT_SNOW,
            'snow': WeatherCondition.LIGHT_SNOW,
            'windy': WeatherCondition.CLEAR  # Clear but windy
        }
        
        condition_str = weather_data.get('condition', 'clear').lower()
        condition = condition_map.get(condition_str, WeatherCondition.CLEAR)
        
        # Get temperature
        temperature = weather_data.get('temperature', 72)
        
        # Get wind info
        wind_speed = weather_data.get('wind_speed', 0)
        wind_direction_str = weather_data.get('wind_direction', 'N')
        
        # Map wind direction to enum (simplified)
        wind_direction = WindDirection.NONE if wind_speed < 5 else WindDirection.CROSSWIND
        
        return Weather(
            condition=condition,
            temperature=temperature,
            wind_speed=wind_speed,
            wind_direction=wind_direction
        )
    
    except Exception:
        # Return default weather if parsing fails
        return Weather()


def _determine_winner(result, home_team: TeamModel, away_team: TeamModel) -> Dict[str, Any]:
    """Determine the winning team."""
    if result.home_score > result.away_score:
        return {
            'team': {
                'abbreviation': home_team.abbreviation,
                'name': home_team.name,
                'city': home_team.city
            },
            'margin': result.home_score - result.away_score
        }
    elif result.away_score > result.home_score:
        return {
            'team': {
                'abbreviation': away_team.abbreviation,
                'name': away_team.name,
                'city': away_team.city
            },
            'margin': result.away_score - result.home_score
        }
    else:
        return {
            'team': None,
            'margin': 0,
            'tie': True
        }


def _format_detailed_stats(game_engine, result) -> Dict[str, Any]:
    """Format detailed game statistics from the game reporter."""
    if not game_engine.reporter or not game_engine.reporter.current_game:
        # Fallback to basic stats if no reporter data
        return {
            'total_plays': 0,
            'total_drives': 0,
            'turnovers': {'home': 0, 'away': 0},
            'time_of_possession': {'home': 30, 'away': 30},
            'yards_gained': {'home': 0, 'away': 0},
            'plays_by_type': {'run': 0, 'pass': 0, 'turnover': 0}
        }
    
    game_report = game_engine.reporter.current_game
    
    # Initialize counters
    total_plays = 0
    total_drives = 0
    home_yards = 0
    away_yards = 0
    home_plays = 0
    away_plays = 0
    home_turnovers = 0
    away_turnovers = 0
    
    play_type_counts = {'run': 0, 'pass': 0, 'turnover': 0}
    
    # Analyze all drives
    for quarter in game_report.quarters:
        for drive in quarter.drives:
            total_drives += 1
            
            # Determine if this is a home or away drive
            is_home_drive = (drive.offense == game_report.home_team)
            
            for play in drive.plays:
                total_plays += 1
                
                # Count plays by team
                if is_home_drive:
                    home_plays += 1
                    home_yards += play.yards_gained
                else:
                    away_plays += 1
                    away_yards += play.yards_gained
                
                # Count play types
                if play.play_type in play_type_counts:
                    play_type_counts[play.play_type] += 1
                
                # Count turnovers
                if play.play_type == 'turnover':
                    if is_home_drive:
                        home_turnovers += 1
                    else:
                        away_turnovers += 1
    
    # Calculate time of possession (simplified estimate based on plays)
    total_game_plays = max(home_plays + away_plays, 1)
    home_top_percentage = home_plays / total_game_plays
    home_top_minutes = round(home_top_percentage * 60)
    away_top_minutes = 60 - home_top_minutes
    
    return {
        'total_plays': total_plays,
        'total_drives': total_drives,
        'turnovers': {
            'home': home_turnovers,
            'away': away_turnovers
        },
        'time_of_possession': {
            'home': home_top_minutes,
            'away': away_top_minutes
        },
        'yards_gained': {
            'home': home_yards,
            'away': away_yards
        },
        'plays_by_type': play_type_counts,
        'average_yards_per_play': {
            'home': round(home_yards / max(home_plays, 1), 1),
            'away': round(away_yards / max(away_plays, 1), 1)
        }
    }


def _format_drive_summary(game_engine) -> List[Dict[str, Any]]:
    """Format drive summary from the game reporter."""
    if not game_engine.reporter or not game_engine.reporter.current_game:
        return []
    
    game_report = game_engine.reporter.current_game
    drive_summary = []
    
    drive_count = 0
    for quarter in game_report.quarters:
        for drive in quarter.drives:
            drive_count += 1
            
            drive_summary.append({
                'drive_number': drive_count,
                'quarter': quarter.quarter,
                'offense': drive.offense,
                'starting_position': drive.starting_position,
                'result': drive.result,
                'points': drive.points,
                'total_plays': drive.total_plays,
                'total_yards': drive.total_yards,
                'plays': [
                    {
                        'down': play.down,
                        'yards_to_go': play.yards_to_go,
                        'play_type': play.play_type,
                        'yards_gained': play.yards_gained,
                        'description': play.description
                    }
                    for play in drive.plays
                ]
            })
    
    return drive_summary


def _format_key_plays(game_engine) -> List[Dict[str, Any]]:
    """Format key plays for the response from the game reporter."""
    if not game_engine.reporter or not game_engine.reporter.current_game:
        return []
    
    game_report = game_engine.reporter.current_game
    key_plays = []
    
    # Find scoring plays and big plays
    for quarter in game_report.quarters:
        for drive in quarter.drives:
            # Add scoring drive summary as a key play
            if drive.points > 0:
                key_plays.append({
                    'quarter': quarter.quarter,
                    'time': '??:??',  # Time tracking not implemented yet
                    'description': f"{drive.offense} {drive.result.replace('_', ' ').title()} - {drive.points} points ({drive.total_plays} plays, {drive.total_yards} yards)",
                    'scoring_play': True,
                    'points': drive.points
                })
            
            # Add big plays (15+ yards or turnovers)
            for play in drive.plays:
                if play.yards_gained >= 15 or play.play_type == 'turnover':
                    key_plays.append({
                        'quarter': quarter.quarter,
                        'time': '??:??',  # Time tracking not implemented yet
                        'description': f"{drive.offense}: {play.description}",
                        'scoring_play': False,
                        'yards': play.yards_gained,
                        'play_type': play.play_type
                    })
    
    # Sort by importance (scoring plays first, then by yards gained)
    key_plays.sort(key=lambda x: (not x['scoring_play'], -x.get('yards', 0)))
    
    # Return top 10 plays
    return key_plays[:10]


# Error handlers
@exhibition_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@exhibition_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
