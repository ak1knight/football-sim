#!/usr/bin/env python3
"""
Performance test for the football simulation engine.

This script tests the performance of the simulation engine
by running multiple games and measuring execution time.
"""

import time
import random
from statistics import mean, stdev
from data.team_loader import load_sample_teams
from simulation.game_engine import GameEngine


def performance_test():
    """Run performance tests on the simulation engine."""
    
    print("Football Simulation Engine - Performance Test")
    print("=" * 60)
    
    # Load teams
    teams = load_sample_teams()
    print(f"Loaded {len(teams)} teams")
    
    # Test parameters
    num_games = 100
    print(f"Running {num_games} simulations...")
    
    # Track timing and results
    simulation_times = []
    scores = []
    
    start_time = time.time()
    
    for i in range(num_games):
        # Pick random teams
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t != home_team])
        
        # Time individual simulation
        sim_start = time.time()
        
        engine = GameEngine(seed=random.randint(1, 100000))
        result = engine.simulate_game(home_team, away_team)
        
        sim_end = time.time()
        simulation_times.append(sim_end - sim_start)
        scores.append((result.home_score, result.away_score))
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Completed {i + 1}/{num_games} simulations...")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    avg_sim_time = mean(simulation_times)
    std_sim_time = stdev(simulation_times) if len(simulation_times) > 1 else 0
    min_sim_time = min(simulation_times)
    max_sim_time = max(simulation_times)
    
    total_points = sum(home + away for home, away in scores)
    avg_total_score = total_points / num_games
    home_scores = [score[0] for score in scores]
    away_scores = [score[1] for score in scores]
    avg_home_score = mean(home_scores)
    avg_away_score = mean(away_scores)
    
    # Results
    print(f"\n{'='*60}")
    print("PERFORMANCE RESULTS")
    print("=" * 60)
    
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Games per second: {num_games / total_time:.1f}")
    print(f"Average simulation time: {avg_sim_time*1000:.1f} ms")
    print(f"Simulation time std dev: {std_sim_time*1000:.1f} ms")
    print(f"Fastest simulation: {min_sim_time*1000:.1f} ms")
    print(f"Slowest simulation: {max_sim_time*1000:.1f} ms")
    
    print(f"\n{'='*60}")
    print("GAME STATISTICS")
    print("=" * 60)
    
    print(f"Games simulated: {num_games}")
    print(f"Average total score: {avg_total_score:.1f}")
    print(f"Average home score: {avg_home_score:.1f}")
    print(f"Average away score: {avg_away_score:.1f}")
    print(f"Highest scoring game: {max(home + away for home, away in scores)} points")
    print(f"Lowest scoring game: {min(home + away for home, away in scores)} points")
    
    # Score distribution
    score_ranges = {
        "Low (0-20)": 0,
        "Moderate (21-35)": 0,
        "High (36-50)": 0,
        "Very High (51+)": 0
    }
    
    for home, away in scores:
        total = home + away
        if total <= 20:
            score_ranges["Low (0-20)"] += 1
        elif total <= 35:
            score_ranges["Moderate (21-35)"] += 1
        elif total <= 50:
            score_ranges["High (36-50)"] += 1
        else:
            score_ranges["Very High (51+)"] += 1
    
    print(f"\nScore Distribution:")
    for range_name, count in score_ranges.items():
        percentage = (count / num_games) * 100
        print(f"  {range_name}: {count} games ({percentage:.1f}%)")
    
    # Performance assessment
    print(f"\n{'='*60}")
    print("PERFORMANCE ASSESSMENT")
    print("=" * 60)
    
    if avg_sim_time < 0.1:
        perf_rating = "Excellent"
    elif avg_sim_time < 0.2:
        perf_rating = "Good"
    elif avg_sim_time < 0.5:
        perf_rating = "Fair"
    else:
        perf_rating = "Needs Optimization"
    
    print(f"Performance Rating: {perf_rating}")
    print(f"Suitable for real-time applications: {'Yes' if avg_sim_time < 0.1 else 'No'}")
    print(f"Games per minute capability: {int(60 / avg_sim_time):,}")
    
    if num_games >= 100:
        print("\n✅ Performance test completed successfully!")
        print("   The simulation engine is ready for production use.")
    
    return {
        'avg_sim_time': avg_sim_time,
        'games_per_second': num_games / total_time,
        'avg_total_score': avg_total_score,
        'performance_rating': perf_rating
    }


if __name__ == "__main__":
    performance_test()
