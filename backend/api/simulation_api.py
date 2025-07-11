"""
Simulation API endpoints for the football simulation engine.

This module provides REST API endpoints for running simulations
and retrieving game results.
"""

from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime

from models.team import Team
from simulation.game_engine import GameEngine, GameResult
from data.team_loader import load_sample_teams

class SimulationAPI:
    """
    API class for handling simulation-related requests.
    
    This class will be integrated with a web framework like Flask or FastAPI
    to provide REST endpoints for the React frontend.
    """
    
    def __init__(self):
        """Initialize the simulation API."""
        self.logger = logging.getLogger(__name__)
        self.game_engine = GameEngine()
        self.simulation_history: List[Dict[str, Any]] = []
    
    def simulate_game(self, home_team_id: str, away_team_id: str, 
                     seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Simulate a game between two teams.
        
        Args:
            home_team_id: Identifier for the home team
            away_team_id: Identifier for the away team
            seed: Optional random seed for reproducible results
            
        Returns:
            Dictionary with simulation results
        """
        try:
            # Load teams (in a real app, this would come from a database)
            teams = load_sample_teams()
            team_lookup = {team.abbreviation: team for team in teams}
            
            if home_team_id not in team_lookup:
                return {"error": f"Home team '{home_team_id}' not found"}
            
            if away_team_id not in team_lookup:
                return {"error": f"Away team '{away_team_id}' not found"}
            
            home_team = team_lookup[home_team_id]
            away_team = team_lookup[away_team_id]
            
            # Set seed if provided
            if seed is not None:
                self.game_engine = GameEngine(seed=seed)
            
            # Run simulation
            result = self.game_engine.simulate_game(home_team, away_team)
            
            # Convert result to API response format
            response = self._format_game_result(result)
            
            # Store in history
            self.simulation_history.append({
                "timestamp": datetime.now().isoformat(),
                "simulation": response,
                "seed": seed
            })
            
            self.logger.info(f"Simulation completed: {response['summary']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Simulation error: {str(e)}")
            return {"error": f"Simulation failed: {str(e)}"}
    
    def get_simulation_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent simulation history.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            Dictionary with simulation history
        """
        return {
            "history": self.simulation_history[-limit:],
            "total_simulations": len(self.simulation_history)
        }
    
    def simulate_season(self, team_ids: List[str], games_per_team: int = 16) -> Dict[str, Any]:
        """
        Simulate a season with multiple games.
        
        Args:
            team_ids: List of team identifiers
            games_per_team: Number of games each team should play
            
        Returns:
            Dictionary with season results
        """
        try:
            teams = load_sample_teams()
            team_lookup = {team.abbreviation: team for team in teams}
            
            # Validate team IDs
            valid_teams = []
            for team_id in team_ids:
                if team_id in team_lookup:
                    valid_teams.append(team_lookup[team_id])
                else:
                    return {"error": f"Team '{team_id}' not found"}
            
            if len(valid_teams) < 2:
                return {"error": "Need at least 2 teams for a season"}
            
            # Generate season schedule (simplified round-robin)
            season_results = []
            
            for i, home_team in enumerate(valid_teams):
                for j, away_team in enumerate(valid_teams):
                    if i != j:  # Teams don't play themselves
                        result = self.game_engine.simulate_game(home_team, away_team)
                        season_results.append(self._format_game_result(result))
            
            # Calculate standings
            standings = self._calculate_standings(valid_teams)
            
            return {
                "season_results": season_results,
                "standings": standings,
                "total_games": len(season_results)
            }
            
        except Exception as e:
            self.logger.error(f"Season simulation error: {str(e)}")
            return {"error": f"Season simulation failed: {str(e)}"}
    
    def _format_game_result(self, result: GameResult) -> Dict[str, Any]:
        """Format a GameResult for API response."""
        return {
            "home_team": {
                "name": result.home_team.full_name,
                "abbreviation": result.home_team.abbreviation,
                "score": result.home_score
            },
            "away_team": {
                "name": result.away_team.full_name,
                "abbreviation": result.away_team.abbreviation,
                "score": result.away_score
            },
            "winner": {
                "name": result.winner.full_name if result.winner else None,
                "abbreviation": result.winner.abbreviation if result.winner else None
            } if result.winner else None,
            "duration_minutes": result.duration,
            "summary": f"{result.away_team.name} {result.away_score} - {result.home_team.name} {result.home_score}"
        }
    
    def _calculate_standings(self, teams: List[Team]) -> List[Dict[str, Any]]:
        """Calculate team standings based on current records."""
        standings_data = []
        
        for team in teams:
            standings_data.append({
                "team": {
                    "name": team.full_name,
                    "abbreviation": team.abbreviation
                },
                "wins": team.wins,
                "losses": team.losses,
                "ties": team.ties,
                "win_percentage": round(team.win_percentage, 3),
                "record": team.record
            })
        
        # Sort by win percentage (descending)
        standings_data.sort(key=lambda x: x["win_percentage"], reverse=True)
        
        return standings_data
