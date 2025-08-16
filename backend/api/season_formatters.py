from typing import Dict, Any, Optional

def format_season_summary(season: Dict[str, Any]) -> Dict[str, Any]:
    """Format season for API response (summary version)."""
    return {
        'id': season['id'],
        'season_name': season['name'],
        'season_year': season['season_year'],
        'current_week': season['current_week'],
        'total_weeks': season['settings']['regular_season_weeks'],
        'phase': season['phase'],
        'created_at': season['created_at'].isoformat() if season.get('created_at') else None,
        'is_active': season['phase'] != 'complete'
    }

def format_season_details(season: Dict[str, Any]) -> Dict[str, Any]:
    """Format season for API response (detailed version)."""
    summary = format_season_summary(season)
    summary.update({
        'teams': season.get('teams', []),
        'team_count': len(season.get('teams', [])),
        'settings': season.get('season_settings', {})
    })
    return summary

def format_game(game: Dict[str, Any]) -> Dict[str, Any]:
    """Format game for API response."""
    return {
        'id': game['id'],
        'week': game['week'],
        #'game_type': game['game_type'],
        'status': game['status'],
        'home_team': {
            'id': game['home_team_id'],
            'name': game.get('home_team_name', ''),
            'city': game.get('home_team_city', ''),
            'abbreviation': game.get('home_team_abbr', '')
        },
        'away_team': {
            'id': game['away_team_id'],
            'name': game.get('away_team_name', ''),
            'city': game.get('away_team_city', ''),
            'abbreviation': game.get('away_team_abbr', '')
        },
        'home_score': game['home_score'],
        'away_score': game['away_score'],
        'scheduled_date': format_datetime(game.get('scheduled_date')),
        'completed_at': format_datetime(game.get('completed_at'))
    }

def format_team_record(team_season: Dict[str, Any]) -> Dict[str, Any]:
    """Format team record for API response."""
    if not team_season:
        return {}
    return {
        'wins': team_season['wins'],
        'losses': team_season['losses'],
        'ties': team_season['ties'],
        'points_for': team_season['points_for'],
        'points_against': team_season['points_against'],
        'point_differential': team_season['points_for'] - team_season['points_against'],
        'division_record': {
            'wins': team_season['division_wins'],
            'losses': team_season['division_losses']
        },
        'conference_record': {
            'wins': team_season['conference_wins'],
            'losses': team_season['conference_losses']
        }
    }

def format_datetime(dt) -> Optional[str]:
    """Format datetime for API response."""
    if dt and hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return None