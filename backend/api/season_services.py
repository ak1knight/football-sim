from typing import Dict, List, Any, Optional
import logging
from database.connection import get_db_manager
from database.dao import SeasonDAO, SeasonTeamDAO, SeasonGameDAO

logger = logging.getLogger(__name__)

def generate_season_schedule(season_id: str, teams: List[Dict[str, Any]]) -> bool:
    """Generate and save season schedule."""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            return False

        # Debug: Log teams list for troubleshooting
        logger.error(f"generate_season_schedule: teams={teams}")

        # Simple schedule generation - each team plays each other once (round-robin)
        season_game_dao = SeasonGameDAO(db_manager)
        games_data = []

        week = 1
        game_count = 0
        max_games_per_week = 16

        for i, home_team in enumerate(teams):
            for j, away_team in enumerate(teams):
                if i != j and i < j:
                    games_data.append({
                        'season_id': season_id,
                        'game_id': f"{season_id}_W{week:02d}_G{i:02d}_{j:02d}",
                        'week': week,
                        'home_team_id': home_team.get('id'),
                        'away_team_id': away_team.get('id'),
                        'home_score': 0,
                        'away_score': 0,
                        'status': 'scheduled',
                        'game_date': None,
                        'weather_conditions': {},
                        'game_data': {},
                        'play_by_play': []
                    })
                    game_count += 1
                    if game_count >= max_games_per_week:
                        week += 1
                        game_count = 0

        if games_data:
            season_game_dao.bulk_create_games(games_data)
        return True

    except Exception as e:
        logger.error(f"Error generating schedule: {str(e)} | teams={teams}")
        return False

def get_season_game_count(season_id: str) -> int:
    """Get total number of games in season."""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            return 0

        season_game_dao = SeasonGameDAO(db_manager)
        games = season_game_dao.get_season_games(season_id)
        return len(games)
    except Exception:
        return 0

def get_completed_game_count(season_id: str) -> int:
    """Get number of completed games in season."""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            return 0

        season_game_dao = SeasonGameDAO(db_manager)
        completed_games = season_game_dao.get_completed_games(season_id)
        return len(completed_games)
    except Exception:
        return 0

def get_team_season_info(season_id: str, team_id: str) -> Optional[Dict[str, Any]]:
    """Get team information in a season context."""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            return None

        season_team_dao = SeasonTeamDAO(db_manager)
        teams = season_team_dao.get_season_teams(season_id)

        for team in teams:
            if team['team_id'] == team_id:
                return team
        return None
    except Exception:
        return None