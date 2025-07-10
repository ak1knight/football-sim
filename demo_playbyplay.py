#!/usr/bin/env python3
"""
Demo script for play-by-play reporting in the football simulation engine.

This script demonstrates the detailed reporting capabilities of the simulation,
including drive summaries and play-by-play narratives.
"""

import logging
from data.team_loader import load_sample_teams
from simulation.game_engine import GameEngine

def main():
    """Run a demo game with detailed play-by-play reporting."""
    
    # Configure logging for less verbose output
    logging.basicConfig(
        level=logging.WARNING,  # Only show warnings and errors
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Football Simulation Engine - Play-by-Play Demo")
    print("=" * 60)
    
    # Load teams
    teams = load_sample_teams()
    home_team = teams[0]  # Eagles
    away_team = teams[1]  # Cowboys
    
    print(f"Today's matchup: {away_team.name} @ {home_team.name}")
    print()
    
    # Create game engine with reporting enabled
    game_engine = GameEngine(
        seed=42,  # For reproducible results
        enable_reporting=True,
        verbose=True  # Enable detailed console output
    )
    
    # Simulate the game
    print("Starting simulation with play-by-play reporting...")
    print()
    
    result = game_engine.simulate_game(home_team, away_team)
    
    # Print additional summaries
    print("\n" + "=" * 60)
    print("GAME SUMMARY")
    print("=" * 60)
    if game_engine.reporter is not None:
        print(game_engine.reporter.get_game_summary())
    else:
        print("No game summary available (reporter not enabled).")
    
    print("\n" + "=" * 60)
    print("DRIVE SUMMARY")
    print("=" * 60)
    if game_engine.reporter is not None:
        print(game_engine.reporter.get_drive_summary())
    else:
        print("No drive summary available (reporter not enabled).")
    
    # Show final result
    winner = result.winner
    if winner:
        print(f"\n🏆 Winner: {winner.name}")
    else:
        print(f"\n🤝 Game ended in a tie: {result.home_score}-{result.away_score}")
    
    print(f"Game duration: {result.duration} minutes")

if __name__ == "__main__":
    main()
