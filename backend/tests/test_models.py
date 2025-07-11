"""
Unit tests for the models module.

Tests for Player and Team classes and their functionality.
"""

import unittest
from models.player import Player, Position, PlayerStats
from models.team import Team, TeamStats

class TestPlayer(unittest.TestCase):
    """Test cases for the Player class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.stats = PlayerStats(overall_rating=85, speed=90, strength=80)
        self.player = Player(
            name="Test Player",
            position=Position.QB,
            jersey_number=12,
            stats=self.stats,
            age=28
        )
    
    def test_player_creation(self):
        """Test creating a player with valid data."""
        self.assertEqual(self.player.name, "Test Player")
        self.assertEqual(self.player.position, Position.QB)
        self.assertEqual(self.player.jersey_number, 12)
        self.assertEqual(self.player.age, 28)
        self.assertEqual(self.player.stats.overall_rating, 85)
    
    def test_invalid_jersey_number(self):
        """Test that invalid jersey numbers raise an error."""
        with self.assertRaises(ValueError):
            Player("Test", Position.QB, 0, self.stats)  # Too low
        
        with self.assertRaises(ValueError):
            Player("Test", Position.QB, 100, self.stats)  # Too high
    
    def test_invalid_age(self):
        """Test that invalid ages raise an error."""
        with self.assertRaises(ValueError):
            Player("Test", Position.QB, 12, self.stats, age=17)  # Too young
        
        with self.assertRaises(ValueError):
            Player("Test", Position.QB, 12, self.stats, age=50)  # Too old
    
    def test_invalid_overall_rating(self):
        """Test that invalid overall ratings raise an error."""
        bad_stats = PlayerStats(overall_rating=101)
        with self.assertRaises(ValueError):
            Player("Test", Position.QB, 12, bad_stats)
    
    def test_is_available(self):
        """Test player availability based on injury status."""
        self.assertTrue(self.player.is_available())
        
        self.player.injury_status = True
        self.assertFalse(self.player.is_available())
    
    def test_position_group(self):
        """Test getting position groups."""
        qb = Player("QB", Position.QB, 1, self.stats)
        self.assertEqual(qb.get_position_group(), "Offense")
        
        lb = Player("LB", Position.LB, 2, self.stats)
        self.assertEqual(lb.get_position_group(), "Defense")
        
        k = Player("K", Position.K, 3, self.stats)
        self.assertEqual(k.get_position_group(), "Special Teams")
    
    def test_string_representation(self):
        """Test the string representation of a player."""
        expected = "#12 Test Player (Quarterback) - OVR: 85"
        self.assertEqual(str(self.player), expected)

class TestTeam(unittest.TestCase):
    """Test cases for the Team class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.stats = TeamStats(
            offensive_rating=85,
            defensive_rating=80,
            coaching_rating=75
        )
        self.team = Team(
            name="Eagles",
            city="Philadelphia",
            abbreviation="PHI",
            conference="NFC",
            division="East",
            stats=self.stats
        )
        
        # Add some test players
        player_stats = PlayerStats(overall_rating=80)
        self.qb = Player("Test QB", Position.QB, 1, player_stats)
        self.rb = Player("Test RB", Position.RB, 2, player_stats)
        self.team.add_player(self.qb)
        self.team.add_player(self.rb)
    
    def test_team_creation(self):
        """Test creating a team with valid data."""
        self.assertEqual(self.team.name, "Eagles")
        self.assertEqual(self.team.city, "Philadelphia")
        self.assertEqual(self.team.abbreviation, "PHI")
        self.assertEqual(self.team.conference, "NFC")
        self.assertEqual(self.team.division, "East")
    
    def test_invalid_conference(self):
        """Test that invalid conferences raise an error."""
        with self.assertRaises(ValueError):
            Team("Test", "Test", "TST", "XFL", "East")
    
    def test_invalid_division(self):
        """Test that invalid divisions raise an error."""
        with self.assertRaises(ValueError):
            Team("Test", "Test", "TST", "NFC", "Central")
    
    def test_full_name(self):
        """Test the full team name property."""
        self.assertEqual(self.team.full_name, "Philadelphia Eagles")
    
    def test_record_and_win_percentage(self):
        """Test record tracking and win percentage calculation."""
        self.assertEqual(self.team.record, "0-0-0")
        self.assertEqual(self.team.win_percentage, 0.0)
        
        # Add some wins and losses
        self.team.update_record(won=True)
        self.team.update_record(won=False)
        self.team.update_record(won=True)
        
        self.assertEqual(self.team.record, "2-1-0")
        self.assertAlmostEqual(self.team.win_percentage, 0.667, places=3)
        
        # Add a tie
        self.team.update_record(won=False, tied=True)
        self.assertEqual(self.team.record, "2-1-1")
        self.assertAlmostEqual(self.team.win_percentage, 0.625, places=3)
    
    def test_add_player(self):
        """Test adding players to the team."""
        initial_count = len(self.team.players)
        
        new_stats = PlayerStats(overall_rating=75)
        new_player = Player("New Player", Position.WR, 3, new_stats)
        self.team.add_player(new_player)
        
        self.assertEqual(len(self.team.players), initial_count + 1)
        self.assertIn(new_player, self.team.players)
    
    def test_duplicate_jersey_number(self):
        """Test that duplicate jersey numbers raise an error."""
        duplicate_stats = PlayerStats(overall_rating=75)
        duplicate_player = Player("Duplicate", Position.WR, 1, duplicate_stats)  # Same as QB
        
        with self.assertRaises(ValueError):
            self.team.add_player(duplicate_player)
    
    def test_get_players_by_position(self):
        """Test getting players by position."""
        qbs = self.team.get_players_by_position(Position.QB)
        self.assertEqual(len(qbs), 1)
        self.assertEqual(qbs[0], self.qb)
        
        rbs = self.team.get_players_by_position(Position.RB)
        self.assertEqual(len(rbs), 1)
        self.assertEqual(rbs[0], self.rb)
        
        wrs = self.team.get_players_by_position(Position.WR)
        self.assertEqual(len(wrs), 0)
    
    def test_get_available_players(self):
        """Test getting available (non-injured) players."""
        available = self.team.get_available_players()
        self.assertEqual(len(available), 2)  # Both players healthy
        
        # Injure one player
        self.qb.injury_status = True
        available = self.team.get_available_players()
        self.assertEqual(len(available), 1)
        self.assertNotIn(self.qb, available)
        self.assertIn(self.rb, available)
    
    def test_team_overall_rating(self):
        """Test calculating team overall rating."""
        # Should be average of player ratings
        expected_rating = (self.qb.stats.overall_rating + self.rb.stats.overall_rating) // 2
        self.assertEqual(self.team.get_team_overall_rating(), expected_rating)
        
        # Test with no players
        empty_team = Team("Empty", "Empty", "EMP", "AFC", "West")
        self.assertEqual(empty_team.get_team_overall_rating(), 0)
    
    def test_string_representation(self):
        """Test the string representation of a team."""
        expected = "Philadelphia Eagles (0-0-0) - OVR: 80"
        self.assertEqual(str(self.team), expected)

if __name__ == '__main__':
    unittest.main()
