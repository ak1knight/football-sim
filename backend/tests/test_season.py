"""
Unit tests for the season management engine.

Tests season creation, scheduling, game result processing,
standings tracking, and API functionality.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from simulation.season_engine import (
    SeasonEngine, ScheduledGame, TeamRecord, GameStatus, SeasonPhase
)
from api.season_api import SeasonAPI
from models.team import Team, TeamStats


class TestSeasonEngine:
    """Test cases for the SeasonEngine class."""
    
    @pytest.fixture
    def sample_teams(self):
        """Create sample teams for testing."""
        teams = []
        
        # AFC East
        bills_stats = TeamStats(offensive_rating=85, defensive_rating=82)
        bills = Team("Bills", "Buffalo", "BUF", "AFC", "East", stats=bills_stats)
        
        dolphins_stats = TeamStats(offensive_rating=80, defensive_rating=78)
        dolphins = Team("Dolphins", "Miami", "MIA", "AFC", "East", stats=dolphins_stats)
        
        # NFC East  
        eagles_stats = TeamStats(offensive_rating=88, defensive_rating=85)
        eagles = Team("Eagles", "Philadelphia", "PHI", "NFC", "East", stats=eagles_stats)
        
        cowboys_stats = TeamStats(offensive_rating=82, defensive_rating=80)
        cowboys = Team("Cowboys", "Dallas", "DAL", "NFC", "East", stats=cowboys_stats)
        
        teams.extend([bills, dolphins, eagles, cowboys])
        return teams
    
    @pytest.fixture
    def season_engine(self, sample_teams):
        """Create a season engine with sample teams."""
        return SeasonEngine(teams=sample_teams, season_year=2024, seed=42)
    
    def test_season_initialization(self, season_engine, sample_teams):
        """Test that season initializes correctly."""
        assert season_engine.season_year == 2024
        assert season_engine.current_week == 1
        assert season_engine.current_phase == SeasonPhase.REGULAR_SEASON
        assert len(season_engine.teams) == len(sample_teams)
        assert len(season_engine.records) == len(sample_teams)
        assert len(season_engine.schedule) > 0
    
    def test_team_records_initialization(self, season_engine, sample_teams):
        """Test that team records are initialized correctly."""
        for team in sample_teams:
            record = season_engine.records[team.abbreviation]
            assert record.team == team
            assert record.wins == 0
            assert record.losses == 0
            assert record.ties == 0
            assert record.points_for == 0
            assert record.points_against == 0
    
    def test_schedule_generation(self, season_engine):
        """Test that schedule is generated properly."""
        # Should have games scheduled
        assert len(season_engine.schedule) > 0
        
        # All games should be for weeks 1-18
        weeks = [game.week for game in season_engine.schedule]
        assert min(weeks) >= 1
        assert max(weeks) <= 18
        
        # All games should start as scheduled
        for game in season_engine.schedule:
            assert game.status == GameStatus.SCHEDULED
            assert game.home_score is None
            assert game.away_score is None
    
    def test_get_next_games(self, season_engine):
        """Test getting next games to simulate."""
        next_games = season_engine.get_next_games(limit=5)
        
        assert len(next_games) <= 5
        for game in next_games:
            assert game.status == GameStatus.SCHEDULED
            assert isinstance(game, ScheduledGame)
    
    def test_get_week_games(self, season_engine):
        """Test getting games for a specific week."""
        week_1_games = season_engine.get_week_games(1)
        
        assert len(week_1_games) > 0
        for game in week_1_games:
            assert game.week == 1
    
    def test_process_game_result(self, season_engine):
        """Test processing a game result."""
        # Get first scheduled game
        game = season_engine.get_next_games(1)[0]
        game_id = game.game_id
        
        # Process result
        success = season_engine.process_game_result(
            game_id=game_id,
            home_score=24,
            away_score=17,
            overtime=False
        )
        
        assert success
        
        # Check game was updated
        updated_game = None
        for g in season_engine.schedule:
            if g.game_id == game_id:
                updated_game = g
                break
        
        assert updated_game is not None
        assert updated_game.status == GameStatus.COMPLETED
        assert updated_game.home_score == 24
        assert updated_game.away_score == 17
        assert updated_game.winner == updated_game.home_team
    
    def test_team_record_updates(self, season_engine):
        """Test that team records are updated correctly after games."""
        # Get first game
        game = season_engine.get_next_games(1)[0]
        home_team = game.home_team
        away_team = game.away_team
        
        # Get initial records
        initial_home_record = season_engine.records[home_team.abbreviation]
        initial_away_record = season_engine.records[away_team.abbreviation]
        
        initial_home_wins = initial_home_record.wins
        initial_away_losses = initial_away_record.losses
        
        # Process game (home team wins)
        season_engine.process_game_result(
            game_id=game.game_id,
            home_score=28,
            away_score=14
        )
        
        # Check records updated
        updated_home_record = season_engine.records[home_team.abbreviation]
        updated_away_record = season_engine.records[away_team.abbreviation]
        
        assert updated_home_record.wins == initial_home_wins + 1
        assert updated_away_record.losses == initial_away_losses + 1
        assert updated_home_record.points_for == 28
        assert updated_home_record.points_against == 14
        assert updated_away_record.points_for == 14
        assert updated_away_record.points_against == 28
    
    def test_standings_generation(self, season_engine):
        """Test standings generation."""
        standings = season_engine.get_standings(by_division=True)
        
        assert isinstance(standings, dict)
        assert len(standings) > 0
        
        # Check that divisions are present
        for division, teams in standings.items():
            assert isinstance(teams, list)
            for team_data in teams:
                assert 'team' in team_data
                assert 'wins' in team_data
                assert 'losses' in team_data
                assert 'win_percentage' in team_data
    
    def test_season_status(self, season_engine):
        """Test season status information."""
        status = season_engine.get_season_status()
        
        assert 'season_year' in status
        assert 'current_week' in status
        assert 'current_phase' in status
        assert 'total_games' in status
        assert 'completed_games' in status
        assert 'completion_percentage' in status
        
        assert status['season_year'] == 2024
        assert status['current_week'] == 1
        assert status['current_phase'] == 'regular_season'
    
    def test_team_schedule(self, season_engine, sample_teams):
        """Test getting a team's schedule."""
        team = sample_teams[0]  # Bills
        schedule = season_engine.get_team_schedule(team.abbreviation)
        
        assert isinstance(schedule, list)
        assert len(schedule) > 0
        
        # Check that all games involve this team
        for game_data in schedule:
            team_involved = (
                game_data['home_team']['abbreviation'] == team.abbreviation or
                game_data['away_team']['abbreviation'] == team.abbreviation
            )
            assert team_involved


