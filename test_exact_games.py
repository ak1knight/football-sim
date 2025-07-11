#!/usr/bin/env python3
"""
Test script to verify exact game counts per team
"""

from data.team_loader import load_sample_teams
from simulation.season_engine import SeasonEngine

def test_game_counts():
    """Test that every team plays exactly 17 games"""
    print("🏈 Testing exact game counts per team...")
    
    # Load teams
    teams = load_sample_teams()
    
    # Create season engine
    season_engine = SeasonEngine(teams, 2024)
    
    # Count games per team
    games_per_team = {}
    for team in teams:
        games_per_team[team.abbreviation] = 0
    
    # Count all games
    for game in season_engine.schedule:
        games_per_team[game.home_team.abbreviation] += 1
        games_per_team[game.away_team.abbreviation] += 1
    
    # Print results
    print(f"📅 Total games: {len(season_engine.schedule)}")
    print(f"🏆 Expected games per team: 17")
    print()
    
    # Check each team
    incorrect_teams = []
    for team_abbrev, game_count in sorted(games_per_team.items()):
        status = "✅" if game_count == 17 else "❌"
        print(f"{status} {team_abbrev}: {game_count} games")
        if game_count != 17:
            incorrect_teams.append((team_abbrev, game_count))
    
    print()
    if incorrect_teams:
        print(f"❌ {len(incorrect_teams)} teams don't have exactly 17 games:")
        for team, count in incorrect_teams:
            print(f"   {team}: {count} games")
    else:
        print("✅ All teams have exactly 17 games!")
    
    # Print summary statistics
    game_counts = list(games_per_team.values())
    print(f"\n📊 Game count statistics:")
    print(f"   Min: {min(game_counts)}")
    print(f"   Max: {max(game_counts)}")
    print(f"   Average: {sum(game_counts) / len(game_counts):.1f}")
    
    # Verify total games is correct
    total_team_games = sum(game_counts)
    expected_total_games = len(teams) * 17 // 2  # Each game involves 2 teams
    print(f"\n🎯 Total verification:")
    print(f"   Games scheduled: {len(season_engine.schedule)}")
    print(f"   Expected games: {expected_total_games}")
    print(f"   Status: {'✅ Match!' if len(season_engine.schedule) == expected_total_games else '❌ Mismatch!'}")

if __name__ == "__main__":
    test_game_counts()
