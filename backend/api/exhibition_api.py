"""
Exhibition game API for running individual game simulations.

This API allows users to simulate games between any two teams
with customizable conditions like weather.
"""

from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.team_loader import load_sample_teams
from simulation.game_engine import GameEngine
from models.weather import Weather, WeatherCondition, WindDirection

exhibition_bp = Blueprint('exhibition', __name__)


@exhibition_bp.route('/teams', methods=['GET'])
def get_teams():
    """Get all available teams for selection."""
    try:
        teams = load_sample_teams()
        
        teams_data = []
        for team in teams:
            teams_data.append({
                'abbreviation': team.abbreviation,
                'name': team.name,
                'city': team.city,
                'conference': team.conference,
                'division': team.division,
                'colors': {
                    'primary': '#1f2937',  # Default colors, could be enhanced
                    'secondary': '#6b7280'
                }
            })
        
        # Sort teams alphabetically by city + name
        teams_data.sort(key=lambda x: f"{x['city']} {x['name']}")
        
        return jsonify({
            'success': True,
            'teams': teams_data,
            'total_teams': len(teams_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@exhibition_bp.route('/simulate', methods=['POST'])
def simulate_exhibition_game():
    """
    Simulate an exhibition game between two teams.
    
    Expected JSON payload:
    {
        "home_team": "KC",
        "away_team": "BUF",
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
        required_fields = ['home_team', 'away_team']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        home_team_abbr = data['home_team']
        away_team_abbr = data['away_team']
        
        # Load teams
        teams = load_sample_teams()
        teams_dict = {team.abbreviation: team for team in teams}
        
        # Find the specified teams
        if home_team_abbr not in teams_dict:
            return jsonify({
                'success': False,
                'error': f'Home team "{home_team_abbr}" not found'
            }), 400
        
        if away_team_abbr not in teams_dict:
            return jsonify({
                'success': False,
                'error': f'Away team "{away_team_abbr}" not found'
            }), 400
        
        home_team = teams_dict[home_team_abbr]
        away_team = teams_dict[away_team_abbr]
        
        # Parse weather conditions
        weather_data = data.get('weather', {})
        weather = _create_weather_condition(weather_data)
        
        # Parse game settings
        game_settings = data.get('game_settings', {})
        
        # Create and run the game simulation
        game_engine = GameEngine(weather=weather)
        
        # Run the simulation
        result = game_engine.simulate_game(home_team, away_team)
        
        # Format the response
        response_data = {
            'success': True,
            'game_result': {
                'home_team': {
                    'abbreviation': home_team.abbreviation,
                    'name': home_team.name,
                    'city': home_team.city,
                    'score': result.home_score
                },
                'away_team': {
                    'abbreviation': away_team.abbreviation,
                    'name': away_team.name,
                    'city': away_team.city,
                    'score': result.away_score
                },
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
            response_data['game_result']['detailed_stats'] = _format_detailed_stats(result)
        
        # Add play-by-play if available
        if hasattr(result, 'plays') and result.plays:
            response_data['game_result']['key_plays'] = _format_key_plays(result.plays[:10])  # Top 10 plays
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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


def _determine_winner(result, home_team, away_team) -> Dict[str, Any]:
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


def _format_detailed_stats(result) -> Dict[str, Any]:
    """Format detailed game statistics."""
    return {
        'total_plays': getattr(result, 'total_plays', 0),
        'turnovers': {
            'home': getattr(result, 'home_turnovers', 0),
            'away': getattr(result, 'away_turnovers', 0)
        },
        'penalties': {
            'home': getattr(result, 'home_penalties', 0),
            'away': getattr(result, 'away_penalties', 0)
        },
        'time_of_possession': {
            'home': getattr(result, 'home_top_minutes', 30),
            'away': getattr(result, 'away_top_minutes', 30)
        }
    }


def _format_key_plays(plays) -> list:
    """Format key plays for the response."""
    formatted_plays = []
    
    for play in plays:
        formatted_plays.append({
            'quarter': getattr(play, 'quarter', 1),
            'time': getattr(play, 'time_remaining', '15:00'),
            'description': getattr(play, 'description', 'Play occurred'),
            'scoring_play': getattr(play, 'is_scoring_play', False)
        })
    
    return formatted_plays


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
