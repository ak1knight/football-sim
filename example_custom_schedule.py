"""
Example of creating a custom schedule generator.

This demonstrates how easy it is to create new schedule types
for different league formats or experimental scheduling rules.
"""

from typing import Dict, List, Tuple
import random
from simulation.schedule_generators import ScheduleGenerator
from models.team import Team


class ShortSeasonScheduleGenerator(ScheduleGenerator):
    """
    Example custom schedule generator for a short season format.
    
    This could be used for preseason, tournament play, or experimental formats.
    Each team plays 8 games over 10 weeks with some bye weeks.
    """
    
    def __init__(self):
        self.total_weeks = 10
        self.games_per_team = 8
    
    def generate_schedule(self, teams: List[Team], season_year: int, seed: int = None) -> Dict[int, List[Tuple[Team, Team]]]:
        """Generate a short season schedule."""
        if seed is not None:
            random.seed(seed)
        
        # Generate matchups
        matchups = self._generate_short_season_matchups(teams)
        
        # Distribute across weeks
        return self._distribute_matchups_across_weeks(matchups)
    
    def get_total_weeks(self) -> int:
        return self.total_weeks
    
    def get_games_per_team(self) -> int:
        return self.games_per_team
    
    def get_schedule_name(self) -> str:
        return "Short Season Schedule (8 games, 10 weeks)"
    
    def _generate_short_season_matchups(self, teams: List[Team]) -> List[Tuple[Team, Team]]:
        """Generate matchups for short season."""
        matchups = []
        
        # Create a simple round-robin with limited games
        for i, team1 in enumerate(teams):
            opponents_needed = self.games_per_team
            potential_opponents = [t for t in teams if t != team1]
            
            # Randomly select opponents
            selected_opponents = random.sample(
                potential_opponents, 
                min(opponents_needed, len(potential_opponents))
            )
            
            for opponent in selected_opponents:
                # Check if this matchup already exists
                if not self._matchup_exists(team1, opponent, matchups):
                    # Randomly decide home/away
                    if random.random() < 0.5:
                        matchups.append((team1, opponent))
                    else:
                        matchups.append((opponent, team1))
        
        return matchups
    
    def _matchup_exists(self, team1: Team, team2: Team, matchups: List[Tuple[Team, Team]]) -> bool:
        """Check if a matchup already exists."""
        for home, away in matchups:
            if ((home == team1 and away == team2) or 
                (home == team2 and away == team1)):
                return True
        return False
    
    def _distribute_matchups_across_weeks(self, matchups: List[Tuple[Team, Team]]) -> Dict[int, List[Tuple[Team, Team]]]:
        """Distribute matchups across weeks."""
        week_schedule = {week: [] for week in range(1, self.total_weeks + 1)}
        remaining_matchups = matchups.copy()
        random.shuffle(remaining_matchups)
        
        for week in range(1, self.total_weeks + 1):
            teams_playing = set()
            games_this_week = []
            
            for matchup in remaining_matchups[:]:
                home_team, away_team = matchup
                
                # Skip if either team is already playing this week
                if (home_team.abbreviation in teams_playing or 
                    away_team.abbreviation in teams_playing):
                    continue
                
                # Schedule the game
                games_this_week.append(matchup)
                teams_playing.add(home_team.abbreviation)
                teams_playing.add(away_team.abbreviation)
                
                # Limit games per week
                if len(games_this_week) >= 12:
                    break
            
            # Remove scheduled games from remaining
            for game in games_this_week:
                if game in remaining_matchups:
                    remaining_matchups.remove(game)
            
            week_schedule[week] = games_this_week
        
        return week_schedule


def demo_custom_schedule_generator():
    """Demonstrate the custom schedule generator."""
    print("=" * 60)
    print("CUSTOM SCHEDULE GENERATOR DEMO")
    print("=" * 60)
    
    from data.team_loader import load_sample_teams
    from simulation.season_engine import SeasonEngine
    
    teams = load_sample_teams()
    
    # Create a season with our custom generator
    custom_generator = ShortSeasonScheduleGenerator()
    season = SeasonEngine(teams, 2024, seed=42, schedule_generator=custom_generator)
    
    status = season.get_season_status()
    print(f"Schedule Type: {status['schedule_type']}")
    print(f"Total Games: {status['total_games']}")
    print(f"Total Weeks: {custom_generator.get_total_weeks()}")
    print(f"Games per Team: {custom_generator.get_games_per_team()}")
    
    # Show games per team distribution
    games_per_team = {}
    for game in season.schedule:
        home_abbr = game.home_team.abbreviation
        away_abbr = game.away_team.abbreviation
        games_per_team[home_abbr] = games_per_team.get(home_abbr, 0) + 1
        games_per_team[away_abbr] = games_per_team.get(away_abbr, 0) + 1
    
    min_games = min(games_per_team.values())
    max_games = max(games_per_team.values())
    avg_games = sum(games_per_team.values()) / len(games_per_team)
    print(f"Games per team: {min_games} - {max_games} (avg: {avg_games:.1f})")
    
    # Show weekly distribution
    print("\nWeekly Schedule:")
    for week in range(1, custom_generator.get_total_weeks() + 1):
        week_games = season.get_week_games(week)
        print(f"Week {week}: {len(week_games)} games")
        
        # Show first few games
        for game in week_games[:3]:
            print(f"  {game.away_team.abbreviation} @ {game.home_team.abbreviation}")
    
    print("\n" + "=" * 60)
    print("CUSTOM GENERATOR CREATION STEPS")
    print("=" * 60)
    print("1. Inherit from ScheduleGenerator")
    print("2. Implement required abstract methods:")
    print("   - generate_schedule()")
    print("   - get_total_weeks()")
    print("   - get_games_per_team()")
    print("   - get_schedule_name()")
    print("3. Pass to SeasonEngine constructor")
    print("4. All season management features work automatically!")
    
    return season


if __name__ == "__main__":
    demo_custom_schedule_generator()
