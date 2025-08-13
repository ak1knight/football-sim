"""
Team API endpoints for the football simulation engine.

This module provides REST API endpoints for team data management,
including roster information and team statistics. Now uses database storage.
"""

from typing import Dict, List, Optional, Any
import logging

from database.connection import get_db_manager
from database.dao import TeamDAO, PlayerDAO


class TeamAPI:
    """
    API class for handling team-related requests using database storage.
    
    This class provides endpoints for team data management
    and integrates with the PostgreSQL database.
    """
    
    def __init__(self):
        """Initialize the team API."""
        self.logger = logging.getLogger(__name__)
    
    def get_all_teams(self) -> Dict[str, Any]:
        """
        Get all available teams from database.
        
        Returns:
            Dictionary with all teams and their basic information
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"error": "Database connection not available"}
            
            team_dao = TeamDAO(db_manager)
            teams = team_dao.get_all()
            
            teams_data = []
            for team in teams:
                teams_data.append(self._format_team_summary(team))
            
            return {
                "teams": teams_data,
                "total_teams": len(teams_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error loading teams from database: {str(e)}")
            return {"error": f"Failed to load teams: {str(e)}"}
    
    def get_team_details(self, team_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific team.
        
        Args:
            team_id: Team identifier (ID or abbreviation)
            
        Returns:
            Dictionary with detailed team information
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"error": "Database connection not available"}
            
            team_dao = TeamDAO(db_manager)
            
            # Try to find by ID first, then by abbreviation
            team = team_dao.get_by_id(team_id)
            if not team:
                team = team_dao.get_by_abbreviation(team_id)
            
            if not team:
                return {"error": f"Team '{team_id}' not found"}
            
            return self._format_team_details(team)
            
        except Exception as e:
            self.logger.error(f"Error loading team details: {str(e)}")
            return {"error": f"Failed to load team details: {str(e)}"}
    
    def get_team_roster(self, team_id: str) -> Dict[str, Any]:
        """
        Get the complete roster for a team.
        
        Args:
            team_id: Team identifier (ID or abbreviation)
            
        Returns:
            Dictionary with team roster information
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"error": "Database connection not available"}
            
            team_dao = TeamDAO(db_manager)
            player_dao = PlayerDAO(db_manager)
            
            # Find team
            team = team_dao.get_by_id(team_id)
            if not team:
                team = team_dao.get_by_abbreviation(team_id)
            
            if not team:
                return {"error": f"Team '{team_id}' not found"}
            
            # Get players for this team
            players = player_dao.get_by_team_id(team['id'])
            
            # Group players by position group
            roster_by_position = self._group_players_by_position(players)
            available_players = [p for p in players if not p['injury_status']]
            
            return {
                "team": self._format_team_summary(team),
                "roster": roster_by_position,
                "total_players": len(players),
                "available_players": len(available_players)
            }
            
        except Exception as e:
            self.logger.error(f"Error loading team roster: {str(e)}")
            return {"error": f"Failed to load team roster: {str(e)}"}
    
    def get_team_stats(self, team_id: str) -> Dict[str, Any]:
        """
        Get team statistics and ratings.
        
        Args:
            team_id: Team identifier (ID or abbreviation)
            
        Returns:
            Dictionary with team statistics
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"error": "Database connection not available"}
            
            team_dao = TeamDAO(db_manager)
            
            # Find team
            team = team_dao.get_by_id(team_id)
            if not team:
                team = team_dao.get_by_abbreviation(team_id)
            
            if not team:
                return {"error": f"Team '{team_id}' not found"}
            
            stats = team.get('team_stats', {})
            overall_rating = self._calculate_overall_rating(stats)
            
            return {
                "team": self._format_team_summary(team),
                "overall_rating": overall_rating,
                "offensive_stats": {
                    "overall": stats.get("offensive_rating", 75),
                    "passing": stats.get("passing_offense", 75),
                    "rushing": stats.get("rushing_offense", 75),
                    "red_zone_efficiency": stats.get("red_zone_efficiency", 75)
                },
                "defensive_stats": {
                    "overall": stats.get("defensive_rating", 75),
                    "pass_defense": stats.get("pass_defense", 75),
                    "run_defense": stats.get("run_defense", 75),
                    "red_zone_defense": stats.get("red_zone_defense", 75)
                },
                "special_teams": {
                    "kicking": stats.get("kicking_game", 75),
                    "returns": stats.get("return_game", 75)
                },
                "coaching": {
                    "rating": stats.get("coaching_rating", 75),
                    "discipline": stats.get("discipline", 75),
                    "conditioning": stats.get("conditioning", 75)
                },
                "home_field_advantage": stats.get("home_field_advantage", 1)
            }
            
        except Exception as e:
            self.logger.error(f"Error loading team stats: {str(e)}")
            return {"error": f"Failed to load team stats: {str(e)}"}
    
    def compare_teams(self, team1_id: str, team2_id: str) -> Dict[str, Any]:
        """
        Compare two teams side by side.
        
        Args:
            team1_id: First team identifier
            team2_id: Second team identifier
            
        Returns:
            Dictionary with team comparison data
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"error": "Database connection not available"}
            
            team_dao = TeamDAO(db_manager)
            
            # Find both teams
            team1 = team_dao.get_by_id(team1_id) or team_dao.get_by_abbreviation(team1_id)
            team2 = team_dao.get_by_id(team2_id) or team_dao.get_by_abbreviation(team2_id)
            
            if not team1:
                return {"error": f"Team '{team1_id}' not found"}
            
            if not team2:
                return {"error": f"Team '{team2_id}' not found"}
            
            team1_overall = self._calculate_overall_rating(team1.get('team_stats', {}))
            team2_overall = self._calculate_overall_rating(team2.get('team_stats', {}))
            
            team1_offense = team1.get('team_stats', {}).get('offensive_rating', 75)
            team2_offense = team2.get('team_stats', {}).get('offensive_rating', 75)
            
            team1_defense = team1.get('team_stats', {}).get('defensive_rating', 75)
            team2_defense = team2.get('team_stats', {}).get('defensive_rating', 75)
            
            return {
                "team1": self._format_team_details(team1),
                "team2": self._format_team_details(team2),
                "comparison": {
                    "overall_rating": {
                        "team1": team1_overall,
                        "team2": team2_overall,
                        "advantage": team1['abbreviation'] if team1_overall > team2_overall else team2['abbreviation']
                    },
                    "offense": {
                        "team1": team1_offense,
                        "team2": team2_offense,
                        "advantage": team1['abbreviation'] if team1_offense > team2_offense else team2['abbreviation']
                    },
                    "defense": {
                        "team1": team1_defense,
                        "team2": team2_defense,
                        "advantage": team1['abbreviation'] if team1_defense > team2_defense else team2['abbreviation']
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing teams: {str(e)}")
            return {"error": f"Failed to compare teams: {str(e)}"}
    
    def _format_team_summary(self, team: Dict[str, Any]) -> Dict[str, Any]:
        """Format a team for API response (summary version)."""
        stats = team.get('team_stats', {})
        overall_rating = self._calculate_overall_rating(stats)
        
        return {
            "id": team['abbreviation'],
            "name": team['name'],
            "full_name": f"{team['city']} {team['name']}",
            "city": team['city'],
            "abbreviation": team['abbreviation'],
            "conference": team['conference'],
            "division": team['division'],
            "overall_rating": overall_rating
        }
    
    def _format_team_details(self, team: Dict[str, Any]) -> Dict[str, Any]:
        """Format a team for API response (detailed version)."""
        summary = self._format_team_summary(team)
        stats = team.get('team_stats', {})
        
        summary.update({
            "stats": {
                "offensive_rating": stats.get("offensive_rating", 75),
                "defensive_rating": stats.get("defensive_rating", 75),
                "coaching_rating": stats.get("coaching_rating", 75)
            }
        })
        return summary
    
    def _format_player(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Format a player for API response."""
        stats = player.get('player_stats', {})
        
        return {
            "id": player['id'],
            "name": player['name'],
            "jersey_number": player['jersey_number'],
            "position": player['position'],
            "position_group": self._get_position_group(player['position']),
            "age": player['age'],
            "years_pro": player['years_pro'],
            "overall_rating": stats.get("overall_rating", 70),
            "injury_status": player['injury_status'],
            "available": not player['injury_status']
        }
    
    def _group_players_by_position(self, players: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group players by position group."""
        roster_by_position = {}
        
        for player in players:
            position_group = self._get_position_group(player['position'])
            if position_group not in roster_by_position:
                roster_by_position[position_group] = []
            
            roster_by_position[position_group].append(self._format_player(player))
        
        return roster_by_position
    
    def _get_position_group(self, position: str) -> str:
        """Get position group for a position."""
        offense_positions = ['QB', 'RB', 'WR', 'TE', 'OL']
        defense_positions = ['DL', 'LB', 'CB', 'S']
        special_teams_positions = ['K', 'P']
        
        if position in offense_positions:
            return 'Offense'
        elif position in defense_positions:
            return 'Defense'
        elif position in special_teams_positions:
            return 'Special Teams'
        else:
            return 'Other'
    
    def _calculate_overall_rating(self, stats: Dict[str, Any]) -> int:
        """Calculate overall team rating from individual stats."""
        if not stats:
            return 75  # Default rating
        
        # Weight the different aspects of team performance
        offense_weight = 0.4
        defense_weight = 0.4
        coaching_weight = 0.2
        
        offensive_rating = stats.get("offensive_rating", 75)
        defensive_rating = stats.get("defensive_rating", 75)
        coaching_rating = stats.get("coaching_rating", 75)
        
        overall = (offensive_rating * offense_weight + 
                  defensive_rating * defense_weight + 
                  coaching_rating * coaching_weight)
        
        return int(round(overall))
