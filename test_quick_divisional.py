#!/usr/bin/env python3
"""
Quick test to check if divisional teams play each other twice.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.season_engine import SeasonEngine
from data.team_loader import load_sample_teams
from collections import defaultdict

def quick_test():
    # Load teams
    teams = load_sample_teams()
    print(f"🏈 Quick divisional test - {len(teams)} teams")
    
    # Create season
    season = SeasonEngine(teams, 2024)
    print(f"📅 Total games: {len(season.schedule)}")
    
    # Check AFC East specifically
    afc_east = [t for t in teams if t.conference == 'AFC' and t.division == 'East']
    print(f"🏟️ AFC East: {[t.abbreviation for t in afc_east]}")
    
    # Count matchups between AFC East teams
    afc_east_games = defaultdict(int)
    
    for game in season.schedule:
        home_team = game.home_team
        away_team = game.away_team
        
        if home_team in afc_east and away_team in afc_east:
            matchup_key = f"{home_team.abbreviation} vs {away_team.abbreviation}"
            afc_east_games[matchup_key] += 1
    
    print(f"📊 AFC East divisional games:")
    for matchup, count in afc_east_games.items():
        print(f"  {matchup}: {count} times")
    
    # Check total games for BUF
    buf_games = [g for g in season.schedule if g.home_team.abbreviation == 'BUF' or g.away_team.abbreviation == 'BUF']
    print(f"🎯 BUF total games: {len(buf_games)}")
    
    # Check BUF vs divisional opponents
    buf_divisional = 0
    for game in buf_games:
        opponent = game.away_team if game.home_team.abbreviation == 'BUF' else game.home_team
        if opponent in afc_east:
            buf_divisional += 1
    
    print(f"🎯 BUF divisional games: {buf_divisional}")
    
    return len(season.schedule)

if __name__ == "__main__":
    quick_test()
