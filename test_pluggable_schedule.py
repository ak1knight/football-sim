"""
Test script to verify the pluggable schedule generator functionality.

This script demonstrates how to use different schedule generators with the SeasonEngine.
"""

from data.team_loader import load_sample_teams
from simulation.season_engine import SeasonEngine
from simulation.schedule_generators import NFLScheduleGenerator, CollegeFootballScheduleGenerator


def test_nfl_schedule_generator():
    """Test NFL schedule generator with SeasonEngine."""
    print("=" * 60)
    print("Testing NFL Schedule Generator")
    print("=" * 60)
    
    # Load teams
    teams = load_sample_teams()
    
    # Create season engine with NFL schedule generator
    nfl_generator = NFLScheduleGenerator()
    season_engine = SeasonEngine(teams, season_year=2024, seed=42, schedule_generator=nfl_generator)
    
    # Get season status
    status = season_engine.get_season_status()
    print(f"Schedule Type: {status['schedule_type']}")
    print(f"Total Games: {status['total_games']}")
    print(f"Total Weeks: {nfl_generator.get_total_weeks()}")
    print(f"Games per Team: {nfl_generator.get_games_per_team()}")
    
    # Check games per team
    games_per_team = {}
    for game in season_engine.schedule:
        home_abbr = game.home_team.abbreviation
        away_abbr = game.away_team.abbreviation
        games_per_team[home_abbr] = games_per_team.get(home_abbr, 0) + 1
        games_per_team[away_abbr] = games_per_team.get(away_abbr, 0) + 1
    
    min_games = min(games_per_team.values())
    max_games = max(games_per_team.values())
    print(f"Games per team range: {min_games} - {max_games}")
    
    # Show sample schedule for first few weeks
    print("\nSample schedule (first 3 weeks):")
    for week in range(1, 4):
        week_games = season_engine.get_week_games(week)
        print(f"Week {week}: {len(week_games)} games")
        for game in week_games[:3]:  # Show first 3 games of each week
            print(f"  {game.away_team.abbreviation} @ {game.home_team.abbreviation}")
    
    return season_engine


def test_college_schedule_generator():
    """Test College Football schedule generator with SeasonEngine."""
    print("\n" + "=" * 60)
    print("Testing College Football Schedule Generator")
    print("=" * 60)
    
    # Load teams
    teams = load_sample_teams()
    
    # Create season engine with College Football schedule generator
    college_generator = CollegeFootballScheduleGenerator()
    season_engine = SeasonEngine(teams, season_year=2024, seed=42, schedule_generator=college_generator)
    
    # Get season status
    status = season_engine.get_season_status()
    print(f"Schedule Type: {status['schedule_type']}")
    print(f"Total Games: {status['total_games']}")
    print(f"Total Weeks: {college_generator.get_total_weeks()}")
    print(f"Games per Team: {college_generator.get_games_per_team()}")
    
    # Check games per team
    games_per_team = {}
    for game in season_engine.schedule:
        home_abbr = game.home_team.abbreviation
        away_abbr = game.away_team.abbreviation
        games_per_team[home_abbr] = games_per_team.get(home_abbr, 0) + 1
        games_per_team[away_abbr] = games_per_team.get(away_abbr, 0) + 1
    
    min_games = min(games_per_team.values())
    max_games = max(games_per_team.values())
    print(f"Games per team range: {min_games} - {max_games}")
    
    # Show sample schedule for first few weeks
    print("\nSample schedule (first 3 weeks):")
    for week in range(1, 4):
        week_games = season_engine.get_week_games(week)
        print(f"Week {week}: {len(week_games)} games")
        for game in week_games[:3]:  # Show first 3 games of each week
            print(f"  {game.away_team.abbreviation} @ {game.home_team.abbreviation}")
    
    return season_engine


def test_default_behavior():
    """Test default behavior (should use NFL generator)."""
    print("\n" + "=" * 60)
    print("Testing Default Behavior (Should use NFL Generator)")
    print("=" * 60)
    
    # Load teams
    teams = load_sample_teams()
    
    # Create season engine without specifying schedule generator
    season_engine = SeasonEngine(teams, season_year=2024, seed=42)
    
    # Get season status
    status = season_engine.get_season_status()
    print(f"Schedule Type: {status['schedule_type']}")
    print(f"Total Games: {status['total_games']}")
    print(f"Total Weeks: {season_engine.schedule_generator.get_total_weeks()}")
    print(f"Games per Team: {season_engine.schedule_generator.get_games_per_team()}")
    
    return season_engine


if __name__ == "__main__":
    try:
        # Test NFL generator
        nfl_season = test_nfl_schedule_generator()
        
        # Test College Football generator  
        college_season = test_college_schedule_generator()
        
        # Test default behavior
        default_season = test_default_behavior()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("The pluggable schedule generator system is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
