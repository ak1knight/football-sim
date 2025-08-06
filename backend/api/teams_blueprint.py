"""
Flask blueprint for team endpoints.
"""

from flask import Blueprint, jsonify
from api.team_api import TeamAPI

# Create blueprint
teams_bp = Blueprint('teams', __name__)

# Initialize API
team_api = TeamAPI()

@teams_bp.route('/', methods=['GET'])
def get_all_teams():
    """Get all teams endpoint."""
    result = team_api.get_all_teams()
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result)

@teams_bp.route('/<team_id>', methods=['GET'])
def get_team_details(team_id):
    """Get specific team details."""
    result = team_api.get_team_details(team_id)
    
    if 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result)

@teams_bp.route('/<team_id>/roster', methods=['GET'])
def get_team_roster(team_id):
    """Get team roster."""
    result = team_api.get_team_roster(team_id)
    
    if 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result)

@teams_bp.route('/<team_id>/stats', methods=['GET'])
def get_team_stats(team_id):
    """Get team statistics."""
    result = team_api.get_team_stats(team_id)
    
    if 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result)

@teams_bp.route('/compare/<team1_id>/<team2_id>', methods=['GET'])
def compare_teams(team1_id, team2_id):
    """Compare two teams."""
    result = team_api.compare_teams(team1_id, team2_id)
    
    if 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result)