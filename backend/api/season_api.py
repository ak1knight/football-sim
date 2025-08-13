"""
Season management API for the football simulation engine.

Provides REST API endpoints for season management, scheduling,
standings tracking, and game result processing using database storage.
"""

from typing import Dict, List, Optional, Any
import logging
from flask import current_app

from database.connection import get_db_manager
from database.dao import SeasonDAO, SeasonTeamDAO, SeasonGameDAO, TeamDAO

from .season_formatters import (
    format_season_summary,
    format_season_details,
    format_game,
    format_team_record,
)
from .season_services import (
    generate_season_schedule,
    get_team_season_info,
    get_season_game_count,
    get_completed_game_count,
)

class SeasonAPI:
    """
    REST API for season management using database storage.
    
    Handles season creation, game scheduling, result processing,
    and standings queries with persistent database storage.
    """
    
    def __init__(self):
        """Initialize the Season API."""
        # Use Flask's app logger via current_app in methods
        self.logger = None  # Deprecated, use current_app.logger instead
    
    def create_season(self, user_id: str, season_name: str, season_year: int = 2024,
                     selected_teams: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new season for a user.

        Parameters:
            user_id (str): ID of the user creating the season.
            season_name (str): Name for the season.
            season_year (int, optional): Year for the season. Defaults to 2024.
            selected_teams (Optional[List[str]], optional): List of team IDs to include. Defaults to all NFL teams.

        Returns:
            Dict[str, Any]: Season creation confirmation and initial status.
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"success": False, "error": "Database connection not available"}
            
            season_dao = SeasonDAO(db_manager)
            season_team_dao = SeasonTeamDAO(db_manager)
            team_dao = TeamDAO(db_manager)
            
            # Create the season
            season_id = season_dao.create_season(
                user_id=user_id,
                season_name=season_name,
                season_year=season_year,
                total_weeks=18,
                current_week=1,
                phase='regular_season'
            )
            
            # Get teams to include in season
            if selected_teams:
                teams = []
                for team_id in selected_teams:
                    team = team_dao.get_by_id(team_id)
                    if team:
                        teams.append(team)
            else:
                # Default to all NFL teams
                teams = team_dao.get_all()
            
            if len(teams) < 2:
                return {"success": False, "error": "Season must have at least 2 teams"}
            
            # Add teams to season
            team_ids = [team['id'] for team in teams]
            season_team_dao.bulk_add_teams_to_season(season_id, team_ids)
            
            # Generate and create game schedule
            schedule_success = generate_season_schedule(season_id, teams)
            if not schedule_success:
                return {"success": False, "error": "Failed to generate season schedule"}
            
            # Get created season with teams
            season = season_dao.get_season_with_teams(season_id)
            
            return {
                'success': True,
                'message': f'Season "{season_name}" created successfully',
                'season': format_season_summary(season) if season else None,
                'total_teams': len(teams),
                'total_games': get_season_game_count(season_id)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error creating season: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to create season: {str(e)}'
            }
    
    def get_user_seasons(self, user_id: str, active_only: bool = False) -> Dict[str, Any]:
        """
        Retrieve all seasons for a user.

        Parameters:
            user_id (str): User ID.
            active_only (bool, optional): If True, only return non-completed seasons.

        Returns:
            Dict[str, Any]: List of user's seasons.
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"success": False, "error": "Database connection not available"}
            
            season_dao = SeasonDAO(db_manager)
            seasons = season_dao.get_user_seasons(user_id, active_only=active_only)
            
            formatted_seasons = []
            for season in seasons:
                formatted_seasons.append(format_season_summary(season))
            
            return {
                'success': True,
                'seasons': formatted_seasons,
                'count': len(formatted_seasons)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting user seasons: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get seasons: {str(e)}'
            }
    
    def get_season_status(self, season_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get the current status of a season.

        Parameters:
            season_id (str): Season ID.
            user_id (str): User ID (for authorization).

        Returns:
            Dict[str, Any]: Current season information and progress.
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"success": False, "error": "Database connection not available"}
            
            season_dao = SeasonDAO(db_manager)
            season = season_dao.get_by_id(season_id)
            
            if not season:
                return {"success": False, "error": "Season not found"}
            
            current_app.logger.info(f"Season found: {season}")
            current_app.logger.info(f"User ID: {user_id}, Season User ID: {season['user_id']}")
            if str(season['user_id']) != str(user_id):
                return {"success": False, "error": "Access denied"}
            
            # Get detailed season information
            season_with_teams = season_dao.get_season_with_teams(season_id)
            game_count = get_season_game_count(season_id)
            completed_games = get_completed_game_count(season_id)
            
            return {
                'success': True,
                'season': format_season_details(season_with_teams) if season_with_teams else None,
                'progress': {
                    'games_completed': completed_games,
                    'total_games': game_count,
                    'completion_percentage': round((completed_games / game_count * 100) if game_count > 0 else 0, 1)
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting season status: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get season status: {str(e)}'
            }
    
    def get_next_games(self, season_id: str, user_id: str, limit: int = 16) -> Dict[str, Any]:
        """
        Get the next games that need to be simulated.

        Parameters:
            season_id (str): Season ID.
            user_id (str): User ID (for authorization).
            limit (int, optional): Maximum number of games to return. Defaults to 16.

        Returns:
            Dict[str, Any]: List of games ready for simulation.
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"success": False, "error": "Database connection not available"}
            
            # Verify user access
            if not self._verify_season_access(season_id, user_id):
                return {"success": False, "error": "Season not found or access denied"}
            
            season_game_dao = SeasonGameDAO(db_manager)
            upcoming_games = season_game_dao.get_upcoming_games(season_id, limit=limit)
            
            formatted_games = []
            for game in upcoming_games:
                formatted_games.append(format_game(game))
            
            return {
                'success': True,
                'games': formatted_games,
                'count': len(formatted_games)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting next games: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get next games: {str(e)}'
            }
    
    def get_week_games(self, season_id: str, user_id: str, week: int) -> Dict[str, Any]:
        """
        Get all games for a specific week.

        Parameters:
            season_id (str): Season ID.
            user_id (str): User ID (for authorization).
            week (int): Week number (1-18 for regular season).

        Returns:
            Dict[str, Any]: List of games for the specified week.
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"success": False, "error": "Database connection not available"}
            
            # Verify user access
            if not self._verify_season_access(season_id, user_id):
                return {"success": False, "error": "Season not found or access denied"}
            
            season_game_dao = SeasonGameDAO(db_manager)
            week_games = season_game_dao.get_season_games(season_id, week=week)
            
            formatted_games = []
            for game in week_games:
                formatted_games.append(format_game(game))
            
            return {
                'success': True,
                'week': week,
                'games': formatted_games,
                'count': len(formatted_games)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting week games: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get week {week} games: {str(e)}'
            }
    
    def submit_game_result(self, season_id: str, user_id: str, game_id: str,
                          home_score: int, away_score: int, overtime: bool = False,
                          game_stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Submit the result of a completed game.

        Parameters:
            season_id (str): Season ID.
            user_id (str): User ID (for authorization).
            game_id (str): Unique game identifier.
            home_score (int): Home team's final score.
            away_score (int): Away team's final score.
            overtime (bool, optional): Whether game went to overtime.
            game_stats (Optional[Dict[str, Any]], optional): Optional detailed game statistics.

        Returns:
            Dict[str, Any]: Confirmation of result processing and updated standings.
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"success": False, "error": "Database connection not available"}
            
            # Verify user access
            if not self._verify_season_access(season_id, user_id):
                return {"success": False, "error": "Season not found or access denied"}
            
            # Validate scores
            if home_score < 0 or away_score < 0:
                return {
                    'success': False,
                    'error': 'Scores cannot be negative'
                }
            
            season_game_dao = SeasonGameDAO(db_manager)
            season_team_dao = SeasonTeamDAO(db_manager)
            
            # Get the game
            game = season_game_dao.get_by_id(game_id)
            if not game:
                return {"success": False, "error": "Game not found"}
            
            if game['status'] != 'scheduled':
                return {"success": False, "error": "Game already completed"}
            
            # Update game result
            success = season_game_dao.update_game_result(
                game_id, home_score, away_score, game_stats
            )
            
            if not success:
                return {"success": False, "error": "Failed to update game result"}
            
            # Update team records
            home_won = home_score > away_score
            away_won = away_score > home_score
            
            # Check if this is a division/conference game
            home_team_data = get_team_season_info(season_id, game['home_team_id'])
            away_team_data = get_team_season_info(season_id, game['away_team_id'])
            
            is_division = bool(home_team_data and away_team_data and
                              home_team_data.get('team_conference') == away_team_data.get('team_conference') and
                              home_team_data.get('team_division') == away_team_data.get('team_division'))
            
            is_conference = bool(home_team_data and away_team_data and
                                home_team_data.get('team_conference') == away_team_data.get('team_conference'))
            
            # Update home team record
            season_team_dao.add_game_result(
                season_id, game['home_team_id'], home_won, 
                home_score, away_score, is_division, is_conference
            )
            
            # Update away team record
            season_team_dao.add_game_result(
                season_id, game['away_team_id'], away_won, 
                away_score, home_score, is_division, is_conference
            )
            
            return {
                'success': True,
                'message': f'Game result processed successfully',
                'game_result': {
                    'game_id': game_id,
                    'home_score': home_score,
                    'away_score': away_score,
                    'overtime': overtime
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error submitting game result: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to process game result: {str(e)}'
            }
    
    def get_standings(self, season_id: str, user_id: str, by_division: bool = True) -> Dict[str, Any]:
        """
        Get current league standings.

        Parameters:
            season_id (str): Season ID.
            user_id (str): User ID (for authorization).
            by_division (bool, optional): Whether to organize by division (True) or conference (False).

        Returns:
            Dict[str, Any]: Current standings organized by division or conference.
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"success": False, "error": "Database connection not available"}
            
            # Verify user access
            if not self._verify_season_access(season_id, user_id):
                return {"success": False, "error": "Season not found or access denied"}
            
            season_team_dao = SeasonTeamDAO(db_manager)
            
            if by_division:
                # Get standings organized by division
                standings = {}
                for conference in ['AFC', 'NFC']:
                    standings[conference] = {}
                    for division in ['East', 'West', 'North', 'South']:
                        division_standings = season_team_dao.get_standings(
                            season_id, conference=conference, division=division
                        )
                        if division_standings:
                            standings[conference][division] = division_standings
            else:
                # Get standings by conference
                standings = {}
                for conference in ['AFC', 'NFC']:
                    conference_standings = season_team_dao.get_standings(
                        season_id, conference=conference
                    )
                    standings[conference] = conference_standings
            
            return {
                'success': True,
                'standings': standings,
                'organization': 'division' if by_division else 'conference'
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting standings: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get standings: {str(e)}'
            }
    
    def get_team_schedule(self, season_id: str, user_id: str, team_id: str) -> Dict[str, Any]:
        """
        Get the complete schedule for a specific team.

        Parameters:
            season_id (str): Season ID.
            user_id (str): User ID (for authorization).
            team_id (str): Team ID.

        Returns:
            Dict[str, Any]: Complete schedule for the team.
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"success": False, "error": "Database connection not available"}
            
            # Verify user access
            if not self._verify_season_access(season_id, user_id):
                return {"success": False, "error": "Season not found or access denied"}
            
            season_game_dao = SeasonGameDAO(db_manager)
            season_team_dao = SeasonTeamDAO(db_manager)
            
            # Get team's games
            team_games = season_game_dao.get_team_games(season_id, team_id)
            
            # Get team's season record
            team_season = season_team_dao.get_team_in_season(season_id, team_id)
            
            formatted_games = []
            for game in team_games:
                formatted_games.append(format_game(game))
            
            return {
                'success': True,
                'team_id': team_id,
                'schedule': formatted_games,
                'record': format_team_record(team_season) if team_season else None,
                'total_games': len(formatted_games)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting team schedule: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get team schedule: {str(e)}'
            }
    
    def _verify_season_access(self, season_id: str, user_id: str) -> bool:
        """Verify that user has access to the season."""
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return False
            
            season_dao = SeasonDAO(db_manager)
            season = season_dao.get_by_id(season_id)
            
            return season is not None and str(season['user_id']) == str(user_id)
        except:
            return False
