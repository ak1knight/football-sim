#!/usr/bin/env python3
"""
Weather Effects Demo for Football Simulation Engine

This script demonstrates the impact of weather conditions on gameplay,
showing how different weather affects game outcomes, statistics, and play results.
"""

import random
from typing import List, Dict, Any
from data.team_loader import load_sample_teams
from simulation.game_engine import GameEngine
from models.weather import Weather, WeatherCondition, WindDirection, generate_random_weather

def demo_weather_effects():
    """Demonstrate weather effects on football gameplay."""
    print("🌤️  Football Simulation Engine - Weather Effects Demo")
    print("=" * 65)
    
    # Load teams
    teams = load_sample_teams()
    home_team = next(team for team in teams if team.name == "Chiefs")  # Strong offensive team
    away_team = next(team for team in teams if team.name == "49ers")  # Strong defensive team
    
    print(f"Matchup: {away_team.city} {away_team.name} @ {home_team.city} {home_team.name}")
    print()
    
    # Define various weather conditions to test
    weather_scenarios = [
        Weather(
            condition=WeatherCondition.CLEAR,
            temperature=72,
            wind_speed=5,
            wind_direction=WindDirection.NONE,
            precipitation_intensity=0.0
        ),
        Weather(
            condition=WeatherCondition.HEAVY_RAIN,
            temperature=45,
            wind_speed=15,
            wind_direction=WindDirection.CROSSWIND,
            precipitation_intensity=0.8
        ),
        Weather(
            condition=WeatherCondition.HEAVY_SNOW,
            temperature=25,
            wind_speed=20,
            wind_direction=WindDirection.HEADWIND,
            precipitation_intensity=0.9
        ),
        Weather(
            condition=WeatherCondition.FOG,
            temperature=55,
            wind_speed=8,
            wind_direction=WindDirection.CROSSWIND,
            precipitation_intensity=0.0
        ),
        Weather(
            condition=WeatherCondition.CLEAR,
            temperature=95,
            wind_speed=25,
            wind_direction=WindDirection.TAILWIND,
            precipitation_intensity=0.0
        ),
    ]
    
    scenario_names = [
        "Perfect Conditions",
        "Heavy Rain & Wind",
        "Blizzard Conditions", 
        "Dense Fog",
        "Hot & Windy"
    ]
    
    results = []
    
    # Test each weather scenario
    for i, (weather, scenario_name) in enumerate(zip(weather_scenarios, scenario_names)):
        print(f"\n📊 Scenario {i+1}: {scenario_name}")
        print(f"   Weather: {weather}")
        print(f"   Severity: {weather.get_severity_rating()}")
        
        # Get weather effects
        effects = weather.get_effects()
        print(f"   Effects:")
        print(f"     Passing Accuracy: {effects.passing_accuracy_modifier:.2f}x")
        print(f"     Passing Distance: {effects.passing_distance_modifier:.2f}x")
        print(f"     Kicking Accuracy: {effects.kicking_accuracy_modifier:.2f}x")
        print(f"     Fumble Chance: {effects.fumble_chance_modifier:.2f}x")
        print(f"     Visibility: {effects.visibility_modifier:.2f}x")
        
        # Run multiple simulations with this weather
        scenario_results = []
        num_sims = 10
        
        for sim in range(num_sims):
            engine = GameEngine(seed=42 + sim, weather=weather, enable_reporting=False, verbose=False)
            result = engine.simulate_game(home_team, away_team)
            scenario_results.append(result)
        
        # Calculate statistics for this scenario
        total_scores = [r.home_score + r.away_score for r in scenario_results]
        home_wins = sum(1 for r in scenario_results if r.home_score > r.away_score)
        
        avg_total_score = sum(total_scores) / len(total_scores)
        avg_home_score = sum(r.home_score for r in scenario_results) / len(scenario_results)
        avg_away_score = sum(r.away_score for r in scenario_results) / len(scenario_results)
        
        results.append({
            'scenario': scenario_name,
            'weather': weather,
            'avg_total_score': avg_total_score,
            'avg_home_score': avg_home_score,
            'avg_away_score': avg_away_score,
            'home_win_rate': home_wins / num_sims,
            'effects': effects
        })
        
        print(f"   Results ({num_sims} simulations):")
        print(f"     Average Total Score: {avg_total_score:.1f}")
        print(f"     Average Home Score: {avg_home_score:.1f}")
        print(f"     Average Away Score: {avg_away_score:.1f}")
        print(f"     Home Win Rate: {home_wins}/{num_sims} ({home_wins/num_sims*100:.1f}%)")
    
    # Summary comparison
    print(f"\n📈 Weather Impact Summary")
    print("=" * 65)
    print(f"{'Scenario':<20} {'Avg Score':<12} {'Home Win%':<12} {'Severity':<12}")
    print("-" * 65)
    
    baseline_score = results[0]['avg_total_score']
    for result in results:
        score_diff = result['avg_total_score'] - baseline_score
        score_indicator = f"{result['avg_total_score']:.1f} ({score_diff:+.1f})"
        win_rate = f"{result['home_win_rate']*100:.1f}%"
        severity = result['weather'].get_severity_rating()
        
        print(f"{result['scenario']:<20} {score_indicator:<12} {win_rate:<12} {severity:<12}")
    
    print(f"\n🎯 Key Observations:")
    
    # Find most impactful scenarios
    score_changes = [(r['scenario'], r['avg_total_score'] - baseline_score) for r in results[1:]]
    most_reduced = min(score_changes, key=lambda x: x[1])
    most_increased = max(score_changes, key=lambda x: x[1])
    
    print(f"   • {most_reduced[0]} reduced scoring by {abs(most_reduced[1]):.1f} points")
    print(f"   • {most_increased[0]} changed scoring by {most_increased[1]:+.1f} points")
    
    # Weather severity correlation
    severe_scenarios = [r for r in results if r['weather'].get_severity_rating() in ['Severe', 'Extreme']]
    if severe_scenarios:
        avg_severe_score = sum(r['avg_total_score'] for r in severe_scenarios) / len(severe_scenarios)
        print(f"   • Severe weather scenarios averaged {avg_severe_score:.1f} points per game")
        print(f"   • Perfect conditions averaged {results[0]['avg_total_score']:.1f} points per game")
    
    return results

