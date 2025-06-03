#!/usr/bin/env python3
"""
American Football Simulation Engine

This module provides the main entry point for running football simulations.
It demonstrates how to use the simulation engine to run a game between two teams.
"""

from models.team import Team
from models.player import Player
from simulation.game_engine import GameEngine
from data.team_loader import load_sample_teams
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to demonstrate the football simulation."""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Football Simulation Engine")
    
    # Load sample teams
    teams = load_sample_teams()
    
    if len(teams) < 2:
        logger.error("Need at least 2 teams to run a simulation")
        return
    
    # Select two teams for simulation
    home_team = teams[0]
    away_team = teams[1]
    
    logger.info(f"Home Team: {home_team.name}")
    logger.info(f"Away Team: {away_team.name}")
    
    # Create and run the game simulation
    game_engine = GameEngine()
    result = game_engine.simulate_game(home_team, away_team)
    
    # Display results
    print("\n" + "="*50)
    print("GAME RESULT")
    print("="*50)
    print(f"{result.away_team.name}: {result.away_score}")
    print(f"{result.home_team.name}: {result.home_score}")
    
    if result.home_score > result.away_score:
        print(f"\nWinner: {result.home_team.name}")
    elif result.away_score > result.home_score:
        print(f"\nWinner: {result.away_team.name}")
    else:
        print("\nGame ended in a tie!")
    
    print(f"\nGame Duration: {result.duration} minutes")
    print("="*50)

if __name__ == "__main__":
    main()
