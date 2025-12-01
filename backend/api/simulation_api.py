"""
Simulation API endpoints for the football simulation engine.

This module provides REST API endpoints for running simulations
and retrieving game results, now using database persistence.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from database.connection import get_db_manager
from database.dao import TeamDAO, SeasonGameDAO
from models.team import Team
from simulation.game_engine import GameEngine, GameResult
from simulation.schedule_generators import NFLScheduleGenerator
from simulation.season_engine import SeasonEngine

class SimulationAPI:
    """
    API class for handling simulation-related requests with database persistence.
    """

    def __init__(self):
        """Initialize the simulation API."""
        self.logger = logging.getLogger(__name__)
        self.game_engine = GameEngine()

    def simulate_game(self, home_team_id: str, away_team_id: str, seed: Optional[int] = None, season_id: Optional[str] = None, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Simulate a game between two teams and persist the result.

        Args:
            home_team_id: Identifier for the home team
            away_team_id: Identifier for the away team
            seed: Optional random seed for reproducible results
            season_id: Optional season ID to associate the game with
            week: Optional week number for the game

        Returns:
            Dictionary with simulation results
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"error": "Database connection not available"}

            team_dao = TeamDAO(db_manager)
            season_game_dao = SeasonGameDAO(db_manager)

            # Fetch teams from the database
            home_team_data = team_dao.get_by_id(home_team_id) or team_dao.get_by_abbreviation(home_team_id)
            away_team_data = team_dao.get_by_id(away_team_id) or team_dao.get_by_abbreviation(away_team_id)

            if not home_team_data:
                return {"error": f"Home team '{home_team_id}' not found"}
            if not away_team_data:
                return {"error": f"Away team '{away_team_id}' not found"}

            # Convert to Team model if needed
            home_team = Team(**home_team_data)
            away_team = Team(**away_team_data)

            # Set seed if provided
            if seed is not None:
                self.game_engine = GameEngine(seed=seed)

            # Run simulation
            result = self.game_engine.simulate_game(home_team, away_team)

            # Persist result if season_id and week are provided
            game_id = None
            if season_id and week:
                game_id = season_game_dao.create_game(
                    season_id=season_id,
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    week=week,
                    
                )
                # Update result in DB
                season_game_dao.update_game_result(
                    game_id=game_id,
                    home_score=result.home_score,
                    away_score=result.away_score,
                    game_stats={
                        "home_score": result.home_score,
                        "away_score": result.away_score,
                        "duration": getattr(result, "duration", None),
                        "winner": getattr(result.winner, "abbreviation", None) if result.winner else None
                    }
                )

            response = self._format_game_result(result)
            response["game_id"] = game_id

            self.logger.info(f"Simulation completed: {response['summary']}")
            return response

        except Exception as e:
            self.logger.error(f"Simulation error: {str(e)}")
            return {"error": f"Simulation failed: {str(e)}"}

    def get_simulation_history(self, season_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent simulation history from the database.

        Args:
            season_id: Optional season ID to filter results
            limit: Maximum number of results to return

        Returns:
            Dictionary with simulation history
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"error": "Database connection not available"}

            season_game_dao = SeasonGameDAO(db_manager)
            if season_id:
                games = season_game_dao.get_completed_games(season_id, limit=limit)
            else:
                # If no season_id, return empty or implement global history if needed
                games = []

            history = []
            for game in games:
                history.append({
                    "game_id": game.get("id"),
                    "season_id": game.get("season_id"),
                    "week": game.get("week"),
                    "home_team": {
                        "id": game.get("home_team_id"),
                        "name": f"{game.get('home_team_city', '')} {game.get('home_team_name', '')}".strip(),
                        "abbreviation": game.get("home_team_abbr")
                    },
                    "away_team": {
                        "id": game.get("away_team_id"),
                        "name": f"{game.get('away_team_city', '')} {game.get('away_team_name', '')}".strip(),
                        "abbreviation": game.get("away_team_abbr")
                    },
                    "home_score": game.get("home_score"),
                    "away_score": game.get("away_score"),
                    "completed_at": game.get("completed_at"),
                    "game_stats": game.get("game_stats", {})
                })

            return {
                "history": history,
                "total_simulations": len(history)
            }
        except Exception as e:
            self.logger.error(f"Failed to get simulation history: {str(e)}")
            return {"error": f"Failed to get simulation history: {str(e)}"}

    def simulate_season(self, team_ids: List[str], games_per_team: int = 16, season_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate a season with multiple games and persist results.

        Args:
            team_ids: List of team identifiers
            games_per_team: Number of games each team should play
            season_id: Optional season ID to associate games with

        Returns:
            Dictionary with season results
        """
        try:
            db_manager = get_db_manager()
            if not db_manager:
                return {"error": "Database connection not available"}

            team_dao = TeamDAO(db_manager)
            season_game_dao = SeasonGameDAO(db_manager)

            # Fetch teams from the database
            teams_data = team_dao.get_teams_by_abbreviations(team_ids)
            team_lookup = {team['abbreviation']: self._to_team_model(team) for team in teams_data}
            team_id_lookup = {team['abbreviation']: team.get('id') for team in teams_data}

            # Validate team IDs
            valid_teams = []
            for team_id in team_ids:
                if team_id in team_lookup:
                    valid_teams.append(team_lookup[team_id])
                else:
                    return {"error": f"Team '{team_id}' not found"}

            if len(valid_teams) < 2:
                return {"error": "Need at least 2 teams for a season"}

            engine = SeasonEngine(
                teams=valid_teams,
                season_year=datetime.now().year,
                schedule_generator=NFLScheduleGenerator(),
                seed=seed,
            )

            # Persist generated schedule if desired
            db_game_ids = []
            if season_id:
                games_data = []
                for game in engine.schedule:
                    games_data.append({
                        "season_id": season_id,
                        "game_id": game.game_id,
                        "week": game.week,
                        "home_team_id": team_id_lookup.get(game.home_team.abbreviation),
                        "away_team_id": team_id_lookup.get(game.away_team.abbreviation),
                        "status": game.status.value,
                        "game_date": game.scheduled_date,
                        "home_score": 0,
                        "away_score": 0,
                    })
                if games_data:
                    db_game_ids = season_game_dao.bulk_create_games(games_data)

            # Simulate schedule using engine and core GameEngine
            season_results = []
            for idx, game in enumerate(engine.schedule):
                result = self.game_engine.simulate_game(game.home_team, game.away_team)
                engine.process_game_result(
                    game.game_id,
                    result.home_score,
                    result.away_score,
                    overtime=getattr(result, "overtime", False),
                    game_duration=getattr(result, "duration", 60),
                )
                formatted_result = self._format_game_result(result)
                formatted_result["game_id"] = game.game_id
                formatted_result["week"] = game.week
                season_results.append(formatted_result)

                if season_id and idx < len(db_game_ids):
                    season_game_dao.update_game_result(
                        game_id=db_game_ids[idx],
                        home_score=result.home_score,
                        away_score=result.away_score,
                    )

            standings = engine.get_standings()

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
                "wins": getattr(team, "wins", 0),
                "losses": getattr(team, "losses", 0),
                "ties": getattr(team, "ties", 0),
                "win_percentage": round(getattr(team, "win_percentage", 0.0), 3),
                "record": getattr(team, "record", "")
            })
        standings_data.sort(key=lambda x: x["win_percentage"], reverse=True)
        return standings_data

    def _to_team_model(self, team_data: Dict[str, Any]) -> Team:
        """Convert DAO dictionaries into Team domain objects."""
        return Team(
            name=team_data.get("name"),
            city=team_data.get("city"),
            abbreviation=team_data.get("abbreviation"),
            conference=team_data.get("conference"),
            division=team_data.get("division"),
        )