class TestSeasonAPI:
    """Test cases for the SeasonAPI class."""
    
    @pytest.fixture
    def season_api(self):
        """Create a season API instance."""
        return SeasonAPI()
    
    def test_create_season(self, season_api):
        """Test season creation through API."""
        result = season_api.create_season(season_year=2024, seed=42)
        
        assert result['success']
        assert 'message' in result
        assert 'season_status' in result
        assert result['season_status']['season_year'] == 2024
    
    def test_get_season_status_no_season(self, season_api):
        """Test getting status when no season exists."""
        result = season_api.get_season_status()
        
        assert not result['success']
        assert 'No active season' in result['error']
    
    def test_get_next_games(self, season_api):
        """Test getting next games through API."""
        # Create season first
        season_api.create_season(2024, seed=42)
        
        result = season_api.get_next_games(limit=5)
        
        assert result['success']
        assert 'games' in result
        assert len(result['games']) <= 5
        assert 'count' in result
        assert 'current_week' in result
    
    def test_submit_game_result(self, season_api):
        """Test submitting game results through API."""
        # Create season and get a game
        season_api.create_season(2024, seed=42)
        next_games = season_api.get_next_games(1)
        
        assert next_games['success']
        assert len(next_games['games']) > 0
        
        game = next_games['games'][0]
        game_id = game['game_id']
        
        # Submit result
        result = season_api.submit_game_result(
            game_id=game_id,
            home_score=21,
            away_score=14
        )
        
        assert result['success']
        assert 'message' in result
        assert 'game_result' in result
        assert result['game_result']['home_score'] == 21
        assert result['game_result']['away_score'] == 14
    
    def test_get_standings(self, season_api):
        """Test getting standings through API."""
        # Create season
        season_api.create_season(2024, seed=42)
        
        result = season_api.get_standings(by_division=True)
        
        assert result['success']
        assert 'standings' in result
        assert result['organization'] == 'division'
    
    def test_get_team_schedule(self, season_api):
        """Test getting team schedule through API."""
        # Create season
        season_api.create_season(2024, seed=42)
        
        # Get all teams to find a valid abbreviation
        teams_result = season_api.get_all_teams()
        assert teams_result['success']
        
        team_abbr = teams_result['teams'][0]['abbreviation']
        
        result = season_api.get_team_schedule(team_abbr)
        
        assert result['success']
        assert 'schedule' in result
        assert 'record' in result
        assert result['team'] == team_abbr
    
    def test_get_all_teams(self, season_api):
        """Test getting all teams through API."""
        result = season_api.get_all_teams()
        
        assert result['success']
        assert 'teams' in result
        assert 'organized_teams' in result
        assert 'total_teams' in result
        assert result['total_teams'] > 0
    
    def test_invalid_game_result(self, season_api):
        """Test submitting invalid game results."""
        season_api.create_season(2024, seed=42)
        
        # Test negative scores
        result = season_api.submit_game_result(
            game_id="invalid_id",
            home_score=-5,
            away_score=14
        )
        
        assert not result['success']
        assert 'negative' in result['error'].lower()
    
    def test_nonexistent_game_result(self, season_api):
        """Test submitting result for nonexistent game."""
        season_api.create_season(2024, seed=42)
        
        result = season_api.submit_game_result(
            game_id="nonexistent_game",
            home_score=21,
            away_score=14
        )
        
        assert not result['success']
        assert 'not found' in result['error'].lower()


if __name__ == "__main__":
    pytest.main([__file__])