def demo_random_weather_generation():
    """Demonstrate random weather generation."""
    print(f"\n🎲 Random Weather Generation Demo")
    print("=" * 65)
    
    # Generate various random weather samples
    weather_samples = []
    for i in range(10):
        weather = generate_random_weather(seed=i * 123)
        weather_samples.append(weather)
    
    print(f"Generated {len(weather_samples)} random weather conditions:")
    print()
    
    for i, weather in enumerate(weather_samples, 1):
        effects = weather.get_effects()
        print(f"{i:2d}. {weather} | Severity: {weather.get_severity_rating()}")
        
        # Show major effects
        significant_effects = []
        if effects.passing_accuracy_modifier < 0.95:
            significant_effects.append(f"Pass Acc: {effects.passing_accuracy_modifier:.2f}x")
        if effects.kicking_accuracy_modifier < 0.95:
            significant_effects.append(f"Kick Acc: {effects.kicking_accuracy_modifier:.2f}x")
        if effects.fumble_chance_modifier > 1.05:
            significant_effects.append(f"Fumbles: {effects.fumble_chance_modifier:.2f}x")
        
        if significant_effects:
            print(f"     Effects: {', '.join(significant_effects)}")
        print()

def demo_detailed_weather_game():
    """Show a detailed game with significant weather effects."""
    print(f"\n🏈 Detailed Weather Game Demo")
    print("=" * 65)
    
    # Create extreme weather for dramatic effect
    extreme_weather = Weather(
        condition=WeatherCondition.HEAVY_SNOW,
        temperature=15,
        wind_speed=30,
        wind_direction=WindDirection.CROSSWIND,
        precipitation_intensity=1.0
    )
    
    teams = load_sample_teams()
    home_team = next(team for team in teams if team.name == "Packers")  # Good cold weather team
    away_team = next(team for team in teams if team.name == "Dolphins")  # Warm weather team
    
    print(f"🥶 Extreme Weather Game: {away_team.city} {away_team.name} @ {home_team.city} {home_team.name}")
    print(f"Weather: {extreme_weather}")
    print(f"Severity: {extreme_weather.get_severity_rating()}")
    
    effects = extreme_weather.get_effects()
    print(f"\nWeather Effects:")
    print(f"  • Passing accuracy reduced to {effects.passing_accuracy_modifier:.0%}")
    print(f"  • Kicking accuracy reduced to {effects.kicking_accuracy_modifier:.0%}")
    print(f"  • Fumble chance increased by {(effects.fumble_chance_modifier-1)*100:.0f}%")
    print(f"  • Visibility reduced to {effects.visibility_modifier:.0%}")
    print(f"  • Field conditions at {effects.field_condition_modifier:.0%}")
    
    # Run the game with detailed reporting
    engine = GameEngine(seed=2024, weather=extreme_weather, enable_reporting=True, verbose=True)
    result = engine.simulate_game(home_team, away_team)
    
    print(f"\n🏆 Final Result:")
    print(f"   {away_team.name}: {result.away_score}")
    print(f"   {home_team.name}: {result.home_score}")
    if result.winner:
        print(f"   Winner: {result.winner.name}")
    else:
        print(f"   Result: Tie")
    
    return result

if __name__ == "__main__":
    # Run weather effects demonstrations
    print("Starting Weather Effects Demo...\n")
    
    # Demo 1: Weather impact comparison
    weather_results = demo_weather_effects()
    
    # Demo 2: Random weather generation
    demo_random_weather_generation()
    
    # Demo 3: Detailed weather game
    detailed_result = demo_detailed_weather_game()
    
    print(f"\n✅ Weather Effects Demo completed successfully!")
    print(f"   The simulation engine now includes realistic weather effects")
    print(f"   that impact passing, kicking, turnovers, and overall gameplay.")
