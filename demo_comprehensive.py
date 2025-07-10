#!/usr/bin/env python3
"""
Comprehensive demo showing the improved football simulation system.
This demonstrates the enhanced features: time-based quarters, proper touchdown detection,
balanced scoring, and robust season management.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.season_engine import SeasonEngine
from simulation.game_engine import GameEngine
from data.team_loader import load_sample_teams
from models.weather import Weather, WeatherCondition, WindDirection
import random

def main():
    print("🏈 ENHANCED FOOTBALL SIMULATION DEMO")
    print("=" * 60)
    
    # Load teams
    teams = load_sample_teams()
    print(f"📊 Loaded {len(teams)} NFL teams")
    
    # Test 1: Individual Game Simulation
    print("\n🎮 TEST 1: Individual Game Simulation")
    print("-" * 40)
    
    # Pick two teams
    chiefs = next(t for t in teams if t.abbreviation == "KC")
    bills = next(t for t in teams if t.abbreviation == "BUF")
    
    print(f"Game: {bills.city} {bills.name} @ {chiefs.city} {chiefs.name}")
    
    # Create game engine
    game_engine = GameEngine()
    
    # Simulate with different weather conditions
    weather_conditions = [
        Weather(WeatherCondition.CLEAR, 72, 5, WindDirection.NONE, 0),
        Weather(WeatherCondition.LIGHT_RAIN, 45, 15, WindDirection.CROSSWIND, 0.3),
        Weather(WeatherCondition.LIGHT_SNOW, 28, 20, WindDirection.HEADWIND, 0.8)
    ]
    
    for i, weather in enumerate(weather_conditions, 1):
        print(f"\n  Simulation {i} - Weather: {weather.condition.value}")
        print(f"    Temperature: {weather.temperature}°F, Wind: {weather.wind_speed}mph")
        
        result = game_engine.simulate_game(bills, chiefs, weather=weather)
        
        print(f"    Final Score: {result.away_team.name} {result.away_score} - {result.home_score} {result.home_team.name}")
        print(f"    Winner: {result.winner.name if result.winner else 'TIE'}")
        print(f"    Total Plays: {len(result.play_log)}")
        
        # Show some key stats
        quarters = [0, 0, 0, 0]  # Track scoring by quarter
        for play in result.play_log:
            if 'TOUCHDOWN' in play or 'FIELD GOAL' in play:
                quarter = 1 if 'Q1' in play else 2 if 'Q2' in play else 3 if 'Q3' in play else 4
                quarters[quarter-1] += 1
        
        print(f"    Scoring plays by quarter: Q1:{quarters[0]}, Q2:{quarters[1]}, Q3:{quarters[2]}, Q4:{quarters[3]}")
    
    # Test 2: Season Management
    print("\n🏆 TEST 2: Season Management")
    print("-" * 40)
    
    # Create season
    season = SeasonEngine(teams, 2024)
    print(f"✅ Created 2024 season with {len(season.teams)} teams")
    print(f"📅 Total games scheduled: {len(season.schedule)}")
    
    # Show schedule variety
    team_opponents = {}
    for game in season.schedule:
        home_abbr = game.home_team.abbreviation
        away_abbr = game.away_team.abbreviation
        
        if home_abbr not in team_opponents:
            team_opponents[home_abbr] = set()
        if away_abbr not in team_opponents:
            team_opponents[away_abbr] = set()
        
        team_opponents[home_abbr].add(away_abbr)
        team_opponents[away_abbr].add(home_abbr)
    
    # Show variety stats
    opponent_counts = [len(opponents) for opponents in team_opponents.values()]
    avg_opponents = sum(opponent_counts) / len(opponent_counts)
    min_opponents = min(opponent_counts)
    max_opponents = max(opponent_counts)
    
    print(f"📊 Schedule variety:")
    print(f"    Average opponents per team: {avg_opponents:.1f}")
    print(f"    Range: {min_opponents} to {max_opponents} different opponents")
    
    # Simulate a few weeks
    print(f"\n🎯 Simulating first 4 weeks...")
    
    for week in range(1, 5):
        games_this_week = season.get_games_for_week(week)
        print(f"  Week {week}: {len(games_this_week)} games")
        
        # Simulate each game
        for game in games_this_week:
            weather = Weather(
                random.choice(list(WeatherCondition)),
                random.randint(20, 85),
                random.randint(0, 25),
                random.choice(list(WindDirection)),
                random.random() * 0.5
            )
            
            result = game_engine.simulate_game(game.away_team, game.home_team, weather=weather)
            season.submit_game_result(game.game_id, result)
    
    # Show standings
    print(f"\n📊 Standings after 4 weeks:")
    standings = season.get_standings()
    
    # Show AFC East and NFC East
    afc_east = [team for team in standings if team.division == 'East' and team.conference == 'AFC']
    nfc_east = [team for team in standings if team.division == 'East' and team.conference == 'NFC']
    
    print(f"  AFC East:")
    for i, team in enumerate(afc_east, 1):
        wins = season.team_records[team.abbreviation]['wins']
        losses = season.team_records[team.abbreviation]['losses']
        pct = wins / (wins + losses) if (wins + losses) > 0 else 0
        print(f"    {i}. {team.name} ({wins}-{losses}, {pct:.3f})")
    
    print(f"  NFC East:")
    for i, team in enumerate(nfc_east, 1):
        wins = season.team_records[team.abbreviation]['wins']
        losses = season.team_records[team.abbreviation]['losses']
        pct = wins / (wins + losses) if (wins + losses) > 0 else 0
        print(f"    {i}. {team.name} ({wins}-{losses}, {pct:.3f})")
    
    # Test 3: Scoring Analysis
    print("\n🎯 TEST 3: Scoring Analysis")
    print("-" * 40)
    
    # Analyze scoring from completed games
    all_scores = []
    overtime_games = 0
    
    for game_id, result in season.completed_games.items():
        home_score = result.home_score
        away_score = result.away_score
        total_score = home_score + away_score
        all_scores.append(total_score)
        
        if result.overtime:
            overtime_games += 1
    
    if all_scores:
        avg_total_score = sum(all_scores) / len(all_scores)
        min_score = min(all_scores)
        max_score = max(all_scores)
        
        print(f"📊 Scoring statistics from {len(all_scores)} games:")
        print(f"    Average total score: {avg_total_score:.1f}")
        print(f"    Score range: {min_score} to {max_score}")
        print(f"    Overtime games: {overtime_games} ({overtime_games/len(all_scores)*100:.1f}%)")
    
    # Test 4: Quarter System
    print("\n⏰ TEST 4: Quarter System Analysis")
    print("-" * 40)
    
    # Run a single game and analyze quarter progression
    patriots = next(t for t in teams if t.abbreviation == "NE")
    dolphins = next(t for t in teams if t.abbreviation == "MIA")
    
    print(f"Detailed game analysis: {patriots.name} @ {dolphins.name}")
    
    weather = Weather(WeatherCondition.CLEAR, 75, 8, WindDirection.NONE, 0)
    result = game_engine.simulate_game(patriots, dolphins, weather=weather)
    
    print(f"Final Score: {result.away_team.name} {result.away_score} - {result.home_score} {result.home_team.name}")
    
    # Analyze quarter progression
    quarter_scores = {'Q1': [0, 0], 'Q2': [0, 0], 'Q3': [0, 0], 'Q4': [0, 0]}
    
    for play in result.play_log:
        if 'TOUCHDOWN' in play or 'FIELD GOAL' in play:
            quarter = 'Q1' if 'Q1' in play else 'Q2' if 'Q2' in play else 'Q3' if 'Q3' in play else 'Q4'
            if result.away_team.abbreviation in play:
                quarter_scores[quarter][0] += 7 if 'TOUCHDOWN' in play else 3
            else:
                quarter_scores[quarter][1] += 7 if 'TOUCHDOWN' in play else 3
    
    print(f"Quarter-by-quarter scoring:")
    for quarter, (away_pts, home_pts) in quarter_scores.items():
        print(f"  {quarter}: {result.away_team.abbreviation} {away_pts} - {home_pts} {result.home_team.abbreviation}")
    
    print(f"\n✅ DEMO COMPLETE - Key Improvements Demonstrated:")
    print("   🕐 Time-based quarters (15 minutes each)")
    print("   🏈 Proper touchdown detection and scoring")
    print("   📊 Balanced scoring (reduced overtime)")
    print("   🏆 Robust season management")
    print("   🎲 Varied opponent scheduling")
    print("   🌤️ Weather impact on gameplay")
    print("   📈 Comprehensive statistics tracking")

if __name__ == "__main__":
    main()
