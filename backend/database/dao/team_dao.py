"""
Team Data Access Object for the Football Simulation application.

Handles all database operations related to NFL teams, including team information,
statistics, and roster management.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from sqlalchemy import select, and_, or_
from .base import BaseDAO, DAOError
from ..schema import teams_table


class TeamDAO(BaseDAO):
    """Data Access Object for Team entities."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager, teams_table)
    
    def get_by_abbreviation(self, abbreviation: str) -> Optional[Dict[str, Any]]:
        """
        Get team by abbreviation (e.g., 'KC', 'BUF').
        
        Args:
            abbreviation: Team abbreviation
            
        Returns:
            Team dictionary or None if not found
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select(self.table).where(self.table.c.abbreviation == abbreviation)
                )
                row = result.fetchone()
                return self._row_to_dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get team by abbreviation {abbreviation}: {str(e)}")
            raise DAOError(f"Failed to get team by abbreviation: {str(e)}")
    
    def get_by_conference(self, conference: str) -> List[Dict[str, Any]]:
        """
        Get all teams in a conference.
        
        Args:
            conference: Conference name ('AFC' or 'NFC')
            
        Returns:
            List of team dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select(self.table)
                    .where(self.table.c.conference == conference)
                    .order_by(self.table.c.division, self.table.c.name)
                )
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get teams by conference {conference}: {str(e)}")
            raise DAOError(f"Failed to get teams by conference: {str(e)}")
    
    def get_by_division(self, conference: str, division: str) -> List[Dict[str, Any]]:
        """
        Get all teams in a specific division.
        
        Args:
            conference: Conference name ('AFC' or 'NFC')
            division: Division name ('East', 'West', 'North', 'South')
            
        Returns:
            List of team dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select(self.table)
                    .where(and_(
                        self.table.c.conference == conference,
                        self.table.c.division == division
                    ))
                    .order_by(self.table.c.name)
                )
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get teams by division {conference} {division}: {str(e)}")
            raise DAOError(f"Failed to get teams by division: {str(e)}")
    
    def get_all_organized(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Get all teams organized by conference and division.
        
        Returns:
            Dictionary structured as: {conference: {division: [teams]}}
        """
        try:
            all_teams = self.get_all()
            organized = {'AFC': {}, 'NFC': {}}
            
            for team in all_teams:
                conference = team['conference']
                division = team['division']
                
                if division not in organized[conference]:
                    organized[conference][division] = []
                
                organized[conference][division].append(team)
            
            # Sort teams within each division
            for conference in organized:
                for division in organized[conference]:
                    organized[conference][division].sort(key=lambda x: x['name'])
            
            return organized
        except Exception as e:
            self.logger.error(f"Failed to get organized teams: {str(e)}")
            raise DAOError(f"Failed to get organized teams: {str(e)}")
    
    def update_team_stats(self, team_id: Union[str, UUID], stats: Dict[str, Any]) -> bool:
        """
        Update team statistics.
        
        Args:
            team_id: Team ID
            stats: Dictionary of team statistics
            
        Returns:
            True if stats were updated, False if team not found
        """
        return self.update_by_id(team_id, {'team_stats': stats})
    
    def search_teams(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search teams by name, city, or abbreviation.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching team dictionaries
        """
        try:
            search_pattern = f"%{search_term}%"
            
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select(self.table)
                    .where(or_(
                        self.table.c.name.ilike(search_pattern),
                        self.table.c.city.ilike(search_pattern),
                        self.table.c.abbreviation.ilike(search_pattern)
                    ))
                    .order_by(self.table.c.name)
                )
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to search teams with term '{search_term}': {str(e)}")
            raise DAOError(f"Failed to search teams: {str(e)}")
    
    def get_team_full_name(self, team_id: Union[str, UUID]) -> Optional[str]:
        """
        Get the full team name (city + name).
        
        Args:
            team_id: Team ID
            
        Returns:
            Full team name or None if not found
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select([self.table.c.city, self.table.c.name])
                    .where(self.table.c.id == team_id)
                )
                row = result.fetchone()
                if row:
                    return f"{row[0]} {row[1]}"
                return None
        except Exception as e:
            self.logger.error(f"Failed to get full name for team {team_id}: {str(e)}")
            return None
    
    def get_teams_by_abbreviations(self, abbreviations: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple teams by their abbreviations.
        
        Args:
            abbreviations: List of team abbreviations
            
        Returns:
            List of team dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select(self.table)
                    .where(self.table.c.abbreviation.in_(abbreviations))
                    .order_by(self.table.c.name)
                )
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get teams by abbreviations: {str(e)}")
            raise DAOError(f"Failed to get teams by abbreviations: {str(e)}")
    
    def create_team(self, name: str, city: str, abbreviation: str, 
                   conference: str, division: str, team_stats: Dict[str, Any] | None = None) -> str:
        """
        Create a new team.
        
        Args:
            name: Team name
            city: Team city
            abbreviation: Team abbreviation
            conference: Conference ('AFC' or 'NFC')
            division: Division ('East', 'West', 'North', 'South')
            team_stats: Optional team statistics
            
        Returns:
            Team ID
        """
        team_data = {
            'name': name,
            'city': city,
            'abbreviation': abbreviation,
            'conference': conference,
            'division': division,
            'team_stats': team_stats or {}
        }
        
        return self.create(team_data)
    
    def abbreviation_exists(self, abbreviation: str, exclude_id: Union[str, UUID] | None = None) -> bool:
        """
        Check if team abbreviation already exists.
        
        Args:
            abbreviation: Abbreviation to check
            exclude_id: Optional team ID to exclude from check (for updates)
            
        Returns:
            True if abbreviation exists, False otherwise
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select([self.table.c.id]).where(self.table.c.abbreviation == abbreviation)
                
                if exclude_id:
                    query = query.where(self.table.c.id != exclude_id)
                
                result = conn.execute(query)
                return result.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Failed to check abbreviation existence {abbreviation}: {str(e)}")
            return False
    
    def get_division_teams(self, reference_team_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        Get all teams in the same division as the reference team.
        
        Args:
            reference_team_id: ID of the reference team
            
        Returns:
            List of teams in the same division
        """
        try:
            # First get the reference team's conference and division
            reference_team = self.get_by_id(reference_team_id)
            if not reference_team:
                return []
            
            return self.get_by_division(
                reference_team['conference'], 
                reference_team['division']
            )
        except Exception as e:
            self.logger.error(f"Failed to get division teams for {reference_team_id}: {str(e)}")
            raise DAOError(f"Failed to get division teams: {str(e)}")
    
    def get_conference_teams(self, reference_team_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        Get all teams in the same conference as the reference team.
        
        Args:
            reference_team_id: ID of the reference team
            
        Returns:
            List of teams in the same conference
        """
        try:
            reference_team = self.get_by_id(reference_team_id)
            if not reference_team:
                return []
            
            return self.get_by_conference(reference_team['conference'])
        except Exception as e:
            self.logger.error(f"Failed to get conference teams for {reference_team_id}: {str(e)}")
            raise DAOError(f"Failed to get conference teams: {str(e)}")