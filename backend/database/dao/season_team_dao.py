"""
Season Team Data Access Object for the Football Simulation application.

Handles all database operations related to teams associated with user seasons,
including team assignments, standings, and season-specific team data.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from sqlalchemy import select, and_, or_, desc, func
from .base import BaseDAO, DAOError
from ..schema import season_teams_table


class SeasonTeamDAO(BaseDAO):
    """Data Access Object for Season Team associations."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager, season_teams_table)
    
    def add_team_to_season(self, season_id: Union[str, UUID], team_id: Union[str, UUID],
                          custom_name: Optional[str] = None) -> str:
        """
        Add a team to a season.
        
        Args:
            season_id: Season ID
            team_id: Team ID
            custom_name: Optional custom team name for this season
            
        Returns:
            Season team association ID
        """
        season_team_data = {
            'season_id': season_id,
            'team_id': team_id,
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'points_for': 0,
            'points_against': 0,
            'division_wins': 0,
            'conference_wins': 0,
            'season_stats': {}
        }
        
        return self.create(season_team_data)
    
    def get_season_teams(self, season_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        Get all teams in a season with their records.
        
        Args:
            season_id: Season ID
            
        Returns:
            List of season team dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                # Join with teams table to get team information
                from ..schema import teams_table
                query = select(
                    self.table.c.id,
                    self.table.c.season_id,
                    self.table.c.team_id,
                    self.table.c.wins,
                    self.table.c.losses,
                    self.table.c.ties,
                    self.table.c.points_for,
                    self.table.c.points_against,
                    self.table.c.division_wins,
                    self.table.c.conference_wins,
                    self.table.c.season_stats,
                    teams_table.c.name.label('team_name'),
                    teams_table.c.city.label('team_city'),
                    teams_table.c.abbreviation.label('team_abbreviation'),
                    teams_table.c.conference.label('team_conference'),
                    teams_table.c.division.label('team_division')
                ).select_from(
                    self.table.join(teams_table, self.table.c.team_id == teams_table.c.id)
                ).where(self.table.c.season_id == season_id).order_by(
                    desc(self.table.c.wins),
                    desc(self.table.c.points_for - self.table.c.points_against)
                )
                
                result = conn.execute(query)
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get teams for season {season_id}: {str(e)}")
            raise DAOError(f"Failed to get season teams: {str(e)}")
    
    def get_team_in_season(self, season_id: Union[str, UUID], 
                          team_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        Get a specific team's data in a season.
        
        Args:
            season_id: Season ID
            team_id: Team ID
            
        Returns:
            Season team dictionary or None if not found
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select(self.table).where(and_(
                        self.table.c.season_id == season_id,
                        self.table.c.team_id == team_id
                    ))
                )
                row = result.fetchone()
                return self._row_to_dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get team {team_id} in season {season_id}: {str(e)}")
            raise DAOError(f"Failed to get team in season: {str(e)}")
    
    def update_team_record(self, season_id: Union[str, UUID], team_id: Union[str, UUID],
                          wins: int, losses: int, ties: int = 0,
                          points_for: int = 0, points_against: int = 0) -> bool:
        """
        Update a team's record in a season.
        
        Args:
            season_id: Season ID
            team_id: Team ID
            wins: Number of wins
            losses: Number of losses
            ties: Number of ties
            points_for: Points scored
            points_against: Points allowed
            
        Returns:
            True if updated successfully, False if not found
        """
        try:
            with self.db_manager.get_db_transaction() as conn:
                from sqlalchemy import update
                result = conn.execute(
                    update(self.table)
                    .where(and_(
                        self.table.c.season_id == season_id,
                        self.table.c.team_id == team_id
                    ))
                    .values(
                        wins=wins,
                        losses=losses,
                        ties=ties,
                        points_for=points_for,
                        points_against=points_against
                    )
                )
                return result.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update team record for team {team_id}: {str(e)}")
            raise DAOError(f"Failed to update team record: {str(e)}")
    
    def add_game_result(self, season_id: Union[str, UUID], team_id: Union[str, UUID],
                       won: bool, points_for: int, points_against: int,
                       is_division: bool = False, is_conference: bool = False) -> bool:
        """
        Add a game result to a team's season record.
        
        Args:
            season_id: Season ID
            team_id: Team ID
            won: True if team won, False if lost
            points_for: Points scored by this team
            points_against: Points scored by opponent
            is_division: True if this was a division game
            is_conference: True if this was a conference game
            
        Returns:
            True if updated successfully, False if not found
        """
        try:
            team_season = self.get_team_in_season(season_id, team_id)
            if not team_season:
                return False
            
            # Update overall record
            new_wins = team_season['wins'] + (1 if won else 0)
            new_losses = team_season['losses'] + (0 if won else 1)
            new_points_for = team_season['points_for'] + points_for
            new_points_against = team_season['points_against'] + points_against
            
            # Update division record if applicable
            new_division_wins = team_season['division_wins'] + (1 if won and is_division else 0)
            new_division_losses = team_season['division_losses'] + (0 if won or not is_division else 1)
            
            # Update conference record if applicable
            new_conference_wins = team_season['conference_wins'] + (1 if won and is_conference else 0)
            new_conference_losses = team_season['conference_losses'] + (0 if won or not is_conference else 1)
            
            with self.db_manager.get_db_transaction() as conn:
                from sqlalchemy import update
                result = conn.execute(
                    update(self.table)
                    .where(and_(
                        self.table.c.season_id == season_id,
                        self.table.c.team_id == team_id
                    ))
                    .values(
                        wins=new_wins,
                        losses=new_losses,
                        points_for=new_points_for,
                        points_against=new_points_against,
                        division_wins=new_division_wins,
                        conference_wins=new_conference_wins
                    )
                )
                return result.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to add game result for team {team_id}: {str(e)}")
            raise DAOError(f"Failed to add game result: {str(e)}")
    
    def get_standings(self, season_id: Union[str, UUID], 
                     conference: Optional[str] = None,
                     division: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get standings for a season, optionally filtered by conference or division.
        
        Args:
            season_id: Season ID
            conference: Optional conference filter ('AFC' or 'NFC')
            division: Optional division filter ('East', 'West', 'North', 'South')
            
        Returns:
            List of team standings with calculated stats
        """
        try:
            teams = self.get_season_teams(season_id)
            
            # Filter by conference/division if specified
            if conference:
                teams = [t for t in teams if t.get('team_conference') == conference]
            if division and conference:
                teams = [t for t in teams if t.get('team_division') == division]
            
            # Calculate additional stats
            for team in teams:
                games_played = team['wins'] + team['losses'] + team['ties']
                team['games_played'] = games_played
                team['win_percentage'] = (team['wins'] + 0.5 * team['ties']) / games_played if games_played > 0 else 0
                team['point_differential'] = team['points_for'] - team['points_against']
                
                # Division record percentage
                div_games = team['division_wins']
                team['division_win_percentage'] = team['division_wins'] / div_games if div_games > 0 else 0
                
                # Conference record percentage
                conf_games = team['conference_wins']
                team['conference_win_percentage'] = team['conference_wins'] / conf_games if conf_games > 0 else 0
            
            # Sort by wins (desc), then win percentage (desc), then point differential (desc)
            teams.sort(key=lambda x: (x['wins'], x['win_percentage'], x['point_differential']), reverse=True)
            
            return teams
            
        except Exception as e:
            self.logger.error(f"Failed to get standings for season {season_id}: {str(e)}")
            raise DAOError(f"Failed to get standings: {str(e)}")
    
    def bulk_add_teams_to_season(self, season_id: Union[str, UUID], 
                                team_ids: List[Union[str, UUID]]) -> List[str]:
        """
        Add multiple teams to a season in bulk.
        
        Args:
            season_id: Season ID
            team_ids: List of team IDs to add
            
        Returns:
            List of created season team association IDs
        """
        records = []
        for team_id in team_ids:
            records.append({
                'season_id': season_id,
                'team_id': team_id,
                'wins': 0,
                'losses': 0,
                'ties': 0,
                'points_for': 0,
                'points_against': 0,
                'division_wins': 0,
                'conference_wins': 0,
                'season_stats': {}
            })
        
        return self.bulk_insert(records)
    
    def remove_team_from_season(self, season_id: Union[str, UUID], 
                               team_id: Union[str, UUID]) -> bool:
        """
        Remove a team from a season.
        
        Args:
            season_id: Season ID
            team_id: Team ID
            
        Returns:
            True if removed successfully, False if not found
        """
        try:
            with self.db_manager.get_db_transaction() as conn:
                from sqlalchemy import delete
                result = conn.execute(
                    delete(self.table).where(and_(
                        self.table.c.season_id == season_id,
                        self.table.c.team_id == team_id
                    ))
                )
                return result.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to remove team {team_id} from season {season_id}: {str(e)}")
            raise DAOError(f"Failed to remove team from season: {str(e)}")
    
    def reset_season_records(self, season_id: Union[str, UUID]) -> int:
        """
        Reset all team records in a season to 0-0.
        
        Args:
            season_id: Season ID
            
        Returns:
            Number of teams reset
        """
        try:
            with self.db_manager.get_db_transaction() as conn:
                from sqlalchemy import update
                result = conn.execute(
                    update(self.table)
                    .where(self.table.c.season_id == season_id)
                    .values(
                        wins=0,
                        losses=0,
                        ties=0,
                        points_for=0,
                        points_against=0,
                        division_wins=0,
                        conference_wins=0
                    )
                )
                return result.rowcount
        except Exception as e:
            self.logger.error(f"Failed to reset season records for season {season_id}: {str(e)}")
            raise DAOError(f"Failed to reset season records: {str(e)}")