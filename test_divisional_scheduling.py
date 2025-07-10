#!/usr/bin/env python3
"""
Test script to verify NFL divisional scheduling rules.
This checks that divisional teams play each other twice (home and away).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.season_engine import SeasonEngine
from data.team_loader import load_sample_teams
from collections import defaultdict

def test_divisional_matchups():
    """Test that divisional teams play each other twice."""
    
    # Load teams
    teams = load_sample_teams()
    print("🏈 NFL DIVISIONAL SCHEDULING TEST")
    print("=" * 50)
    print(f"📊 Loaded {len(teams)} teams")
    
    # Create season
    season = SeasonEngine(teams, 2024)
    print(f"📅 Total games scheduled: {len(season.schedule)}")
    
    # Organize teams by division
    divisions = defaultdict(list)
    for team in teams:
        division_key = f"{team.conference} {team.division}"
        divisions[division_key].append(team)
    
    print(f"🏟️ Found {len(divisions)} divisions:")
    for div_name, div_teams in divisions.items():
        print(f"  {div_name}: {len(div_teams)} teams ({', '.join(t.abbreviation for t in div_teams)})")
    
    # Check divisional matchups
    print(f"\n🔍 Checking divisional matchups...")
    
    # For each division, check if teams play each other twice
    total_divisional_games = 0
    
    for div_name, div_teams in divisions.items():
        print(f"\n📍 {div_name} Division:")
        
        # Create a matrix of games between divisional teams
        matchup_matrix = defaultdict(int)
        
        for game in season.schedule:
            home_team = game.home_team
            away_team = game.away_team
            
            # Check if both teams are in this division
            if home_team in div_teams and away_team in div_teams:
                # Create a consistent matchup key
                teams_sorted = sorted([home_team.abbreviation, away_team.abbreviation])
                matchup_key = f"{teams_sorted[0]} vs {teams_sorted[1]}"
                matchup_matrix[matchup_key] += 1
                total_divisional_games += 1
        
        # Check if each team plays every other team in division twice
        expected_matchups = len(div_teams) * (len(div_teams) - 1) // 2  # Each pair once
        expected_games = expected_matchups * 2  # Each pair twice (home and away)
        
        print(f"  Expected matchups: {expected_matchups} (each twice = {expected_games} games)")
        print(f"  Actual games found: {len(matchup_matrix)}")
        
        # Show the actual matchups
        for matchup, count in matchup_matrix.items():
            status = "✅" if count == 2 else "❌"
            print(f"    {status} {matchup}: {count} time(s)")
        
        if len(matchup_matrix) == expected_matchups:
            all_twice = all(count == 2 for count in matchup_matrix.values())
            if all_twice:
                print(f"  ✅ Perfect! All divisional teams play each other twice")
            else:
                print(f"  ❌ Some teams don't play each other twice")
        else:
            print(f"  ❌ Missing divisional matchups")
    
    print(f"\n📊 Summary:")
    print(f"  Total divisional games: {total_divisional_games}")
    print(f"  Expected divisional games: {8 * 6 * 4} (8 divisions × 6 games per team × 4 teams ÷ 2)")
    
    # Check individual team schedules
    print(f"\n🎯 Sample Team Analysis:")
    
    # Check a few teams from different divisions
    sample_teams = ['KC', 'BUF', 'SF', 'DAL']
    
    for team_abbr in sample_teams:
        team = next((t for t in teams if t.abbreviation == team_abbr), None)
        if not team:
            continue
            
        # Find team's division
        team_division = None
        for div_name, div_teams in divisions.items():
            if team in div_teams:
                team_division = div_name
                break
        
        if not team_division:
            continue
            
        print(f"\n  {team_abbr} ({team_division}):")
        
        # Find games against divisional opponents
        div_opponents = defaultdict(int)
        total_games = 0
        
        for game in season.schedule:
            if game.home_team == team or game.away_team == team:
                total_games += 1
                opponent = game.away_team if game.home_team == team else game.home_team
                
                # Check if opponent is in same division
                if opponent in divisions[team_division]:
                    div_opponents[opponent.abbreviation] += 1
        
        print(f"    Total games: {total_games}")
        print(f"    Divisional opponents:")
        for opp_abbr, count in div_opponents.items():
            status = "✅" if count == 2 else "❌"
            print(f"      {status} vs {opp_abbr}: {count} time(s)")
    
    print(f"\n✅ Divisional scheduling analysis complete!")

if __name__ == "__main__":
    test_divisional_matchups()
