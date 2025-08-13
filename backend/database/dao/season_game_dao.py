"""
Season Game Data Access Object for the Football Simulation application.

Handles all database operations related to games within user seasons,
including game scheduling, results, and statistics tracking.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, desc, asc
from .base import BaseDAO, DAOError
from ..schema import season_games_table


class SeasonGameDAO(BaseDAO):
    """Data Access Object for Season Game entities."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager, season_games_table)
    
    def create_game(self, season_id: Union[str, UUID], home_team_id: Union[str, UUID],
                   away_team_id: Union[str, UUID], week: int, 
                   game_date: Optional[datetime] = None) -> str:
        """
        Create a new game in a season.
        
        Args:
            season_id: Season ID
            home_team_id: Home team ID
            away_team_id: Away team ID
            week: Week number
            game_date: Optional scheduled date/time
            
        Returns:
            Game ID
        """
        game_data = {
            'season_id': season_id,
            'home_team_id': home_team_id,
            'away_team_id': away_team_id,
            'week': week,
            'status': 'scheduled',
            'game_date': game_date,
            'home_score': 0,
            'away_score': 0,
            '': {}
        }
        
        return self.create(game_data)
    
    def get_season_games(self, season_id: Union[str, UUID], 
                        week: Optional[int] = None,
                        status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get games for a season, optionally filtered by week or status.
        
        Args:
            season_id: Season ID
            week: Optional week filter
            status: Optional status filter ('scheduled', 'in_progress', 'completed', 'cancelled')
            
        Returns:
            List of game dictionaries with team information
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                # Join with teams table to get team names
                from ..schema import teams_table
                
                home_teams = teams_table.alias('home_teams')
                away_teams = teams_table.alias('away_teams')
                
                query = select(
                    self.table.c.id,
                    self.table.c.season_id,
                    self.table.c.week,
                    self.table.c.status,
                    self.table.c.game_date,
                    self.table.c.home_score,
                    self.table.c.away_score,
                    self.table.c.home_team_id,
                    self.table.c.away_team_id,
                    home_teams.c.name.label('home_team_name'),
                    home_teams.c.city.label('home_team_city'),
                    home_teams.c.abbreviation.label('home_team_abbr'),
                    away_teams.c.name.label('away_team_name'),
                    away_teams.c.city.label('away_team_city'),
                    away_teams.c.abbreviation.label('away_team_abbr')
                ).select_from(
                    self.table
                    .join(home_teams, self.table.c.home_team_id == home_teams.c.id)
                    .join(away_teams, self.table.c.away_team_id == away_teams.c.id)
                ).where(self.table.c.season_id == season_id)
                
                if week is not None:
                    query = query.where(self.table.c.week == week)
                if status:
                    query = query.where(self.table.c.status == status)
                
                query = query.order_by(self.table.c.week, self.table.c.game_date)
                
                result = conn.execute(query)
                return self._rows_to_list(list(result.fetchall()))
        except Exception as e:
            self.logger.error(f"Failed to get games for season {season_id}: {str(e)}")
            raise DAOError(f"Failed to get season games: {str(e)}")
    
    def get_team_games(self, season_id: Union[str, UUID], team_id: Union[str, UUID],
                      completed_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all games for a specific team in a season.
        
        Args:
            season_id: Season ID
            team_id: Team ID
            completed_only: If True, only return completed games
            
        Returns:
            List of game dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                conditions = [
                    self.table.c.season_id == season_id,
                    or_(
                        self.table.c.home_team_id == team_id,
                        self.table.c.away_team_id == team_id
                    )
                ]
                
                if completed_only:
                    conditions.append(self.table.c.status == 'completed')
                
                query = select(self.table).where(and_(*conditions)).order_by(self.table.c.week)
                result = conn.execute(query)
                return self._rows_to_list(list(result.fetchall()))
        except Exception as e:
            self.logger.error(f"Failed to get games for team {team_id}: {str(e)}")
            raise DAOError(f"Failed to get team games: {str(e)}")
    
    def update_game_result(self, game_id: Union[str, UUID], home_score: int, away_score: int) -> bool:
        """
        Update game result and mark as completed.

        Args:
            game_id: Game ID
            home_score: Home team final score
            away_score: Away team final score

        Returns:
            True if updated successfully, False if game not found
        """
        update_data = {
            'home_score': home_score,
            'away_score': away_score,
            'status': 'completed',
        }
        return self.update_by_id(game_id, update_data)
    
    def set_game_status(self, game_id: Union[str, UUID], status: str) -> bool:
        """
        Update game status.
        
        Args:
            game_id: Game ID
            status: New status ('scheduled', 'in_progress', 'completed', 'cancelled')
            
        Returns:
            True if updated successfully, False if game not found
        """
        return self.update_by_id(game_id, {'status': status})
    
    def get_week_schedule(self, season_id: Union[str, UUID], week: int) -> List[Dict[str, Any]]:
        """
        Get all games scheduled for a specific week.
        
        Args:
            season_id: Season ID
            week: Week number
            
        Returns:
            List of game dictionaries for the week
        """
        return self.get_season_games(season_id, week=week)
    
    def get_completed_games(self, season_id: Union[str, UUID], 
                           limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get completed games for a season, ordered by completion date.
        
        Args:
            season_id: Season ID
            limit: Optional limit on number of results
            
        Returns:
            List of completed game dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).where(and_(
                    self.table.c.season_id == season_id,
                    self.table.c.status == 'completed'
                )).order_by(desc(self.table.c.game_date))
                
                if limit:
                    query = query.limit(limit)
                
                result = conn.execute(query)
                return self._rows_to_list(list(result.fetchall()))
        except Exception as e:
            self.logger.error(f"Failed to get completed games for season {season_id}: {str(e)}")
            raise DAOError(f"Failed to get completed games: {str(e)}")
    
    def get_upcoming_games(self, season_id: Union[str, UUID], 
                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get upcoming games for a season.
        
        Args:
            season_id: Season ID
            limit: Optional limit on number of results
            
        Returns:
            List of upcoming game dictionaries
        """
        return self.get_season_games(season_id, status='scheduled')[:limit] if limit else self.get_season_games(season_id, status='scheduled')
    
    def bulk_create_games(self, games_data: List[Dict[str, Any]]) -> List[str]:
        """
        Create multiple games in bulk.
        
        Args:
            games_data: List of game dictionaries
            
        Returns:
            List of created game IDs
        """
        # Ensure all games have required defaults
        for game_data in games_data:
            game_data.setdefault('status', 'scheduled')
            game_data.setdefault('home_score', 0)
            game_data.setdefault('away_score', 0)
        
        return self.bulk_insert(games_data)
    
    def get_head_to_head(self, season_id: Union[str, UUID], 
                        team1_id: Union[str, UUID], team2_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        Get all games between two teams in a season.
        
        Args:
            season_id: Season ID
            team1_id: First team ID
            team2_id: Second team ID
            
        Returns:
            List of games between the two teams
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).where(and_(
                    self.table.c.season_id == season_id,
                    or_(
                        and_(
                            self.table.c.home_team_id == team1_id,
                            self.table.c.away_team_id == team2_id
                        ),
                        and_(
                            self.table.c.home_team_id == team2_id,
                            self.table.c.away_team_id == team1_id
                        )
                    )
                )).order_by(self.table.c.week)
                
                result = conn.execute(query)
                return self._rows_to_list(list(result.fetchall()))
        except Exception as e:
            self.logger.error(f"Failed to get head-to-head games: {str(e)}")
            raise DAOError(f"Failed to get head-to-head games: {str(e)}")
    
    def get_playoff_games(self, season_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        Get all playoff games for a season.
        
        Args:
            season_id: Season ID
            
        Returns:
            List of playoff game dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).where(and_(
                    self.table.c.season_id == season_id,
                    # Removed game_type filter; column does not exist
                )).order_by(self.table.c.week, self.table.c.game_date)
                
                result = conn.execute(query)
                return self._rows_to_list(list(result.fetchall()))
        except Exception as e:
            self.logger.error(f"Failed to get playoff games for season {season_id}: {str(e)}")
            raise DAOError(f"Failed to get playoff games: {str(e)}")
    
    def delete_season_games(self, season_id: Union[str, UUID]) -> int:
        """
        Delete all games for a season.
        
        Args:
            season_id: Season ID
            
        Returns:
            Number of games deleted
        """
        try:
            with self.db_manager.get_db_transaction() as conn:
                from sqlalchemy import delete
                result = conn.execute(
                    delete(self.table).where(self.table.c.season_id == season_id)
                )
                deleted_count = result.rowcount
                if deleted_count > 0:
                    self.logger.debug(f"Deleted {deleted_count} games for season {season_id}")
                return deleted_count
        except Exception as e:
            self.logger.error(f"Failed to delete games for season {season_id}: {str(e)}")
            raise DAOError(f"Failed to delete season games: {str(e)}")
    
    def get_team_record_vs_opponent(self, season_id: Union[str, UUID], 
                                   team_id: Union[str, UUID], 
                                   opponent_id: Union[str, UUID]) -> Dict[str, int]:
        """
        Get a team's record against a specific opponent.
        
        Args:
            season_id: Season ID
            team_id: Team ID
            opponent_id: Opponent team ID
            
        Returns:
            Dictionary with wins, losses, and ties
        """
        try:
            games = self.get_head_to_head(season_id, team_id, opponent_id)
            completed_games = [g for g in games if g['status'] == 'completed']
            
            wins = 0
            losses = 0
            ties = 0
            
            for game in completed_games:
                if game['home_team_id'] == str(team_id):
                    # Team was home
                    if game['home_score'] > game['away_score']:
                        wins += 1
                    elif game['home_score'] < game['away_score']:
                        losses += 1
                    else:
                        ties += 1
                else:
                    # Team was away
                    if game['away_score'] > game['home_score']:
                        wins += 1
                    elif game['away_score'] < game['home_score']:
                        losses += 1
                    else:
                        ties += 1
            
            return {'wins': wins, 'losses': losses, 'ties': ties}
            
        except Exception as e:
            self.logger.error(f"Failed to get team record vs opponent: {str(e)}")
            return {'wins': 0, 'losses': 0, 'ties': 0}
    
    def get_game_summary_stats(self, season_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Get summary statistics for all games in a season.
        
        Args:
            season_id: Season ID
            
        Returns:
            Dictionary with game summary statistics
        """
        try:
            games = self.get_season_games(season_id)
            
            total_games = len(games)
            completed_games = len([g for g in games if g['status'] == 'completed'])
            scheduled_games = len([g for g in games if g['status'] == 'scheduled'])
            
            if completed_games > 0:
                completed_game_list = [g for g in games if g['status'] == 'completed']
                total_points = sum(g['home_score'] + g['away_score'] for g in completed_game_list)
                avg_points_per_game = total_points / completed_games
                
                # Find highest scoring game
                highest_scoring = max(completed_game_list, key=lambda x: x['home_score'] + x['away_score'])
                highest_total = highest_scoring['home_score'] + highest_scoring['away_score']
            else:
                avg_points_per_game = 0
                highest_total = 0
            
            return {
                'total_games': total_games,
                'completed_games': completed_games,
                'scheduled_games': scheduled_games,
                'completion_percentage': (completed_games / total_games * 100) if total_games > 0 else 0,
                'avg_points_per_game': round(avg_points_per_game, 1),
                'highest_scoring_game_total': highest_total
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get game summary stats for season {season_id}: {str(e)}")
            return {
                'total_games': 0,
                'completed_games': 0,
                'scheduled_games': 0,
                'completion_percentage': 0,
                'avg_points_per_game': 0,
                'highest_scoring_game_total': 0
            }