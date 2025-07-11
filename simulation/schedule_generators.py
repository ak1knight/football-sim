"""
Schedule generator interface and implementations for football simulation.

This module provides different scheduling strategies that can be plugged into
the SeasonEngine, allowing for different league formats (NFL, college, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
import random
from collections import defaultdict

from models.team import Team


class ScheduleGenerator(ABC):
    """Abstract base class for schedule generators."""
    
    @abstractmethod
    def generate_schedule(self, teams: List[Team], season_year: int, seed: Optional[int] = None) -> Dict[int, List[Tuple[Team, Team]]]:
        """
        Generate a complete season schedule.
        
        Args:
            teams: List of all teams in the league
            season_year: Year of the season
            seed: Random seed for reproducible scheduling
            
        Returns:
            Dictionary mapping week number to list of matchups (home, away)
        """
        pass
    
    @abstractmethod
    def get_total_weeks(self) -> int:
        """Get the total number of weeks in the season."""
        pass
    
    @abstractmethod
    def get_games_per_team(self) -> int:
        """Get the expected number of games per team."""
        pass
    
    @abstractmethod
    def get_schedule_name(self) -> str:
        """Get a descriptive name for this schedule type."""
        pass


class NFLScheduleGenerator(ScheduleGenerator):
    """
    NFL-style schedule generator.
    
    Generates a 17-game, 18-week schedule with bye weeks following NFL rules:
    - 6 games vs division rivals (3 teams x 2 games each)
    - 4 games vs one other division in same conference
    - 4 games vs one division in opposite conference
    - 3 additional games to reach 17 total
    - 1 bye week per team between weeks 4-14
    """
    
    def __init__(self):
        self.total_weeks = 18
        self.games_per_team = 17
    
    def generate_schedule(self, teams: List[Team], season_year: int, seed: Optional[int] = None) -> Dict[int, List[Tuple[Team, Team]]]:
        """Generate NFL-style schedule with bye weeks."""
        if seed is not None:
            random.seed(seed)
        
        # Organize teams by division
        divisions = self._organize_by_division(teams)
        
        # Generate all matchups
        if len(teams) == 32 and len(divisions) == 8:
            matchups = self._generate_nfl_style_matchups(teams, divisions, season_year)
        else:
            # Fallback for non-standard team counts
            matchups = self._generate_round_robin_matchups(teams)
        
        # Generate bye weeks
        bye_weeks = self._generate_bye_weeks(teams)
        
        # Distribute matchups across weeks with bye weeks
        return self._distribute_matchups_by_week_with_byes(matchups, bye_weeks)
    
    def get_total_weeks(self) -> int:
        return self.total_weeks
    
    def get_games_per_team(self) -> int:
        return self.games_per_team
    
    def get_schedule_name(self) -> str:
        return "NFL Schedule (17 games, 18 weeks, bye weeks)"
    
    def _organize_by_division(self, teams: List[Team]) -> Dict[str, List[Team]]:
        """Organize teams by conference and division."""
        divisions = defaultdict(list)
        for team in teams:
            division_key = f"{team.conference} {team.division}"
            divisions[division_key].append(team)
        return dict(divisions)
    
    def _generate_nfl_style_matchups(self, teams: List[Team], divisions: Dict[str, List[Team]], season_year: int) -> List[Tuple[Team, Team]]:
        """Generate NFL-style matchups following exact NFL scheduling rules."""
        matchups = []
        
        # Group divisions by conference
        afc_divisions = {k: v for k, v in divisions.items() if k.startswith('AFC')}
        nfc_divisions = {k: v for k, v in divisions.items() if k.startswith('NFC')}
        
        # Convert to lists for easier rotation logic
        afc_division_list = list(afc_divisions.keys())
        nfc_division_list = list(nfc_divisions.keys())
        
        # Track games per team to ensure exactly 17
        games_per_team = {team.abbreviation: 0 for team in teams}
        
        # 1. DIVISIONAL GAMES: Each team plays division rivals twice (6 games)
        for division_name, division_teams in divisions.items():
            for i, team1 in enumerate(division_teams):
                for j, team2 in enumerate(division_teams):
                    if i < j:  # Only process each pair once
                        # Team1 hosts Team2
                        matchups.append((team1, team2))
                        games_per_team[team1.abbreviation] += 1
                        games_per_team[team2.abbreviation] += 1
                        
                        # Team2 hosts Team1 (return game)
                        matchups.append((team2, team1))
                        games_per_team[team1.abbreviation] += 1
                        games_per_team[team2.abbreviation] += 1
        
        # 2. INTRA-CONFERENCE GAMES: Each division plays one other division in same conference (4 games)
        # AFC divisions - simple pairing
        afc_pairings = [
            ('AFC East', 'AFC North'),
            ('AFC South', 'AFC West')
        ]
        
        for div1_name, div2_name in afc_pairings:
            # Each team in div1 plays each team in div2 once
            for team1 in afc_divisions[div1_name]:
                for team2 in afc_divisions[div2_name]:
                    # Alternate home/away based on team order
                    if hash(team1.abbreviation + team2.abbreviation) % 2 == 0:
                        matchups.append((team1, team2))
                    else:
                        matchups.append((team2, team1))
                    
                    games_per_team[team1.abbreviation] += 1
                    games_per_team[team2.abbreviation] += 1
        
        # NFC divisions - simple pairing
        nfc_pairings = [
            ('NFC East', 'NFC North'),
            ('NFC South', 'NFC West')
        ]
        
        for div1_name, div2_name in nfc_pairings:
            for team1 in nfc_divisions[div1_name]:
                for team2 in nfc_divisions[div2_name]:
                    if hash(team1.abbreviation + team2.abbreviation) % 2 == 0:
                        matchups.append((team1, team2))
                    else:
                        matchups.append((team2, team1))
                    
                    games_per_team[team1.abbreviation] += 1
                    games_per_team[team2.abbreviation] += 1
        
        # 3. INTER-CONFERENCE GAMES: Each division plays one opposite conference division (4 games)
        for i, afc_div in enumerate(afc_division_list):
            # AFC division plays against NFC division
            nfc_target_index = i % len(nfc_division_list)  # Simple pairing
            nfc_div = nfc_division_list[nfc_target_index]
            
            for afc_team in afc_divisions[afc_div]:
                for nfc_team in nfc_divisions[nfc_div]:
                    # Alternate home/away
                    if hash(afc_team.abbreviation + nfc_team.abbreviation) % 2 == 0:
                        matchups.append((afc_team, nfc_team))
                    else:
                        matchups.append((nfc_team, afc_team))
                    
                    games_per_team[afc_team.abbreviation] += 1
                    games_per_team[nfc_team.abbreviation] += 1
        
        # 4. REMAINING GAMES: Fill to exactly 17 games per team
        # At this point, each team should have 14 games (6 + 4 + 4)
        # We need to add 3 more games per team
        
        all_teams = list(teams)
        max_attempts = 1000  # Prevent infinite loops
        attempt = 0
        
        while attempt < max_attempts:
            # Find teams that need more games
            teams_needing_games = [team for team in all_teams if games_per_team[team.abbreviation] < 17]
            
            if not teams_needing_games:
                break  # All teams have 17 games
            
            # Try to pair teams that both need games
            game_added = False
            
            for team in teams_needing_games:
                if games_per_team[team.abbreviation] >= 17:
                    continue
                
                # Find opponents that also need games and haven't played this team yet
                potential_opponents = []
                
                for opponent in teams_needing_games:
                    if (opponent != team and 
                        games_per_team[opponent.abbreviation] < 17 and
                        not self._teams_already_play(team, opponent, matchups)):
                        potential_opponents.append(opponent)
                
                if potential_opponents:
                    # Pick first available opponent
                    opponent = potential_opponents[0]
                    
                    # Decide home/away
                    if hash(team.abbreviation + opponent.abbreviation + str(season_year)) % 2 == 0:
                        matchups.append((team, opponent))
                    else:
                        matchups.append((opponent, team))
                    
                    games_per_team[team.abbreviation] += 1
                    games_per_team[opponent.abbreviation] += 1
                    game_added = True
                    break
            
            if not game_added:
                # If we can't find perfect pairs, just add games even if they create duplicates
                for team in teams_needing_games:
                    if games_per_team[team.abbreviation] >= 17:
                        continue
                        
                    # Find any opponent that needs games
                    for opponent in teams_needing_games:
                        if (opponent != team and 
                            games_per_team[opponent.abbreviation] < 17):
                            
                            # Add the game
                            if hash(team.abbreviation + opponent.abbreviation + str(season_year)) % 2 == 0:
                                matchups.append((team, opponent))
                            else:
                                matchups.append((opponent, team))
                            
                            games_per_team[team.abbreviation] += 1
                            games_per_team[opponent.abbreviation] += 1
                            game_added = True
                            break
                    
                    if game_added:
                        break
            
            attempt += 1
        
        return matchups
    
    def _teams_already_play(self, team1: Team, team2: Team, matchups: List[Tuple[Team, Team]]) -> bool:
        """Check if two teams already have a matchup scheduled."""
        for home, away in matchups:
            if ((home == team1 and away == team2) or 
                (home == team2 and away == team1)):
                return True
        return False
    
    def _generate_round_robin_matchups(self, teams: List[Team]) -> List[Tuple[Team, Team]]:
        """Generate matchups for non-standard team configurations."""
        matchups = []
        num_teams = len(teams)
        
        # Simple round-robin approach
        for i in range(num_teams):
            for j in range(i + 1, num_teams):
                home_team = teams[i]
                away_team = teams[j]
                
                # Randomly decide home/away
                if random.random() < 0.5:
                    matchups.append((home_team, away_team))
                else:
                    matchups.append((away_team, home_team))
        
        # Limit to approximately 17 games per team
        target_matchups = min(len(teams) * 17 // 2, len(matchups))
        random.shuffle(matchups)
        return matchups[:target_matchups]
    
    def _generate_bye_weeks(self, teams: List[Team]) -> Dict[str, int]:
        """Generate bye weeks for all teams between weeks 4-14."""
        bye_weeks = {}
        available_weeks = list(range(4, 15))  # Weeks 4-14
        teams_list = list(teams)
        
        # Shuffle teams to randomize bye week assignments
        random.shuffle(teams_list)
        
        # Distribute teams across bye weeks as evenly as possible
        teams_per_week = len(teams_list) // len(available_weeks)
        extra_teams = len(teams_list) % len(available_weeks)
        
        team_index = 0
        for week_index, week in enumerate(available_weeks):
            # Some weeks get one extra team
            teams_this_week = teams_per_week + (1 if week_index < extra_teams else 0)
            
            for _ in range(teams_this_week):
                if team_index < len(teams_list):
                    bye_weeks[teams_list[team_index].abbreviation] = week
                    team_index += 1
        
        return bye_weeks
    
    def _distribute_matchups_by_week_with_byes(self, matchups: List[Tuple[Team, Team]], 
                                             bye_weeks: Dict[str, int]) -> Dict[int, List[Tuple[Team, Team]]]:
        """Distribute matchups across 18 weeks considering bye weeks."""
        week_matchups = {week: [] for week in range(1, 19)}  # 18 weeks
        remaining_matchups = matchups.copy()
        
        # Simple but effective approach: go through each week and schedule as many games as possible
        for week in range(1, 19):
            # Find teams that are on bye this week
            teams_on_bye = set()
            for team_abbr, bye_week in bye_weeks.items():
                if bye_week == week:
                    teams_on_bye.add(team_abbr)
            
            # Track which teams are already playing this week
            teams_playing_this_week = set()
            
            # Try to schedule games for this week
            games_to_schedule = []
            
            for matchup in remaining_matchups[:]:  # Copy the list for safe iteration
                home_team, away_team = matchup
                
                # Skip if either team is on bye this week
                if (home_team.abbreviation in teams_on_bye or 
                    away_team.abbreviation in teams_on_bye):
                    continue
                
                # Skip if either team is already playing this week
                if (home_team.abbreviation in teams_playing_this_week or 
                    away_team.abbreviation in teams_playing_this_week):
                    continue
                
                # Schedule this game
                games_to_schedule.append(matchup)
                teams_playing_this_week.add(home_team.abbreviation)
                teams_playing_this_week.add(away_team.abbreviation)
                
                # Don't overfill the week
                if len(games_to_schedule) >= 16:
                    break
            
            # Add scheduled games to the week and remove from remaining
            for game in games_to_schedule:
                week_matchups[week].append(game)
                remaining_matchups.remove(game)
        
        # If there are remaining matchups, force them into available slots
        for matchup in remaining_matchups:
            home_team, away_team = matchup
            
            # Find the best week for this matchup
            best_week = None
            min_conflicts = float('inf')
            
            for week in range(1, 19):
                # Skip if either team is on bye this week
                if (bye_weeks.get(home_team.abbreviation) == week or 
                    bye_weeks.get(away_team.abbreviation) == week):
                    continue
                
                # Count conflicts (teams already playing this week)
                conflicts = 0
                teams_playing_this_week = set()
                for existing_home, existing_away in week_matchups[week]:
                    teams_playing_this_week.add(existing_home.abbreviation)
                    teams_playing_this_week.add(existing_away.abbreviation)
                
                if home_team.abbreviation in teams_playing_this_week:
                    conflicts += 1
                if away_team.abbreviation in teams_playing_this_week:
                    conflicts += 1
                
                # Choose the week with the fewest conflicts
                if conflicts < min_conflicts:
                    min_conflicts = conflicts
                    best_week = week
            
            # Schedule in the best week found (even if it has conflicts)
            if best_week is not None:
                week_matchups[best_week].append(matchup)
        
        return week_matchups


class CollegeFootballScheduleGenerator(ScheduleGenerator):
    """
    College football schedule generator.
    
    Generates a 12-game, 14-week schedule typical of college football:
    - No bye weeks (simpler scheduling)
    - Conference games prioritized
    - Some non-conference games
    - Shorter season than NFL
    """
    
    def __init__(self):
        self.total_weeks = 14
        self.games_per_team = 12
    
    def generate_schedule(self, teams: List[Team], season_year: int, seed: Optional[int] = None) -> Dict[int, List[Tuple[Team, Team]]]:
        """Generate college football style schedule."""
        if seed is not None:
            random.seed(seed)
        
        # Generate matchups (simpler than NFL)
        matchups = self._generate_college_matchups(teams)
        
        # Distribute across weeks (no bye weeks)
        return self._distribute_matchups_by_week(matchups)
    
    def get_total_weeks(self) -> int:
        return self.total_weeks
    
    def get_games_per_team(self) -> int:
        return self.games_per_team
    
    def get_schedule_name(self) -> str:
        return "College Football Schedule (12 games, 14 weeks, no byes)"
    
    def _generate_college_matchups(self, teams: List[Team]) -> List[Tuple[Team, Team]]:
        """Generate college football style matchups."""
        matchups = []
        
        # Organize by conference
        conferences = defaultdict(list)
        for team in teams:
            conferences[team.conference].append(team)
        
        # Generate conference games (each team plays most teams in their conference)
        for conference, conf_teams in conferences.items():
            for i, team1 in enumerate(conf_teams):
                for j, team2 in enumerate(conf_teams):
                    if i < j:
                        # Some conference matchups (not all teams play all others)
                        if random.random() < 0.7:  # 70% chance of playing conference opponent
                            if random.random() < 0.5:
                                matchups.append((team1, team2))
                            else:
                                matchups.append((team2, team1))
        
        # Add some non-conference games
        all_teams = list(teams)
        for team in all_teams:
            # Add a few non-conference opponents
            other_teams = [t for t in all_teams if t.conference != team.conference]
            if other_teams:
                for _ in range(min(3, len(other_teams))):  # Up to 3 non-conference games
                    if random.random() < 0.3:  # 30% chance
                        opponent = random.choice(other_teams)
                        if not self._teams_already_play(team, opponent, matchups):
                            if random.random() < 0.5:
                                matchups.append((team, opponent))
                            else:
                                matchups.append((opponent, team))
        
        # Trim to approximately 12 games per team
        target_matchups = len(teams) * self.games_per_team // 2
        random.shuffle(matchups)
        return matchups[:target_matchups]
    
    def _teams_already_play(self, team1: Team, team2: Team, matchups: List[Tuple[Team, Team]]) -> bool:
        """Check if two teams already have a matchup scheduled."""
        for home, away in matchups:
            if ((home == team1 and away == team2) or 
                (home == team2 and away == team1)):
                return True
        return False
    
    def _distribute_matchups_by_week(self, matchups: List[Tuple[Team, Team]]) -> Dict[int, List[Tuple[Team, Team]]]:
        """Distribute matchups across weeks (no bye weeks)."""
        week_matchups = {week: [] for week in range(1, self.total_weeks + 1)}
        remaining_matchups = matchups.copy()
        random.shuffle(remaining_matchups)
        
        # Simple week-by-week distribution
        for week in range(1, self.total_weeks + 1):
            teams_playing_this_week = set()
            games_to_schedule = []
            
            for matchup in remaining_matchups[:]:
                home_team, away_team = matchup
                
                # Skip if either team is already playing this week
                if (home_team.abbreviation in teams_playing_this_week or 
                    away_team.abbreviation in teams_playing_this_week):
                    continue
                
                # Schedule this game
                games_to_schedule.append(matchup)
                teams_playing_this_week.add(home_team.abbreviation)
                teams_playing_this_week.add(away_team.abbreviation)
            
            # Add scheduled games to the week and remove from remaining
            for game in games_to_schedule:
                week_matchups[week].append(game)
                remaining_matchups.remove(game)
        
        return week_matchups
