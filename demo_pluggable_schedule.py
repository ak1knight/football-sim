"""
Comprehensive demo of the pluggable schedule generator system.

This demo showcases the extensibility of the new schedule generator architecture
and how different league types can be easily supported.
"""

from data.team_loader import load_sample_teams
from simulation.season_engine import SeasonEngine
from simulation.schedule_generators import NFLScheduleGenerator, CollegeFootballScheduleGenerator


def demo_schedule_generator_extensibility():
    """Demonstrate the extensibility of the schedule generator system."""
    print("=" * 80)
    print("PLUGGABLE SCHEDULE GENERATOR DEMO")
    print("=" * 80)
    
    teams = load_sample_teams()
    print(f"Loaded {len(teams)} teams for demonstration")
    
    print("\n" + "=" * 60)
    print("1. NFL SCHEDULE GENERATOR")
    print("=" * 60)
    
    # Create NFL season
    nfl_season = SeasonEngine(teams, 2024, seed=42, 
                             schedule_generator=NFLScheduleGenerator())
    
    nfl_status = nfl_season.get_season_status()
    print(f"Schedule Type: {nfl_status['schedule_type']}")
    print(f"Total Games: {nfl_status['total_games']}")
    print(f"Weeks: {nfl_season.schedule_generator.get_total_weeks()}")
    print(f"Games per Team: {nfl_season.schedule_generator.get_games_per_team()}")
    
    # Show bye weeks
    bye_week_count = {}
    for week in range(1, 19):
        week_games = nfl_season.get_week_games(week)
        teams_playing = set()
        for game in week_games:
            teams_playing.add(game.home_team.abbreviation)
            teams_playing.add(game.away_team.abbreviation)
        
        teams_on_bye = len(teams) - len(teams_playing)
        if teams_on_bye > 0:
            bye_week_count[week] = teams_on_bye
    
    print(f"Bye weeks: {len(bye_week_count)} weeks with byes")
    if bye_week_count:
        print(f"  Range: Week {min(bye_week_count.keys())} - Week {max(bye_week_count.keys())}")
    
    print("\n" + "=" * 60)
    print("2. COLLEGE FOOTBALL SCHEDULE GENERATOR")
    print("=" * 60)
    
    # Create College Football season
    college_season = SeasonEngine(teams, 2024, seed=42, 
                                 schedule_generator=CollegeFootballScheduleGenerator())
    
    college_status = college_season.get_season_status()
    print(f"Schedule Type: {college_status['schedule_type']}")
    print(f"Total Games: {college_status['total_games']}")
    print(f"Weeks: {college_season.schedule_generator.get_total_weeks()}")
    print(f"Games per Team: {college_season.schedule_generator.get_games_per_team()}")
    
    # Analyze games per team distribution
    college_games_per_team = {}
    for game in college_season.schedule:
        home_abbr = game.home_team.abbreviation
        away_abbr = game.away_team.abbreviation
        college_games_per_team[home_abbr] = college_games_per_team.get(home_abbr, 0) + 1
        college_games_per_team[away_abbr] = college_games_per_team.get(away_abbr, 0) + 1
    
    min_games = min(college_games_per_team.values())
    max_games = max(college_games_per_team.values())
    avg_games = sum(college_games_per_team.values()) / len(college_games_per_team)
    print(f"Games per team: {min_games} - {max_games} (avg: {avg_games:.1f})")
    
    print("\n" + "=" * 60)
    print("3. DEFAULT BEHAVIOR")
    print("=" * 60)
    
    # Create season with default generator
    default_season = SeasonEngine(teams, 2024, seed=42)
    default_status = default_season.get_season_status()
    print(f"Default Schedule Type: {default_status['schedule_type']}")
    print("✓ Defaults to NFL schedule generator when none specified")
    
    print("\n" + "=" * 60)
    print("4. SCHEDULE COMPARISON")
    print("=" * 60)
    
    print(f"{'Aspect':<20} {'NFL':<25} {'College':<25}")
    print("-" * 70)
    print(f"{'Total Games':<20} {nfl_status['total_games']:<25} {college_status['total_games']:<25}")
    print(f"{'Total Weeks':<20} {nfl_season.schedule_generator.get_total_weeks():<25} {college_season.schedule_generator.get_total_weeks():<25}")
    print(f"{'Games per Team':<20} {nfl_season.schedule_generator.get_games_per_team():<25} {f'{min_games}-{max_games}':<25}")
    print(f"{'Bye Weeks':<20} {'Yes (4-14)':<25} {'No':<25}")
    
    print("\n" + "=" * 60)
    print("5. EXTENSIBILITY SHOWCASE")
    print("=" * 60)
    
    print("✓ Easy to add new league types:")
    print("  1. Create new class inheriting from ScheduleGenerator")
    print("  2. Implement generate_schedule() method")
    print("  3. Pass to SeasonEngine constructor")
    print()
    print("✓ All season management features work with any generator:")
    print("  - Standings tracking")
    print("  - Game result processing")
    print("  - Playoff picture")
    print("  - Season statistics")
    print()
    print("✓ Clean separation of concerns:")
    print("  - SeasonEngine: Season management, standings, API")
    print("  - ScheduleGenerator: Schedule creation logic")
    print("  - Complete modularity and testability")
    
    print("\n" + "=" * 80)
    print("REFACTORING COMPLETE!")
    print("The schedule generation logic is now fully pluggable and extensible.")
    print("Different league types can easily use different scheduling algorithms.")
    print("=" * 80)


def show_sample_schedules():
    """Show sample schedules from both generators."""
    print("\n" + "=" * 60)
    print("SAMPLE SCHEDULES")
    print("=" * 60)
    
    teams = load_sample_teams()
    
    # NFL Sample
    nfl_season = SeasonEngine(teams, 2024, seed=42, 
                             schedule_generator=NFLScheduleGenerator())
    
    print("\nNFL Schedule (Week 1):")
    week1_games = nfl_season.get_week_games(1)
    for game in week1_games[:8]:  # Show first 8 games
        print(f"  {game.away_team.city} {game.away_team.name} @ {game.home_team.city} {game.home_team.name}")
    
    # College Sample
    college_season = SeasonEngine(teams, 2024, seed=42, 
                                 schedule_generator=CollegeFootballScheduleGenerator())
    
    print("\nCollege Football Schedule (Week 1):")
    week1_games = college_season.get_week_games(1)
    for game in week1_games[:8]:  # Show first 8 games
        print(f"  {game.away_team.city} {game.away_team.name} @ {game.home_team.city} {game.home_team.name}")


if __name__ == "__main__":
    demo_schedule_generator_extensibility()
    show_sample_schedules()
