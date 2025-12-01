from typing import Dict, List, Any, Optional
import logging
from database.connection import get_db_manager
from database.dao import SeasonDAO, SeasonTeamDAO, SeasonGameDAO
from models.team import Team
from simulation.season_engine import SeasonEngine
from simulation.schedule_generators import NFLScheduleGenerator

logger = logging.getLogger(__name__)

def generate_season_schedule(season_id: str, teams: List[Dict[str, Any]]) -> bool:
    """Generate and save season schedule."""
    try:
        db_manager = get_db_manager()
        if not db_manager:
            return False

        season_dao = SeasonDAO(db_manager)
        season = season_dao.get_by_id(season_id)
        season_year = season['season_year'] if season else 2024
        seed = season.get('seed') if season else None

        season_game_dao = SeasonGameDAO(db_manager)

        # Normalize incoming records into Team objects and keep ID lookup
        team_lookup = {}
        team_id_lookup = {}
        for raw in teams:
            abbr = raw.get('team_abbreviation') or raw.get('abbreviation')
            if not abbr:
                continue
            team_lookup[abbr] = Team(
                name=raw.get('team_name') or raw.get('name'),
                city=raw.get('team_city') or raw.get('city'),
                abbreviation=abbr,
                conference=raw.get('team_conference') or raw.get('conference'),
                division=raw.get('team_division') or raw.get('division'),
            )
            team_id_lookup[abbr] = raw.get('team_id') or raw.get('id')

        engine = SeasonEngine(
            teams=list(team_lookup.values()),
            season_year=season_year,
            seed=seed,
            schedule_generator=NFLScheduleGenerator(),
        )

        games_data = []
        for game in engine.schedule:
            home_id = team_id_lookup.get(game.home_team.abbreviation)
            away_id = team_id_lookup.get(game.away_team.abbreviation)
            games_data.append({
                'season_id': season_id,
                'game_id': game.game_id,
                'week': game.week,
                'home_team_id': home_id,
                'away_team_id': away_id,
                'home_score': game.home_score or 0,
                'away_score': game.away_score or 0,
                'status': game.status.value,
                'game_date': game.scheduled_date,
                'weather_conditions': {},
                'game_data': {},
                'play_by_play': [],
            })

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
