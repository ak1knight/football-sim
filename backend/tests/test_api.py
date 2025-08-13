"""
Unit tests for the API module.

Tests for SimulationAPI and TeamAPI classes, updated for database persistence.
"""

import unittest
from unittest.mock import patch, MagicMock
from api.simulation_api import SimulationAPI
from api.team_api import TeamAPI

class TestSimulationAPI(unittest.TestCase):
    """Test cases for the SimulationAPI class with database persistence."""

    def setUp(self):
        """Set up test fixtures."""
        self.api = SimulationAPI()

    @patch("api.simulation_api.TeamDAO")
    @patch("api.simulation_api.SeasonGameDAO")
    @patch("api.simulation_api.get_db_manager")
    def test_simulate_game_valid_teams(self, mock_get_db_manager, mock_season_game_dao, mock_team_dao):
        """Test simulating a game with valid team IDs and database persistence."""
        mock_db = MagicMock()
        mock_get_db_manager.return_value = mock_db

        # Mock team DAO
        mock_team = MagicMock()
        mock_team.id = "PHI"
        mock_team.abbreviation = "PHI"
        mock_team.full_name = "Philadelphia Eagles"
        mock_team.wins = 0
        mock_team.losses = 0
        mock_team.ties = 0
        mock_team.win_percentage = 0.0
        mock_team.record = "0-0"
        mock_team_dao.return_value.get_by_id.side_effect = lambda tid: {"id": tid, "abbreviation": tid, "full_name": f"Team {tid}"} if tid in ["PHI", "DAL"] else None

        # Mock season game DAO
        mock_season_game_dao.return_value.create_game.return_value = "game123"
        mock_season_game_dao.return_value.update_game_result.return_value = True

        result = self.api.simulate_game("PHI", "DAL", season_id="season1", week=1)
        self.assertNotIn("error", result)
        self.assertIn("home_team", result)
        self.assertIn("away_team", result)
        self.assertIn("winner", result)
        self.assertIn("summary", result)
        self.assertEqual(result["game_id"], "game123")

    @patch("api.simulation_api.TeamDAO")
    @patch("api.simulation_api.get_db_manager")
    def test_simulate_game_invalid_home_team(self, mock_get_db_manager, mock_team_dao):
        """Test simulating a game with invalid home team ID."""
        mock_db = MagicMock()
        mock_get_db_manager.return_value = mock_db
        mock_team_dao.return_value.get_by_id.side_effect = lambda tid: None

        result = self.api.simulate_game("INVALID", "DAL", season_id="season1", week=1)
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])

    @patch("api.simulation_api.TeamDAO")
    @patch("api.simulation_api.get_db_manager")
    def test_simulate_game_invalid_away_team(self, mock_get_db_manager, mock_team_dao):
        """Test simulating a game with invalid away team ID."""
        mock_db = MagicMock()
        mock_get_db_manager.return_value = mock_db
        mock_team_dao.return_value.get_by_id.side_effect = lambda tid: {"id": tid, "abbreviation": tid, "full_name": f"Team {tid}"} if tid == "PHI" else None

        result = self.api.simulate_game("PHI", "INVALID", season_id="season1", week=1)
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])

    @patch("api.simulation_api.TeamDAO")
    @patch("api.simulation_api.SeasonGameDAO")
    @patch("api.simulation_api.get_db_manager")
    def test_simulate_game_with_seed(self, mock_get_db_manager, mock_season_game_dao, mock_team_dao):
        """Test simulating a game with a specific seed for reproducibility."""
        mock_db = MagicMock()
        mock_get_db_manager.return_value = mock_db
        mock_team_dao.return_value.get_by_id.side_effect = lambda tid: {"id": tid, "abbreviation": tid, "full_name": f"Team {tid}"} if tid in ["PHI", "DAL"] else None
        mock_season_game_dao.return_value.create_game.return_value = "game123"
        mock_season_game_dao.return_value.update_game_result.return_value = True

        result1 = self.api.simulate_game("PHI", "DAL", seed=42, season_id="season1", week=1)
        api2 = SimulationAPI()
        with patch("api.simulation_api.TeamDAO", mock_team_dao), \
             patch("api.simulation_api.SeasonGameDAO", mock_season_game_dao), \
             patch("api.simulation_api.get_db_manager", return_value=mock_db):
            result2 = api2.simulate_game("PHI", "DAL", seed=42, season_id="season1", week=1)
        self.assertEqual(result1["home_team"]["score"], result2["home_team"]["score"])
        self.assertEqual(result1["away_team"]["score"], result2["away_team"]["score"])

    @patch("api.simulation_api.SeasonGameDAO")
    @patch("api.simulation_api.get_db_manager")
    def test_get_simulation_history_empty(self, mock_get_db_manager, mock_season_game_dao):
        """Test getting simulation history when empty."""
        mock_db = MagicMock()
        mock_get_db_manager.return_value = mock_db
        mock_season_game_dao.return_value.get_completed_games.return_value = []

        history = self.api.get_simulation_history(season_id="season1")
        self.assertIn("history", history)
        self.assertIn("total_simulations", history)
        self.assertEqual(len(history["history"]), 0)
        self.assertEqual(history["total_simulations"], 0)

    @patch("api.simulation_api.SeasonGameDAO")
    @patch("api.simulation_api.get_db_manager")
    def test_get_simulation_history_with_data(self, mock_get_db_manager, mock_season_game_dao):
        """Test getting simulation history with data."""
        mock_db = MagicMock()
        mock_get_db_manager.return_value = mock_db
        mock_season_game_dao.return_value.get_completed_games.return_value = [
            {
                "id": "game1",
                "season_id": "season1",
                "week": 1,
                "home_team_id": "PHI",
                "away_team_id": "DAL",
                "home_team_name": "Eagles",
                "home_team_city": "Philadelphia",
                "home_team_abbr": "PHI",
                "away_team_name": "Cowboys",
                "away_team_city": "Dallas",
                "away_team_abbr": "DAL",
                "home_score": 24,
                "away_score": 21,
                "completed_at": "2025-08-09T22:00:00Z",
                "game_stats": {}
            }
        ]

        history = self.api.get_simulation_history(season_id="season1")
        self.assertEqual(len(history["history"]), 1)
        self.assertEqual(history["total_simulations"], 1)
        entry = history["history"][0]
        self.assertIn("game_id", entry)
        self.assertIn("home_team", entry)
        self.assertIn("away_team", entry)
        self.assertIn("home_score", entry)
        self.assertIn("away_score", entry)
        self.assertIn("completed_at", entry)

if __name__ == '__main__':
    unittest.main()
