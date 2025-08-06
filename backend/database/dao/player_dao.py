"""
Player Data Access Object for the Football Simulation application.

Handles all database operations related to players, including roster management,
statistics tracking, and team associations.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from sqlalchemy import select, and_, or_
from .base import BaseDAO, DAOError
from ..schema import players_table


class PlayerDAO(BaseDAO):
    """Data Access Object for Player entities."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager, players_table)
    
    def get_by_team_id(self, team_id: Union[str, UUID], 
                      limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all players for a specific team.
        
        Args:
            team_id: Team ID
            limit: Optional limit on results
            
        Returns:
            List of player dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).where(self.table.c.team_id == team_id)
                
                if limit:
                    query = query.limit(limit)
                
                query = query.order_by(self.table.c.jersey_number)
                result = conn.execute(query)
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get players for team {team_id}: {str(e)}")
            raise DAOError(f"Failed to get players for team: {str(e)}")
    
    def get_by_position(self, position: str, team_id: Union[str, UUID] | None = None) -> List[Dict[str, Any]]:
        """
        Get players by position, optionally filtered by team.
        
        Args:
            position: Player position (e.g., 'QB', 'RB', etc.)
            team_id: Optional team ID filter
            
        Returns:
            List of player dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                conditions = [self.table.c.position == position]
                
                if team_id:
                    conditions.append(self.table.c.team_id == team_id)
                
                query = select(self.table).where(and_(*conditions)).order_by(self.table.c.name)
                result = conn.execute(query)
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get players by position {position}: {str(e)}")
            raise DAOError(f"Failed to get players by position: {str(e)}")
    
    def get_available_players(self, team_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        Get all available (non-injured) players for a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of available player dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).where(and_(
                    self.table.c.team_id == team_id,
                    self.table.c.injury_status == False
                )).order_by(self.table.c.jersey_number)
                
                result = conn.execute(query)
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get available players for team {team_id}: {str(e)}")
            raise DAOError(f"Failed to get available players: {str(e)}")
    
    def get_injured_players(self, team_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        Get all injured players for a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of injured player dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).where(and_(
                    self.table.c.team_id == team_id,
                    self.table.c.injury_status == True
                )).order_by(self.table.c.jersey_number)
                
                result = conn.execute(query)
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get injured players for team {team_id}: {str(e)}")
            raise DAOError(f"Failed to get injured players: {str(e)}")
    
    def create_player(self, team_id: Union[str, UUID], name: str, position: str,
                     jersey_number: int, age: int = 25, years_pro: int = 2,
                     player_stats: Dict[str, Any] | None = None) -> str:
        """
        Create a new player.
        
        Args:
            team_id: Team ID
            name: Player name
            position: Player position
            jersey_number: Jersey number (1-99)
            age: Player age
            years_pro: Years of professional experience
            player_stats: Player statistics dictionary
            
        Returns:
            Player ID
        """
        player_data = {
            'team_id': team_id,
            'name': name,
            'position': position,
            'jersey_number': jersey_number,
            'age': age,
            'years_pro': years_pro,
            'player_stats': player_stats or {},
            'injury_status': False
        }
        
        return self.create(player_data)
    
    def update_player_stats(self, player_id: Union[str, UUID], 
                           stats: Dict[str, Any]) -> bool:
        """
        Update player statistics.
        
        Args:
            player_id: Player ID
            stats: Dictionary of player statistics
            
        Returns:
            True if stats were updated, False if player not found
        """
        return self.update_by_id(player_id, {'player_stats': stats})
    
    def set_injury_status(self, player_id: Union[str, UUID], 
                         is_injured: bool) -> bool:
        """
        Set player injury status.
        
        Args:
            player_id: Player ID
            is_injured: True if player is injured, False if healthy
            
        Returns:
            True if status was updated, False if player not found
        """
        return self.update_by_id(player_id, {'injury_status': is_injured})
    
    def transfer_player(self, player_id: Union[str, UUID], 
                       new_team_id: Union[str, UUID]) -> bool:
        """
        Transfer a player to a different team.
        
        Args:
            player_id: Player ID
            new_team_id: New team ID
            
        Returns:
            True if player was transferred, False if player not found
        """
        return self.update_by_id(player_id, {'team_id': new_team_id})
    
    def check_jersey_number_available(self, team_id: Union[str, UUID], 
                                    jersey_number: int,
                                    exclude_player_id: Union[str, UUID] | None = None) -> bool:
        """
        Check if a jersey number is available on a team.
        
        Args:
            team_id: Team ID
            jersey_number: Jersey number to check
            exclude_player_id: Optional player ID to exclude (for updates)
            
        Returns:
            True if jersey number is available, False otherwise
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                conditions = [
                    self.table.c.team_id == team_id,
                    self.table.c.jersey_number == jersey_number
                ]
                
                if exclude_player_id:
                    conditions.append(self.table.c.id != exclude_player_id)
                
                query = select([self.table.c.id]).where(and_(*conditions))
                result = conn.execute(query)
                return result.fetchone() is None
        except Exception as e:
            self.logger.error(f"Failed to check jersey number availability: {str(e)}")
            return False
    
    def get_team_roster_by_position_group(self, team_id: Union[str, UUID]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get team roster organized by position group.
        
        Args:
            team_id: Team ID
            
        Returns:
            Dictionary with position groups as keys and player lists as values
        """
        try:
            players = self.get_by_team_id(team_id)
            
            # Position group mapping
            position_groups = {
                'Offense': ['QB', 'RB', 'WR', 'TE', 'OL'],
                'Defense': ['DL', 'LB', 'CB', 'S'],
                'Special Teams': ['K', 'P']
            }
            
            roster_by_group = {group: [] for group in position_groups}
            
            for player in players:
                position = player['position']
                for group, positions in position_groups.items():
                    if position in positions:
                        roster_by_group[group].append(player)
                        break
            
            return roster_by_group
        except Exception as e:
            self.logger.error(f"Failed to get roster by position group for team {team_id}: {str(e)}")
            raise DAOError(f"Failed to get roster by position group: {str(e)}")
    
    def search_players(self, search_term: str, team_id: Union[str, UUID] | None = None) -> List[Dict[str, Any]]:
        """
        Search players by name or position.
        
        Args:
            search_term: Term to search for
            team_id: Optional team ID filter
            
        Returns:
            List of matching player dictionaries
        """
        try:
            search_pattern = f"%{search_term}%"
            
            conditions = [or_(
                self.table.c.name.ilike(search_pattern),
                self.table.c.position.ilike(search_pattern)
            )]
            
            if team_id:
                conditions.append(self.table.c.team_id == team_id)
            
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).where(and_(*conditions)).order_by(self.table.c.name)
                result = conn.execute(query)
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to search players with term '{search_term}': {str(e)}")
            raise DAOError(f"Failed to search players: {str(e)}")
    
    def get_top_players_by_rating(self, position: str | None = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top players by overall rating.
        
        Args:
            position: Optional position filter
            limit: Number of players to return
            
        Returns:
            List of top-rated player dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                # Note: This uses JSONB operator to extract overall_rating
                # In SQLAlchemy Core, we need to use raw SQL for JSONB operations
                base_query = """
                    SELECT * FROM players 
                    WHERE (player_stats->>'overall_rating')::int IS NOT NULL
                """
                
                if position:
                    base_query += f" AND position = '{position}'"
                
                base_query += """
                    ORDER BY (player_stats->>'overall_rating')::int DESC
                    LIMIT :limit
                """
                
                from sqlalchemy import text
                result = conn.execute(text(base_query), {'limit': limit})
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get top players by rating: {str(e)}")
            raise DAOError(f"Failed to get top players by rating: {str(e)}")
    
    def get_player_stats_summary(self, team_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Get summary statistics for a team's players.
        
        Args:
            team_id: Team ID
            
        Returns:
            Dictionary with player statistics summary
        """
        try:
            players = self.get_by_team_id(team_id)
            
            if not players:
                return {
                    'total_players': 0,
                    'available_players': 0,
                    'injured_players': 0,
                    'average_age': 0,
                    'position_breakdown': {}
                }
            
            # Calculate summary statistics
            total_players = len(players)
            available_players = len([p for p in players if not p['injury_status']])
            injured_players = total_players - available_players
            average_age = sum(p['age'] for p in players) / total_players if players else 0
            
            # Position breakdown
            position_breakdown = {}
            for player in players:
                position = player['position']
                position_breakdown[position] = position_breakdown.get(position, 0) + 1
            
            return {
                'total_players': total_players,
                'available_players': available_players,
                'injured_players': injured_players,
                'average_age': round(average_age, 1),
                'position_breakdown': position_breakdown
            }
        except Exception as e:
            self.logger.error(f"Failed to get player stats summary for team {team_id}: {str(e)}")
            raise DAOError(f"Failed to get player stats summary: {str(e)}")
    
    def delete_by_team_id(self, team_id: Union[str, UUID]) -> int:
        """
        Delete all players for a specific team.
        
        Args:
            team_id: Team ID
            
        Returns:
            Number of players deleted
        """
        try:
            with self.db_manager.get_db_transaction() as conn:
                from sqlalchemy import delete
                result = conn.execute(
                    delete(self.table).where(self.table.c.team_id == team_id)
                )
                deleted_count = result.rowcount
                if deleted_count > 0:
                    self.logger.debug(f"Deleted {deleted_count} players for team {team_id}")
                return deleted_count
        except Exception as e:
            self.logger.error(f"Failed to delete players for team {team_id}: {str(e)}")
            raise DAOError(f"Failed to delete players for team: {str(e)}")