"""
Team API endpoints for the football simulation engine.

This module provides REST API endpoints for team data management,
including roster information and team statistics.
"""

from typing import Dict, List, Optional, Any
import logging

from models.team import Team
from models.player import Player, Position
from data.team_loader import load_sample_teams

class TeamAPI:
    """
    API class for handling team-related requests.
    
    This class provides endpoints for team data management
    and will be integrated with a web framework.
    """
    
    def __init__(self):
        """Initialize the team API."""
        self.logger = logging.getLogger(__name__)
    
    def get_all_teams(self) -> Dict[str, Any]:
        """
        Get all available teams.
        
        Returns:
            Dictionary with all teams and their basic information
        """
        try:
            teams = load_sample_teams()
            teams_data = []
            
            for team in teams:
                teams_data.append(self._format_team_summary(team))
            
            return {
                "teams": teams_data,
                "total_teams": len(teams_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error loading teams: {str(e)}")
            return {"error": f"Failed to load teams: {str(e)}"}
    
    def get_team_details(self, team_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific team.
        
        Args:
            team_id: Team identifier (abbreviation)
            
        Returns:
            Dictionary with detailed team information
        """
        try:
            teams = load_sample_teams()
            team_lookup = {team.abbreviation: team for team in teams}
            
            if team_id not in team_lookup:
                return {"error": f"Team '{team_id}' not found"}
            
            team = team_lookup[team_id]
            return self._format_team_details(team)
            
        except Exception as e:
            self.logger.error(f"Error loading team details: {str(e)}")
            return {"error": f"Failed to load team details: {str(e)}"}
    
    def get_team_roster(self, team_id: str) -> Dict[str, Any]:
        """
        Get the complete roster for a team.
        
        Args:
            team_id: Team identifier (abbreviation)
            
        Returns:
            Dictionary with team roster information
        """
        try:
            teams = load_sample_teams()
            team_lookup = {team.abbreviation: team for team in teams}
            
            if team_id not in team_lookup:
                return {"error": f"Team '{team_id}' not found"}
            
            team = team_lookup[team_id]
            
            # Group players by position
            roster_by_position = {}
            for player in team.players:
                position_group = player.get_position_group()
                if position_group not in roster_by_position:
                    roster_by_position[position_group] = []
                
                roster_by_position[position_group].append(self._format_player(player))
            
            return {
                "team": self._format_team_summary(team),
                "roster": roster_by_position,
                "total_players": len(team.players),
                "available_players": len(team.get_available_players())
            }
            
        except Exception as e:
            self.logger.error(f"Error loading team roster: {str(e)}")
            return {"error": f"Failed to load team roster: {str(e)}"}
    
    def get_team_stats(self, team_id: str) -> Dict[str, Any]:
        """
        Get team statistics and ratings.
        
        Args:
            team_id: Team identifier (abbreviation)
            
        Returns:
            Dictionary with team statistics
        """
        try:
            teams = load_sample_teams()
            team_lookup = {team.abbreviation: team for team in teams}
            
            if team_id not in team_lookup:
                return {"error": f"Team '{team_id}' not found"}
            
            team = team_lookup[team_id]
            
            return {
                "team": self._format_team_summary(team),
                "overall_rating": team.get_team_overall_rating(),
                "offensive_stats": {
                    "overall": team.stats.offensive_rating,
                    "passing": team.stats.passing_offense,
                    "rushing": team.stats.rushing_offense,
                    "red_zone_efficiency": team.stats.red_zone_efficiency
                },
                "defensive_stats": {
                    "overall": team.stats.defensive_rating,
                    "pass_defense": team.stats.pass_defense,
                    "run_defense": team.stats.run_defense,
                    "red_zone_defense": team.stats.red_zone_defense
                },
                "special_teams": {
                    "kicking": team.stats.kicking_game,
                    "returns": team.stats.return_game
                },
                "coaching": {
                    "rating": team.stats.coaching_rating,
                    "discipline": team.stats.discipline,
                    "conditioning": team.stats.conditioning
                },
                "home_field_advantage": team.stats.home_field_advantage
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
            teams = load_sample_teams()
            team_lookup = {team.abbreviation: team for team in teams}
            
            if team1_id not in team_lookup:
                return {"error": f"Team '{team1_id}' not found"}
            
            if team2_id not in team_lookup:
                return {"error": f"Team '{team2_id}' not found"}
            
            team1 = team_lookup[team1_id]
            team2 = team_lookup[team2_id]
            
            return {
                "team1": self._format_team_details(team1),
                "team2": self._format_team_details(team2),
                "comparison": {
                    "overall_rating": {
                        "team1": team1.get_team_overall_rating(),
                        "team2": team2.get_team_overall_rating(),
                        "advantage": team1_id if team1.get_team_overall_rating() > team2.get_team_overall_rating() else team2_id
                    },
                    "offense": {
                        "team1": team1.stats.offensive_rating,
                        "team2": team2.stats.offensive_rating,
                        "advantage": team1_id if team1.stats.offensive_rating > team2.stats.offensive_rating else team2_id
                    },
                    "defense": {
                        "team1": team1.stats.defensive_rating,
                        "team2": team2.stats.defensive_rating,
                        "advantage": team1_id if team1.stats.defensive_rating > team2.stats.defensive_rating else team2_id
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing teams: {str(e)}")
            return {"error": f"Failed to compare teams: {str(e)}"}
    
    def _format_team_summary(self, team: Team) -> Dict[str, Any]:
        """Format a team for API response (summary version)."""
        return {
            "id": team.abbreviation,
            "name": team.name,
            "full_name": team.full_name,
            "city": team.city,
            "abbreviation": team.abbreviation,
            "conference": team.conference,
            "division": team.division,
            "record": team.record,
            "win_percentage": round(team.win_percentage, 3),
            "overall_rating": team.get_team_overall_rating()
        }
    
    def _format_team_details(self, team: Team) -> Dict[str, Any]:
        """Format a team for API response (detailed version)."""
        summary = self._format_team_summary(team)
        summary.update({
            "roster_size": len(team.players),
            "available_players": len(team.get_available_players()),
            "stats": {
                "offensive_rating": team.stats.offensive_rating,
                "defensive_rating": team.stats.defensive_rating,
                "coaching_rating": team.stats.coaching_rating
            }
        })
        return summary
    
    def _format_player(self, player: Player) -> Dict[str, Any]:
        """Format a player for API response."""
        return {
            "name": player.name,
            "jersey_number": player.jersey_number,
            "position": player.position.value,
            "position_group": player.get_position_group(),
            "age": player.age,
            "years_pro": player.years_pro,
            "overall_rating": player.stats.overall_rating,
            "injury_status": player.injury_status,
            "available": player.is_available()
        }
