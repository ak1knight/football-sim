#!/usr/bin/env python3
"""
Test script for playoff functionality.

This script tests the complete playoff system by simulating a season
through to completion and then running the playoffs.
"""

import sys
import os
import random

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.team_loader import load_sample_teams
from simulation.season_engine import SeasonEngine
from simulation.game_engine import GameEngine


def test_playoffs():
    """Test the complete playoff system."""
    print("🏈 Testing NFL Playoffs System")
    print("=" * 50)
    
    # Load teams and create season
    teams = load_sample_teams()
    print(f"✓ Loaded {len(teams)} teams")
    
    # Create season with fixed seed for reproducible results
    season = SeasonEngine(teams, season_year=2024, seed=42)
    print(f"✓ Created {season.season_year} season")
    print(f"  - Total games: {len(season.schedule)}")
    print(f"  - Current phase: {season.current_phase.value}")
    print()
    
    # Simulate the entire regular season
    print("📅 Simulating Regular Season...")
    game_engine = GameEngine(seed=42)
    games_simulated = 0
    
    for week in range(1, 19):  # Weeks 1-18
        week_games = season.get_week_games(week)
        print(f"  Week {week}: {len(week_games)} games")
        
        for game in week_games:
            if game.status.value == 'scheduled':
                # Simulate the game
                result = game_engine.simulate_game(game.home_team, game.away_team)
                
                # Process the result
                season.process_game_result(
                    game.game_id,
                    result.home_score,
                    result.away_score,
                    result.duration > 60,
                    result.duration
                )
                games_simulated += 1
    
    print(f"✓ Simulated {games_simulated} regular season games")
    print(f"  - Current phase: {season.current_phase.value}")
    print()
    
    # Check if playoffs were initialized
    if season.playoff_engine is None:
        print("❌ Playoffs not initialized!")
        return
    
    print("🏆 Playoffs Initialized!")
    bracket = season.get_playoff_bracket()
    
    if not bracket:
        print("❌ No playoff bracket found!")
        return
    
    print(f"  - Current round: {bracket['current_round']}")
    print(f"  - AFC playoff teams: {len(bracket['afc_teams'])}")
    print(f"  - NFC playoff teams: {len(bracket['nfc_teams'])}")
    print()
    
    # Display playoff teams
    print("AFC Playoff Teams:")
    for team in bracket['afc_teams']:
        status = "Division Winner" if team['division_winner'] else "Wild Card"
        print(f"  {team['seed']}. {team['team']['city']} {team['team']['name']} ({team['record']}) - {status}")
    
    print("\nNFC Playoff Teams:")
    for team in bracket['nfc_teams']:
        status = "Division Winner" if team['division_winner'] else "Wild Card"
        print(f"  {team['seed']}. {team['team']['city']} {team['team']['name']} ({team['record']}) - {status}")
    print()
    
    # Simulate playoffs
    print("🎯 Simulating Playoffs...")
    playoff_games_simulated = 0
    
    while not season.is_season_complete():
        next_games = season.get_next_playoff_games()
        
        if not next_games:
            break
        
        current_round = next_games[0]['round'] if next_games else "unknown"
        print(f"\n--- {current_round.replace('_', ' ').title()} Round ---")
        
        for game_data in next_games:
            if game_data['is_ready_to_play']:
                # Find the teams for simulation
                home_team = None
                away_team = None
                
                for team in teams:
                    if team.abbreviation == game_data['home_team']['abbreviation']:
                        home_team = team
                    elif team.abbreviation == game_data['away_team']['abbreviation']:
                        away_team = team
                
                if home_team and away_team:
                    # Simulate playoff game
                    result = game_engine.simulate_game(home_team, away_team)
                    
                    # Process result
                    success = season.process_playoff_game_result(
                        game_data['game_id'],
                        result.home_score,
                        result.away_score,
                        result.duration > 60
                    )
                    
                    if success:
                        winner = "Home" if result.home_score > result.away_score else "Away"
                        print(f"  {game_data['matchup_description']}: {result.home_score}-{result.away_score} ({winner} wins)")
                        playoff_games_simulated += 1
    
    print(f"\n✓ Simulated {playoff_games_simulated} playoff games")
    
    # Display final results
    final_bracket = season.get_playoff_bracket()
    if final_bracket:
        print("\n🏆 FINAL RESULTS:")
        
        if final_bracket.get('afc_champion'):
            afc_champ = final_bracket['afc_champion']
            print(f"  AFC Champion: {afc_champ['team']['city']} {afc_champ['team']['name']} ({afc_champ['seed']} seed)")
        
        if final_bracket.get('nfc_champion'):
            nfc_champ = final_bracket['nfc_champion']
            print(f"  NFC Champion: {nfc_champ['team']['city']} {nfc_champ['team']['name']} ({nfc_champ['seed']} seed)")
        
        if final_bracket.get('super_bowl_champion'):
            sb_champ = final_bracket['super_bowl_champion']
            print(f"  🏆 SUPER BOWL CHAMPION: {sb_champ['team']['city']} {sb_champ['team']['name']} ({sb_champ['seed']} seed)")
        
        print(f"  Season complete: {final_bracket['is_complete']}")
    
    print("\n🎉 Playoff test completed successfully!")


if __name__ == "__main__":
    try:
        test_playoffs()
    except Exception as e:
        print(f"❌ Error during playoff test: {e}")
        import traceback
        traceback.print_exc()