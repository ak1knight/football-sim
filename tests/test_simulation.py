"""
Unit tests for the simulation module.

Tests for GameEngine and simulation logic.
"""

import unittest
from simulation.game_engine import GameEngine, GameResult
from models.team import Team, TeamStats
from models.player import Player, Position, PlayerStats
from data.team_loader import load_sample_teams

class TestGameEngine(unittest.TestCase):
    """Test cases for the GameEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = GameEngine(seed=42)  # Use seed for reproducible tests
        
        # Create two test teams
        self.home_team = Team(
            name="Home Team",
            city="Home",
            abbreviation="HOM",
            conference="NFC",
            division="East",
            stats=TeamStats(offensive_rating=80, defensive_rating=75)
        )
        
        self.away_team = Team(
            name="Away Team", 
            city="Away",
            abbreviation="AWY",
            conference="AFC",
            division="West",
            stats=TeamStats(offensive_rating=75, defensive_rating=80)
        )
        
        # Add minimal rosters
        home_stats = PlayerStats(overall_rating=80)
        away_stats = PlayerStats(overall_rating=75)
        
        self.home_team.add_player(Player("Home QB", Position.QB, 1, home_stats))
        self.home_team.add_player(Player("Home RB", Position.RB, 2, home_stats))
        
        self.away_team.add_player(Player("Away QB", Position.QB, 1, away_stats))
        self.away_team.add_player(Player("Away RB", Position.RB, 2, away_stats))
    
    def test_engine_initialization(self):
        """Test GameEngine initialization."""
        engine = GameEngine()
        self.assertIsNotNone(engine)
        
        # Test with seed
        seeded_engine = GameEngine(seed=123)
        self.assertIsNotNone(seeded_engine)
    
    def test_simulate_game_returns_result(self):
        """Test that simulate_game returns a valid GameResult."""
        result = self.engine.simulate_game(self.home_team, self.away_team)
        
        self.assertIsInstance(result, GameResult)
        self.assertEqual(result.home_team, self.home_team)
        self.assertEqual(result.away_team, self.away_team)
        self.assertIsInstance(result.home_score, int)
        self.assertIsInstance(result.away_score, int)
        self.assertGreaterEqual(result.home_score, 0)
        self.assertGreaterEqual(result.away_score, 0)
        self.assertGreater(result.duration, 0)
    
    def test_game_result_winner_property(self):
        """Test the winner property of GameResult."""
        # Test home team wins
        result = GameResult(
            home_team=self.home_team,
            away_team=self.away_team,
            home_score=21,
            away_score=14,
            duration=60
        )
        self.assertEqual(result.winner, self.home_team)
        
        # Test away team wins
        result = GameResult(
            home_team=self.home_team,
            away_team=self.away_team,
            home_score=14,
            away_score=21,
            duration=60
        )
        self.assertEqual(result.winner, self.away_team)
        
        # Test tie
        result = GameResult(
            home_team=self.home_team,
            away_team=self.away_team,
            home_score=14,
            away_score=14,
            duration=60
        )
        self.assertIsNone(result.winner)
    
    def test_reproducible_simulations(self):
        """Test that simulations with the same seed are reproducible."""
        engine1 = GameEngine(seed=42)
        engine2 = GameEngine(seed=42)
        
        result1 = engine1.simulate_game(self.home_team, self.away_team)
        result2 = engine2.simulate_game(self.home_team, self.away_team)
        
        self.assertEqual(result1.home_score, result2.home_score)
        self.assertEqual(result1.away_score, result2.away_score)
    
    def test_different_seeds_produce_different_results(self):
        """Test that different seeds can produce different results."""
        engine1 = GameEngine(seed=1)
        engine2 = GameEngine(seed=2)
        
        # Run multiple simulations to increase chance of different outcomes
        results1 = []
        results2 = []
        
        for _ in range(5):
            # Reset teams for fresh simulations
            fresh_home = Team("Home", "Home", "HOM", "NFC", "East")
            fresh_away = Team("Away", "Away", "AWY", "AFC", "West")
            
            fresh_home.add_player(Player("QB", Position.QB, 1, PlayerStats(overall_rating=80)))
            fresh_away.add_player(Player("QB", Position.QB, 1, PlayerStats(overall_rating=80)))
            
            result1 = engine1.simulate_game(fresh_home, fresh_away)
            result2 = engine2.simulate_game(fresh_home, fresh_away)
            
            results1.append((result1.home_score, result1.away_score))
            results2.append((result2.home_score, result2.away_score))
        
        # At least one result should be different (highly probable with different seeds)
        self.assertNotEqual(results1, results2)
    
    def test_team_records_updated(self):
        """Test that team records are updated after simulation."""
        initial_home_wins = self.home_team.wins
        initial_home_losses = self.home_team.losses
        initial_away_wins = self.away_team.wins
        initial_away_losses = self.away_team.losses
        
        result = self.engine.simulate_game(self.home_team, self.away_team)
        
        # Check that one team got a win and one got a loss (or both got ties)
        total_wins = self.home_team.wins + self.away_team.wins
        total_losses = self.home_team.losses + self.away_team.losses
        total_ties = self.home_team.ties + self.away_team.ties
        
        if result.home_score != result.away_score:
            # Non-tie game
            self.assertEqual(total_wins, initial_home_wins + initial_away_wins + 1)
            self.assertEqual(total_losses, initial_home_losses + initial_away_losses + 1)
        else:
            # Tie game
            self.assertEqual(total_ties, 2)  # Both teams get a tie
    
    def test_success_probability_calculation(self):
        """Test the success probability calculation."""
        # Higher offensive rating should give higher success probability
        high_prob = self.engine._calculate_success_probability(90, 70)
        low_prob = self.engine._calculate_success_probability(70, 90)
        
        self.assertGreater(high_prob, low_prob)
        
        # Probabilities should be within valid range
        self.assertGreaterEqual(high_prob, 0.1)
        self.assertLessEqual(high_prob, 0.8)
        self.assertGreaterEqual(low_prob, 0.1)
        self.assertLessEqual(low_prob, 0.8)
    
    def test_points_calculation(self):
        """Test the points calculation for different outcomes."""
        self.assertEqual(self.engine._calculate_points('touchdown'), 7)
        self.assertEqual(self.engine._calculate_points('field_goal'), 3)
        self.assertEqual(self.engine._calculate_points('safety'), 2)
        self.assertEqual(self.engine._calculate_points('missed_fg'), 0)
        self.assertEqual(self.engine._calculate_points('turnover'), 0)
        self.assertEqual(self.engine._calculate_points('punt'), 0)
        self.assertEqual(self.engine._calculate_points('unknown'), 0)
    
    def test_sample_teams_simulation(self):
        """Test simulation with sample teams."""
        teams = load_sample_teams()
        self.assertGreaterEqual(len(teams), 2)
        
        result = self.engine.simulate_game(teams[0], teams[1])
        self.assertIsInstance(result, GameResult)
        self.assertGreaterEqual(result.home_score, 0)
        self.assertGreaterEqual(result.away_score, 0)

if __name__ == '__main__':
    unittest.main()
