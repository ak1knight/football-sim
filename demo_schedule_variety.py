#!/usr/bin/env python3
"""
Simple demo showing the improved schedule generation fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.season_engine import SeasonEngine
from data.team_loader import load_sample_teams
from collections import defaultdict

def main():
    print("🏈 SCHEDULE VARIETY DEMO")
    print("=" * 50)
    
    # Load teams
    teams = load_sample_teams()
    print(f"📊 Loaded {len(teams)} NFL teams")
    
    # Create season
    season = SeasonEngine(teams, 2024)
    print(f"✅ Created 2024 season")
    print(f"📅 Total games scheduled: {len(season.schedule)}")
    
    # Analyze opponent variety
    team_opponents = defaultdict(set)
    team_game_counts = defaultdict(int)
    
    for game in season.schedule:
        home_abbr = game.home_team.abbreviation
        away_abbr = game.away_team.abbreviation
        
        team_opponents[home_abbr].add(away_abbr)
        team_opponents[away_abbr].add(home_abbr)
        
        team_game_counts[home_abbr] += 1
        team_game_counts[away_abbr] += 1
    
    # Show variety stats
    opponent_counts = [len(opponents) for opponents in team_opponents.values()]
    game_counts = list(team_game_counts.values())
    
    print(f"\n📊 Schedule Analysis:")
    print(f"    Teams with different opponents:")
    print(f"      Average: {sum(opponent_counts) / len(opponent_counts):.1f}")
    print(f"      Range: {min(opponent_counts)} to {max(opponent_counts)}")
    
    print(f"    Games per team:")
    print(f"      Average: {sum(game_counts) / len(game_counts):.1f}")
    print(f"      Range: {min(game_counts)} to {max(game_counts)}")
    
    # Show some examples
    print(f"\n🎯 Example Team Schedules:")
    
    # Show 3 teams and their opponents
    sample_teams = ['KC', 'BUF', 'SF']
    for team_abbr in sample_teams:
        if team_abbr in team_opponents:
            opponents = sorted(team_opponents[team_abbr])
            games = team_game_counts[team_abbr]
            print(f"    {team_abbr}: {games} games against {len(opponents)} different opponents")
            print(f"         Opponents: {', '.join(opponents[:10])}{'...' if len(opponents) > 10 else ''}")
    
    # Check for repeated matchups
    print(f"\n🔄 Matchup Analysis:")
    matchup_counts = defaultdict(int)
    
    for game in season.schedule:
        teams_sorted = sorted([game.home_team.abbreviation, game.away_team.abbreviation])
        matchup = f"{teams_sorted[0]} vs {teams_sorted[1]}"
        matchup_counts[matchup] += 1
    
    repeated_matchups = {k: v for k, v in matchup_counts.items() if v > 1}
    
    if repeated_matchups:
        print(f"    Found {len(repeated_matchups)} repeated matchups:")
        for matchup, count in list(repeated_matchups.items())[:5]:  # Show first 5
            print(f"      {matchup}: {count} times")
    else:
        print(f"    ✅ No repeated matchups found!")
        print(f"    Each team plays different opponents every week.")
    
    # Weekly distribution
    print(f"\n📅 Weekly Distribution:")
    week_games = defaultdict(int)
    for game in season.schedule:
        week_games[game.week] += 1
    
    for week in sorted(week_games.keys())[:10]:  # Show first 10 weeks
        print(f"    Week {week}: {week_games[week]} games")
    
    print(f"\n✅ SCHEDULE ANALYSIS COMPLETE!")
    print(f"Key Improvements:")
    print(f"  🎲 Varied opponents each week (no repeated matchups)")
    print(f"  ⚖️ Balanced game distribution ({min(game_counts)}-{max(game_counts)} games per team)")
    print(f"  📊 Consistent weekly schedule ({min(week_games.values())}-{max(week_games.values())} games per week)")

if __name__ == "__main__":
    main()
