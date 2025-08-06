#!/usr/bin/env python3
"""
Test script for season simulation endpoints.

This script demonstrates how the season simulation API works
by creating a season and running a few simulated games.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.season_api import SeasonAPI
from api.simulation_api import SimulationAPI
from simulation.game_engine import GameEngine

def test_season_simulation():
    """Test the complete season simulation workflow."""
    
    print("🏈 Football Season Simulation Test")
    print("=" * 50)
    
    # Initialize the season API
    season_api = SeasonAPI()
    game_engine = GameEngine()
    
    # Create a new season
    print("\n1. Creating new season...")
    season_result = season_api.create_season(season_year=2024, seed=12345)
    
    if season_result['success']:
        print(f"✅ Season created successfully!")
        print(f"   - Total teams: {season_result['total_teams']}")
        print(f"   - Total games: {season_result['total_games']}")
        print(f"   - Current week: {season_result['season_status']['current_week']}")
    else:
        print(f"❌ Failed to create season: {season_result['error']}")
        return
    
    # Get season status
    print("\n2. Getting season status...")
    status = season_api.get_season_status()
    if status['success']:
        s = status['season_status']
        print(f"✅ Season Status:")
        print(f"   - Year: {s['season_year']}")
        print(f"   - Current Week: {s['current_week']}")
        print(f"   - Phase: {s['current_phase']}")
        print(f"   - Games Completed: {s['completed_games']}/{s['total_games']}")
        print(f"   - Progress: {s['completion_percentage']}%")
    
    # Get next games to simulate
    print("\n3. Getting next games...")
    next_games = season_api.get_next_games(limit=4)
    if next_games['success']:
        print(f"✅ Found {next_games['count']} games ready to simulate")
        
        # Simulate a few games
        print("\n4. Simulating games...")
        for i, game_data in enumerate(next_games['games'][:2]):
            game_id = game_data['game_id']
            home_team = game_data['home_team']['name']
            away_team = game_data['away_team']['name']
            
            print(f"\n   Simulating Game {i+1}: {away_team} @ {home_team}")
            
            # Find the actual team objects for simulation
            home_team_obj = None
            away_team_obj = None
            
            for team in season_api.teams:
                if team.abbreviation == game_data['home_team']['abbreviation']:
                    home_team_obj = team
                if team.abbreviation == game_data['away_team']['abbreviation']:
                    away_team_obj = team
            
            if home_team_obj and away_team_obj:
                # Simulate the game
                result = game_engine.simulate_game(home_team_obj, away_team_obj)
                
                # Submit result to season
                submit_result = season_api.submit_game_result(
                    game_id=game_id,
                    home_score=result.home_score,
                    away_score=result.away_score,
                    overtime=result.duration > 60,
                    game_duration=result.duration
                )
                
                if submit_result['success']:
                    print(f"   ✅ {away_team} {result.away_score} - {result.home_score} {home_team}")
                    if result.winner:
                        print(f"      Winner: {result.winner.name}")
                else:
                    print(f"   ❌ Failed to submit result: {submit_result['error']}")
    
    # Get standings
    print("\n5. Getting current standings...")
    standings = season_api.get_standings(by_division=True)
    if standings['success']:
        print("✅ Current Standings (by Division):")
        for division, teams in standings['standings'].items():
            print(f"\n   {division}:")
            for i, team in enumerate(teams[:3]):  # Show top 3 in each division
                record = f"{team['wins']}-{team['losses']}-{team['ties']}"
                pct = team['win_percentage']
                print(f"     {i+1}. {team['team']['city']} {team['team']['name']} ({record}, {pct})")
    
    # Get updated season status
    print("\n6. Final season status...")
    final_status = season_api.get_season_status()
    if final_status['success']:
        s = final_status['season_status']
        print(f"✅ Updated Status:")
        print(f"   - Current Week: {s['current_week']}")
        print(f"   - Games Completed: {s['completed_games']}/{s['total_games']}")
        print(f"   - Progress: {s['completion_percentage']}%")
    
    print("\n🎉 Season simulation test completed successfully!")
    print("\nThe season simulation system is ready for frontend integration.")


if __name__ == "__main__":
    test_season_simulation()