#!/usr/bin/env python3

"""
Test quarter transition logic to ensure possession is maintained properly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.team_loader import load_sample_teams
from simulation.game_engine import GameEngine


def test_quarter_transitions():
    """Test quarter transition logic and scoring improvements."""
    print("🏈 Testing Quarter Transitions and Scoring")
    print("=" * 50)
    
    # Load teams
    teams = load_sample_teams()
    
    # Use specific teams for testing
    bills = next(t for t in teams if t.name == "Bills")
    dolphins = next(t for t in teams if t.name == "Dolphins")
    
    # Test multiple games to see patterns
    games_played = 0
    overtime_games = 0
    total_points = 0
    
    print(f"Testing multiple games between {bills.name} and {dolphins.name}")
    print(f"Looking for quarter transition preservation and improved scoring...")
    print()
    
    for game_num in range(5):
        print(f"Game {game_num + 1}:")
        print("-" * 20)
        
        # Create game engine with reporting for first game
        engine = GameEngine(
            seed=42 + game_num,
            enable_reporting=True,
            verbose=(game_num == 0)  # Only verbose for first game
        )
        
        # Simulate game
        result = engine.simulate_game(bills, dolphins)
        
        games_played += 1
        game_total = result.home_score + result.away_score
        total_points += game_total
        
        if result.duration > 60:
            overtime_games += 1
            print(f"   Result: {result.home_team.name} {result.home_score} - {result.away_team.name} {result.away_score} (OT)")
        else:
            print(f"   Result: {result.home_team.name} {result.home_score} - {result.away_team.name} {result.away_score}")
        
        print(f"   Total Points: {game_total}")
        print()
    
    # Calculate statistics
    avg_points = total_points / games_played if games_played > 0 else 0
    overtime_pct = (overtime_games / games_played) * 100 if games_played > 0 else 0
    
    print("📊 Results Summary:")
    print(f"   Games Played: {games_played}")
    print(f"   Average Points per Game: {avg_points:.1f}")
    print(f"   Overtime Games: {overtime_games} ({overtime_pct:.1f}%)")
    print()
    
    # Test quarter-ending scenarios specifically
    print("🕐 Testing Quarter-End Scenarios:")
    print("-" * 30)
    
    # Test with a game that might have quarter transitions
    engine = GameEngine(seed=999, enable_reporting=True, verbose=True)
    print("Running one game with detailed output to check quarter transitions...")
    result = engine.simulate_game(bills, dolphins)
    
    print(f"Final Result: {result.home_team.name} {result.home_score} - {result.away_team.name} {result.away_score}")
    
    if avg_points > 30:
        print("✅ Scoring looks improved!")
    else:
        print("⚠️  Scoring still seems low...")
    
    if overtime_pct < 25:
        print("✅ Overtime frequency looks reasonable!")
    else:
        print("⚠️  Still too many overtime games...")


if __name__ == "__main__":
    test_quarter_transitions()
