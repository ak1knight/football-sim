#!/usr/bin/env python3
"""
Simple test to verify the season engine's schedule generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.team_loader import load_sample_teams
from simulation.season_engine import SeasonEngine

def test_season_engine():
    """Test the season engine directly."""
    print("🏈 Testing Season Engine directly...")
    
    # Load teams
    teams = load_sample_teams()
    print(f"📋 Loaded {len(teams)} teams")
    
    # Create season engine
    season_engine = SeasonEngine(teams, season_year=2024, seed=42)
    
    # Check schedule
    print(f"📅 Total scheduled games: {len(season_engine.schedule)}")
    
    # Count games per team
    games_per_team = {}
    for team in teams:
        games_per_team[team.abbreviation] = 0
    
    for game in season_engine.schedule:
        games_per_team[game.home_team.abbreviation] += 1
        games_per_team[game.away_team.abbreviation] += 1
    
    print(f"🎯 Games per team:")
    for team_abbr, count in games_per_team.items():
        status = "✅" if count == 17 else "❌"
        print(f"   {status} {team_abbr}: {count} games")
    
    # Summary
    unique_counts = set(games_per_team.values())
    print(f"\n📊 Summary:")
    print(f"   Total games scheduled: {len(season_engine.schedule)}")
    print(f"   Game counts per team: {sorted(unique_counts)}")
    print(f"   Expected: 17 games per team, 272 total games")
    
    if len(unique_counts) == 1 and list(unique_counts)[0] == 17:
        print("✅ SUCCESS: All teams have exactly 17 games!")
    else:
        print("❌ FAILURE: Game counts are not balanced!")

if __name__ == "__main__":
    test_season_engine()
