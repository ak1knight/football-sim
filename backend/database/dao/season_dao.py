import json
"""
Season Data Access Object for the Football Simulation application.

Handles all database operations related to user seasons, including season
creation, management, team associations, and game scheduling.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from sqlalchemy import select, and_, or_, desc
from .base import UserScopedDAO, DAOError
from ..schema import seasons_table, season_teams_table, season_games_table


class SeasonDAO(UserScopedDAO):
    """Data Access Object for Season entities."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager, seasons_table)
    
    def create_season(self, user_id: Union[str, UUID], season_name: str, 
                     season_year: int = 2024, total_weeks: int = 18,
                     current_week: int = 1, phase: str = 'regular_season') -> str:
        """
        Create a new season for a user.
        
        Args:
            user_id: User ID who owns the season
            season_name: Name of the season
            season_year: Year of the season (default 2024)
            total_weeks: Total number of weeks in season (default 18)
            current_week: Current week (default 1)
            phase: Season phase ('regular_season', 'playoffs', 'offseason', 'complete')
            
        Returns:
            Season ID
        """
        season_data = {
            'user_id': user_id,
            'name': season_name,
            'season_year': season_year,
            'current_week': current_week,
            'phase': phase,
            'settings': {
                'playoff_teams': 14,
                'regular_season_weeks': total_weeks,
                'playoff_format': 'standard'
            }
        }
        
        return self.create(season_data)
    
    def get_user_seasons(self, user_id: Union[str, UUID], 
                        active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all seasons for a user.
        
        Args:
            user_id: User ID
            active_only: If True, only return active seasons (not complete)
            
        Returns:
            List of season dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).where(self.table.c.user_id == user_id)
                
                if active_only:
                    query = query.where(self.table.c.phase != 'complete')
                
                query = query.order_by(desc(self.table.c.created_at))
                result = conn.execute(query)
                return self._rows_to_list(list(result.fetchall()))
        except Exception as e:
            self.logger.error(f"Failed to get seasons for user {user_id}: {str(e)}")
            raise DAOError(f"Failed to get user seasons: {str(e)}")
    
    def get_active_season(self, user_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        Get the most recently active season for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Active season dictionary or None if no active season
        """
        try:
            active_seasons = self.get_user_seasons(user_id, active_only=True)
            return active_seasons[0] if active_seasons else None
        except Exception as e:
            self.logger.error(f"Failed to get active season for user {user_id}: {str(e)}")
            return None
    
    def update_season_phase(self, season_id: Union[str, UUID], 
                           phase: str, current_week: Optional[int] = None) -> bool:
        """
        Update season phase and optionally current week.
        
        Args:
            season_id: Season ID
            phase: New phase ('regular_season', 'playoffs', 'offseason', 'complete')
            current_week: Optional current week to set
            
        Returns:
            True if updated successfully, False if season not found
        """
        update_data = {'phase': phase}
        if current_week is not None:
            update_data['current_week'] = str(current_week)
            
        return self.update_by_id(season_id, update_data)
    
    def advance_season_week(self, season_id: Union[str, UUID]) -> bool:
        """
        Advance season to next week.
        
        Args:
            season_id: Season ID
            
        Returns:
            True if advanced successfully, False if season not found
        """
        try:
            season = self.get_by_id(season_id)
            if not season:
                return False
            
            new_week = season['current_week'] + 1
            
            # Check if we need to advance to playoffs
            if season['phase'] == 'regular_season' and new_week > 18:
                return self.update_season_phase(season_id, 'playoffs', 1)
            else:
                return self.update_by_id(season_id, {'current_week': new_week})
                
        except Exception as e:
            self.logger.error(f"Failed to advance season {season_id}: {str(e)}")
            raise DAOError(f"Failed to advance season: {str(e)}")
    
    def update_season_settings(self, season_id: Union[str, UUID], 
                              settings: Dict[str, Any]) -> bool:
        """
        Update season settings.
        
        Args:
            season_id: Season ID
            settings: Dictionary of season settings
            
        Returns:
            True if updated successfully, False if season not found
        """
        return self.update_by_id(season_id, {'season_settings': settings})
    
    def get_season_with_teams(self, season_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        Get season with associated teams.
        
        Args:
            season_id: Season ID
            
        Returns:
            Season dictionary with teams list or None if not found
        """
        try:
            season = self.get_by_id(season_id)
            if not season:
                return None
            
            # Get associated teams - import locally to avoid circular imports
            from .season_team_dao import SeasonTeamDAO
            season_team_dao = SeasonTeamDAO(self.db_manager)
            teams = season_team_dao.get_season_teams(season_id)
            season['teams'] = teams
            
            return season
            
        except Exception as e:
            self.logger.error(f"Failed to get season with teams {season_id}: {str(e)}")
            raise DAOError(f"Failed to get season with teams: {str(e)}")
    
    def get_seasons_by_year(self, user_id: Union[str, UUID], 
                           season_year: int) -> List[Dict[str, Any]]:
        """
        Get all seasons for a user in a specific year.
        
        Args:
            user_id: User ID
            season_year: Season year
            
        Returns:
            List of season dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).where(and_(
                    self.table.c.user_id == user_id,
                    self.table.c.season_year == season_year
                )).order_by(desc(self.table.c.created_at))
                
                result = conn.execute(query)
                return self._rows_to_list(list(result.fetchall()))
        except Exception as e:
            self.logger.error(f"Failed to get seasons for user {user_id} year {season_year}: {str(e)}")
            raise DAOError(f"Failed to get seasons by year: {str(e)}")
    
    def search_seasons(self, user_id: Union[str, UUID], 
                      search_term: str) -> List[Dict[str, Any]]:
        """
        Search user's seasons by name or year.
        
        Args:
            user_id: User ID
            search_term: Term to search for
            
        Returns:
            List of matching season dictionaries
        """
        try:
            search_pattern = f"%{search_term}%"
            
            with self.db_manager.get_db_connection() as conn:
                # Try to parse search term as year
                year_search = None
                try:
                    year_search = int(search_term)
                except ValueError:
                    pass
                
                conditions = [self.table.c.user_id == user_id]
                
                if year_search:
                    conditions.append(or_(
                        self.table.c.name.ilike(search_pattern),
                        self.table.c.season_year == year_search
                    ))
                else:
                    conditions.append(self.table.c.name.ilike(search_pattern))
                
                query = select(self.table).where(and_(*conditions)).order_by(desc(self.table.c.created_at))
                result = conn.execute(query)
                return self._rows_to_list(list(result.fetchall()))
        except Exception as e:
            self.logger.error(f"Failed to search seasons for user {user_id}: {str(e)}")
            raise DAOError(f"Failed to search seasons: {str(e)}")
    
    def complete_season(self, season_id: Union[str, UUID], 
                       final_standings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Mark a season as complete.
        
        Args:
            season_id: Season ID
            final_standings: Optional final standings data
            
        Returns:
            True if marked complete, False if season not found
        """
        update_data = {'phase': 'complete'}
        if final_standings:
            update_data['season_settings'] = json.dumps(final_standings)
            
        return self.update_by_id(season_id, update_data)
    
    def get_season_summary(self, season_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        Get a summary of season information including basic stats.
        
        Args:
            season_id: Season ID
            
        Returns:
            Season summary dictionary or None if not found
        """
        try:
            season = self.get_by_id(season_id)
            if not season:
                return None
            
            # Add computed summary information
            summary = dict(season)
            summary['is_active'] = season['phase'] != 'complete'
            summary['progress_percentage'] = (season['current_week'] / season['settings']['regular_season_weeks']) * 100
            summary['phase_display'] = season['phase'].replace('_', ' ').title()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get season summary {season_id}: {str(e)}")
            return None