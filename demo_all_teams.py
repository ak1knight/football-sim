#!/usr/bin/env python3
"""
Demo script to showcase all 32 NFL teams in the simulation engine.

This script demonstrates balanced gameplay across different team tiers
and divisions, showing realistic score distributions.
"""

import random
from collections import defaultdict
from data.team_loader import load_sample_teams
from simulation.game_engine import GameEngine


def main():
    """Run simulations with all 32 NFL teams to test balance."""
    
    print("Football Simulation Engine - All 32 Teams Demo")
    print("=" * 60)
    
    # Load all teams
    teams = load_sample_teams()
    print(f"Loaded {len(teams)} NFL teams")
    
    # Organize teams by conference and division
    conferences = defaultdict(lambda: defaultdict(list))
    for team in teams:
        conferences[team.conference][team.division].append(team)
    
    print("\nTeam Organization:")
    for conf in sorted(conferences.keys()):
        print(f"\n{conf} Conference:")
        for div in sorted(conferences[conf].keys()):
            print(f"  {div} Division:")
            for team in sorted(conferences[conf][div], key=lambda t: t.name):
                rating = (team.stats.offensive_rating + team.stats.defensive_rating) / 2
                print(f"    {team.city} {team.name} (Overall: {rating:.1f})")
    
    # Test divisional matchups
    print(f"\n{'='*60}")
    print("DIVISIONAL MATCHUP SIMULATIONS")
    print("=" * 60)
    
    # Simulate some classic divisional rivalries
    rivalry_games = [
        # AFC East
        ("New England Patriots", "Buffalo Bills"),
        ("New York Jets", "Miami Dolphins"),
        
        # AFC North  
        ("Pittsburgh Steelers", "Baltimore Ravens"),
        ("Cincinnati Bengals", "Cleveland Browns"),
        
        # AFC South
        ("Houston Texans", "Indianapolis Colts"),
        ("Jacksonville Jaguars", "Tennessee Titans"),
        
        # AFC West
        ("Kansas City Chiefs", "Denver Broncos"),
        ("Las Vegas Raiders", "Los Angeles Chargers"),
        
        # NFC East
        ("Dallas Cowboys", "Philadelphia Eagles"),
        ("New York Giants", "Washington Commanders"),
        
        # NFC North
        ("Green Bay Packers", "Chicago Bears"),
        ("Detroit Lions", "Minnesota Vikings"),
        
        # NFC South
        ("New Orleans Saints", "Atlanta Falcons"),
        ("Tampa Bay Buccaneers", "Carolina Panthers"),
        
        # NFC West
        ("San Francisco 49ers", "Seattle Seahawks"),
        ("Los Angeles Rams", "Arizona Cardinals"),
    ]
    
    # Create team lookup
    team_lookup = {}
    for team in teams:
        team_lookup[f"{team.city} {team.name}"] = team
        team_lookup[team.name] = team  # Also allow lookup by just name
    
    scores = []
    results_summary = defaultdict(int)
    
    for away_name, home_name in rivalry_games:
        # Find teams
        away_team = team_lookup.get(away_name)
        home_team = team_lookup.get(home_name)
        
        if not away_team or not home_team:
            print(f"Warning: Could not find teams {away_name} vs {home_name}")
            continue
        
        # Create engine with random seed
        engine = GameEngine(seed=random.randint(1, 100000))
        result = engine.simulate_game(home_team, away_team)
        
        # Track results
        scores.append((result.away_score, result.home_score))
        total_points = result.away_score + result.home_score
        
        if total_points < 20:
            results_summary["Low Scoring (< 20)"] += 1
        elif total_points < 35:
            results_summary["Moderate Scoring (20-34)"] += 1
        elif total_points < 50:
            results_summary["High Scoring (35-49)"] += 1
        else:
            results_summary["Very High Scoring (50+)"] += 1
        
        # Display result
        winner_text = f"{result.winner.city} {result.winner.name}" if result.winner else "TIE"
        print(f"{away_team.city} {away_team.name} @ {home_team.city} {home_team.name}")
        print(f"  Final: {result.away_score} - {result.home_score} (Winner: {winner_text})")
    
    # Show statistics
    print(f"\n{'='*60}")
    print("SIMULATION STATISTICS")
    print("=" * 60)
    
    if scores:
        total_games = len(scores)
        total_points = sum(away + home for away, home in scores)
        avg_points_per_game = total_points / total_games
        
        away_scores = [score[0] for score in scores]
        home_scores = [score[1] for score in scores]
        
        print(f"Games Simulated: {total_games}")
        print(f"Average Points per Game: {avg_points_per_game:.1f}")
        print(f"Average Away Score: {sum(away_scores) / len(away_scores):.1f}")
        print(f"Average Home Score: {sum(home_scores) / len(home_scores):.1f}")
        print(f"Highest Scoring Game: {max(away + home for away, home in scores)} points")
        print(f"Lowest Scoring Game: {min(away + home for away, home in scores)} points")
        
        print(f"\nScore Distribution:")
        for category, count in results_summary.items():
            percentage = (count / total_games) * 100
            print(f"  {category}: {count} games ({percentage:.1f}%)")
    
    # Test team strength differences
    print(f"\n{'='*60}")
    print("TEAM STRENGTH ANALYSIS")
    print("=" * 60)
    
    # Find strongest and weakest teams by overall rating
    team_ratings = []
    for team in teams:
        overall_rating = (team.stats.offensive_rating + team.stats.defensive_rating) / 2
        team_ratings.append((team, overall_rating))
    
    team_ratings.sort(key=lambda x: x[1], reverse=True)
    
    print("Strongest Teams (Top 5):")
    for i, (team, rating) in enumerate(team_ratings[:5]):
        print(f"  {i+1}. {team.city} {team.name} - {rating:.1f}")
    
    print("\nWeakest Teams (Bottom 5):")
    for i, (team, rating) in enumerate(team_ratings[-5:]):
        rank = len(team_ratings) - 4 + i
        print(f"  {rank}. {team.city} {team.name} - {rating:.1f}")
    
    # Test strong vs weak matchup
    strongest_team = team_ratings[0][0]
    weakest_team = team_ratings[-1][0]
    
    print(f"\nStrong vs Weak Team Test:")
    print(f"{weakest_team.city} {weakest_team.name} @ {strongest_team.city} {strongest_team.name}")
    
    engine = GameEngine(seed=42)  # Fixed seed for reproducible result
    result = engine.simulate_game(strongest_team, weakest_team)
    
    winner_text = f"{result.winner.city} {result.winner.name}" if result.winner else "TIE"
    print(f"Result: {result.away_score} - {result.home_score} (Winner: {winner_text})")
    
    if result.winner == strongest_team:
        print("✓ Stronger team won as expected")
    elif result.winner == weakest_team:
        print("! Upset victory by weaker team (this can happen in football!)")
    else:
        print("- Game ended in a tie")


if __name__ == "__main__":
    main()
