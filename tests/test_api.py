"""
Unit tests for the API module.

Tests for SimulationAPI and TeamAPI classes.
"""

import unittest
from api.simulation_api import SimulationAPI
from api.team_api import TeamAPI

class TestSimulationAPI(unittest.TestCase):
    """Test cases for the SimulationAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = SimulationAPI()
    
    def test_api_initialization(self):
        """Test SimulationAPI initialization."""
        self.assertIsNotNone(self.api.game_engine)
        self.assertEqual(len(self.api.simulation_history), 0)
    
    def test_simulate_game_valid_teams(self):
        """Test simulating a game with valid team IDs."""
        result = self.api.simulate_game("PHI", "DAL")
        
        self.assertNotIn("error", result)
        self.assertIn("home_team", result)
        self.assertIn("away_team", result)
        self.assertIn("winner", result)
        self.assertIn("summary", result)
        
        # Check that scores are integers
        self.assertIsInstance(result["home_team"]["score"], int)
        self.assertIsInstance(result["away_team"]["score"], int)
        
        # Check that history was updated
        self.assertEqual(len(self.api.simulation_history), 1)
    
    def test_simulate_game_invalid_home_team(self):
        """Test simulating a game with invalid home team ID."""
        result = self.api.simulate_game("INVALID", "DAL")
        
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])
    
    def test_simulate_game_invalid_away_team(self):
        """Test simulating a game with invalid away team ID."""
        result = self.api.simulate_game("PHI", "INVALID")
        
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])
    
    def test_simulate_game_with_seed(self):
        """Test simulating a game with a specific seed."""
        result1 = self.api.simulate_game("PHI", "DAL", seed=42)
        
        # Create new API instance to test reproducibility
        api2 = SimulationAPI()
        result2 = api2.simulate_game("PHI", "DAL", seed=42)
        
        # Results should be identical with same seed
        self.assertEqual(result1["home_team"]["score"], result2["home_team"]["score"])
        self.assertEqual(result1["away_team"]["score"], result2["away_team"]["score"])
    
    def test_get_simulation_history_empty(self):
        """Test getting simulation history when empty."""
        history = self.api.get_simulation_history()
        
        self.assertIn("history", history)
        self.assertIn("total_simulations", history)
        self.assertEqual(len(history["history"]), 0)
        self.assertEqual(history["total_simulations"], 0)
    
    def test_get_simulation_history_with_data(self):
        """Test getting simulation history with data."""
        # Run a few simulations
        self.api.simulate_game("PHI", "DAL")
        self.api.simulate_game("KC", "BUF")
        
        history = self.api.get_simulation_history()
        
        self.assertEqual(len(history["history"]), 2)
        self.assertEqual(history["total_simulations"], 2)
        
        # Check that history entries have required fields
        entry = history["history"][0]
        self.assertIn("timestamp", entry)
        self.assertIn("simulation", entry)
        self.assertIn("seed", entry)
    
    def test_get_simulation_history_limit(self):
        """Test getting simulation history with limit."""
        # Run multiple simulations
        for i in range(5):
            self.api.simulate_game("PHI", "DAL")
        
        # Get limited history
        history = self.api.get_simulation_history(limit=3)
        
        self.assertEqual(len(history["history"]), 3)
        self.assertEqual(history["total_simulations"], 5)
    
    def test_simulate_season_valid_teams(self):
        """Test simulating a season with valid teams."""
        result = self.api.simulate_season(["PHI", "DAL", "KC"])
        
        self.assertNotIn("error", result)
        self.assertIn("season_results", result)
        self.assertIn("standings", result)
        self.assertIn("total_games", result)
        
        # Should have games between all teams
        self.assertGreater(len(result["season_results"]), 0)
        self.assertEqual(len(result["standings"]), 3)
    
    def test_simulate_season_invalid_team(self):
        """Test simulating a season with invalid team."""
        result = self.api.simulate_season(["PHI", "INVALID"])
        
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])
    
    def test_simulate_season_insufficient_teams(self):
        """Test simulating a season with insufficient teams."""
        result = self.api.simulate_season(["PHI"])
        
        self.assertIn("error", result)
        self.assertIn("at least 2 teams", result["error"])

class TestTeamAPI(unittest.TestCase):
    """Test cases for the TeamAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = TeamAPI()
    
    def test_api_initialization(self):
        """Test TeamAPI initialization."""
        self.assertIsNotNone(self.api.logger)
    
    def test_get_all_teams(self):
        """Test getting all teams."""
        result = self.api.get_all_teams()
        
        self.assertNotIn("error", result)
        self.assertIn("teams", result)
        self.assertIn("total_teams", result)
        self.assertGreater(len(result["teams"]), 0)
        self.assertEqual(len(result["teams"]), result["total_teams"])
        
        # Check team structure
        team = result["teams"][0]
        required_fields = ["id", "name", "full_name", "city", "abbreviation", 
                          "conference", "division", "record", "win_percentage", "overall_rating"]
        for field in required_fields:
            self.assertIn(field, team)
    
    def test_get_team_details_valid_id(self):
        """Test getting team details with valid team ID."""
        result = self.api.get_team_details("PHI")
        
        self.assertNotIn("error", result)
        self.assertIn("name", result)
        self.assertIn("full_name", result)
        self.assertIn("roster_size", result)
        self.assertIn("stats", result)
        
        # Check stats structure
        stats = result["stats"]
        self.assertIn("offensive_rating", stats)
        self.assertIn("defensive_rating", stats)
        self.assertIn("coaching_rating", stats)
    
    def test_get_team_details_invalid_id(self):
        """Test getting team details with invalid team ID."""
        result = self.api.get_team_details("INVALID")
        
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])
    
    def test_get_team_roster_valid_id(self):
        """Test getting team roster with valid team ID."""
        result = self.api.get_team_roster("PHI")
        
        self.assertNotIn("error", result)
        self.assertIn("team", result)
        self.assertIn("roster", result)
        self.assertIn("total_players", result)
        self.assertIn("available_players", result)
        
        # Check roster structure
        roster = result["roster"]
        self.assertIsInstance(roster, dict)
        
        # Should have position groups
        expected_groups = ["Offense", "Defense", "Special Teams"]
        for group in expected_groups:
            if group in roster:
                # Check player structure
                if len(roster[group]) > 0:
                    player = roster[group][0]
                    required_fields = ["name", "jersey_number", "position", 
                                     "position_group", "overall_rating", "available"]
                    for field in required_fields:
                        self.assertIn(field, player)
    
    def test_get_team_roster_invalid_id(self):
        """Test getting team roster with invalid team ID."""
        result = self.api.get_team_roster("INVALID")
        
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])
    
    def test_get_team_stats_valid_id(self):
        """Test getting team stats with valid team ID."""
        result = self.api.get_team_stats("PHI")
        
        self.assertNotIn("error", result)
        self.assertIn("team", result)
        self.assertIn("overall_rating", result)
        self.assertIn("offensive_stats", result)
        self.assertIn("defensive_stats", result)
        self.assertIn("special_teams", result)
        self.assertIn("coaching", result)
        self.assertIn("home_field_advantage", result)
        
        # Check offensive stats structure
        offensive = result["offensive_stats"]
        self.assertIn("overall", offensive)
        self.assertIn("passing", offensive)
        self.assertIn("rushing", offensive)
        
        # Check defensive stats structure
        defensive = result["defensive_stats"]
        self.assertIn("overall", defensive)
        self.assertIn("pass_defense", defensive)
        self.assertIn("run_defense", defensive)
    
    def test_get_team_stats_invalid_id(self):
        """Test getting team stats with invalid team ID."""
        result = self.api.get_team_stats("INVALID")
        
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])
    
    def test_compare_teams_valid_ids(self):
        """Test comparing two teams with valid IDs."""
        result = self.api.compare_teams("PHI", "DAL")
        
        self.assertNotIn("error", result)
        self.assertIn("team1", result)
        self.assertIn("team2", result)
        self.assertIn("comparison", result)
        
        # Check comparison structure
        comparison = result["comparison"]
        self.assertIn("overall_rating", comparison)
        self.assertIn("offense", comparison)
        self.assertIn("defense", comparison)
        
        # Each comparison should have team1, team2, and advantage
        for category in ["overall_rating", "offense", "defense"]:
            cat_data = comparison[category]
            self.assertIn("team1", cat_data)
            self.assertIn("team2", cat_data)
            self.assertIn("advantage", cat_data)
    
    def test_compare_teams_invalid_first_id(self):
        """Test comparing teams with invalid first team ID."""
        result = self.api.compare_teams("INVALID", "DAL")
        
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])
    
    def test_compare_teams_invalid_second_id(self):
        """Test comparing teams with invalid second team ID."""
        result = self.api.compare_teams("PHI", "INVALID")
        
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])

if __name__ == '__main__':
    unittest.main()
