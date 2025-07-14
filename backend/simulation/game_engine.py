"""
Game simulation engine for American football.

This module contains the core logic for simulating football games,
including play-by-play simulation, scoring, and game flow.
"""

import random
import logging
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

from models.team import Team
from models.weather import Weather, generate_random_weather, WeatherEffects
from simulation.game_reporter import GameReporter


@dataclass
class GameResult:
    """Result of a simulated game."""
    home_team: Team
    away_team: Team
    home_score: int
    away_score: int
    duration: int  # Game duration in minutes
    weather: Optional[Weather] = None  # Weather conditions during the game
    
    @property
    def winner(self) -> Optional[Team]:
        """Get the winning team, or None if tied."""
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None


class GameEngine:
    """
    Core simulation engine for football games.
    
    This class handles the simulation of entire games, including
    drive simulation, scoring plays, and game flow management.
    """
    def __init__(self, seed: Optional[int] = None, enable_reporting: bool = False, verbose: bool = False, weather: Optional[Weather] = None):
        """
        Initialize the game engine.
        
        Args:
            seed: Random seed for reproducible simulations
            enable_reporting: Whether to enable detailed play-by-play reporting
            verbose: Whether to print detailed information during simulation
            weather: Weather conditions for the game (None = random weather)
        """
        self.logger = logging.getLogger(__name__)
        self.seed = seed        
        self.enable_reporting = enable_reporting
        self.verbose = verbose
        self.reporter = GameReporter() if enable_reporting else None
        self.weather = weather
        self.weather_effects = None
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def simulate_game(self, home_team: Team, away_team: Team) -> GameResult:
        """
        Simulate a complete game between two teams.
        
        Args:
            home_team: The home team
            away_team: The away team
            
        Returns:
            GameResult with final scores and game details
        """
        # Set seed before each game for reproducibility
        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed)
        
        # Set up weather conditions
        if self.weather is None:
            # Generate random weather if none provided
            weather_seed = self.seed + 1000 if self.seed is not None else None
            self.weather = generate_random_weather(weather_seed)
        
        self.weather_effects = self.weather.get_effects()
        
        self.logger.info(f"Starting simulation: {away_team.name} @ {home_team.name}")
        self.logger.info(f"Weather: {self.weather} (Severity: {self.weather.get_severity_rating()})")
        
        # Start game reporting
        if self.reporter:
            self.reporter.start_game(home_team, away_team, self.verbose)
            # Log weather information
            if self.verbose:
                print(f"\n🌤️  Weather Conditions: {self.weather}")
                print(f"   Severity: {self.weather.get_severity_rating()}")
        
        # Initialize scores
        home_score = 0
        away_score = 0
        
        # Track possession state between quarters
        self.quarter_possession = None  # Will store possession info for quarter transitions
        
        # Track who received opening kickoff for halftime logic
        self.opening_kickoff_receiver = home_team  # Home team receives opening kickoff (away team kicks)
        
        # Simulate four quarters
        for quarter in range(1, 5):
            self.logger.info(f"Quarter {quarter}")
            
            # Start quarter reporting
            if self.reporter:
                self.reporter.start_quarter(quarter)
            
            quarter_home, quarter_away = self._simulate_quarter(
                home_team, away_team, quarter
            )
            home_score += quarter_home
            away_score += quarter_away
            
            # End quarter reporting
            if self.reporter:
                self.reporter.end_quarter(quarter_home, quarter_away)
            
            self.logger.info(f"End Q{quarter}: {home_team.name} {home_score}, {away_team.name} {away_score}")
        
        # Check for overtime
        game_duration = 60  # Regular game duration
        overtime = False
        if home_score == away_score:
            self.logger.info("Game tied, going to overtime")
            overtime = True
            ot_home, ot_away = self._simulate_overtime(home_team, away_team)
            home_score += ot_home
            away_score += ot_away
            game_duration += 15  # Add overtime period
        
        result = GameResult(
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            duration=game_duration,
            weather=self.weather
        )
        
        # Update team records
        self._update_team_records(result)
        
        # End game reporting
        if self.reporter:
            self.reporter.end_game(home_score, away_score, game_duration, overtime)
        
        self.logger.info(f"Final: {home_team.name} {home_score}, {away_team.name} {away_score}")
        return result
    
    def _simulate_quarter(self, home_team: Team, away_team: Team, quarter: int) -> Tuple[int, int]:
        """
        Simulate one quarter of gameplay with realistic time management.
        
        Returns:
            Tuple of (home_points, away_points) scored in this quarter
        """
        home_points = 0
        away_points = 0
        
        # Quarter time is 15 minutes (900 seconds)
        time_remaining = 900  # seconds
        
        # Initialize field position tracking
        # Field position: 0-100 (0 = offense's goal line, 100 = opponent's goal line)
        if quarter == 1:
            # Game starts with kickoff - away team kicks to home team
            possession_team = home_team
            defending_team = away_team
            field_position = self._simulate_kickoff(away_team, home_team)
            is_home_possession = True
            down = 1
            yards_for_first_down = 10
        elif quarter == 2 or quarter == 4:
            # Check if there's possession from previous quarter
            if hasattr(self, 'quarter_possession') and self.quarter_possession:
                # Continue with same possession from previous quarter
                possession_team = self.quarter_possession['team']
                defending_team = self.quarter_possession['opponent']
                field_position = self.quarter_possession['field_position']
                is_home_possession = (possession_team == home_team)
                down = self.quarter_possession.get('down', 1)
                yards_for_first_down = self.quarter_possession.get('yards_for_first_down', 10)
                self.logger.info(f"Q{quarter}: Continuing drive - {possession_team.name} has ball at {field_position}-yard line")
            else:
                # No previous possession or Q4 - start with kickoff or random
                if quarter == 4:
                    # Q4 typically starts with the team that didn't get Q1 kickoff
                    possession_team = away_team
                    defending_team = home_team
                    field_position = self._simulate_kickoff(home_team, away_team)
                    is_home_possession = False
                else:
                    # Q2 - random start if no carry-over
                    if random.random() < 0.5:
                        possession_team = home_team
                        defending_team = away_team
                        is_home_possession = True
                    else:
                        possession_team = away_team
                        defending_team = home_team
                        is_home_possession = False
                    field_position = random.randint(20, 80)
                down = 1
                yards_for_first_down = 10
        else:  # quarter == 3
            # Q3 starts with halftime kickoff - opposite team from opening kickoff receives
            if self.opening_kickoff_receiver == home_team:
                # Home team got opening kickoff, so away team gets halftime kickoff
                possession_team = away_team
                defending_team = home_team
                field_position = self._simulate_kickoff(home_team, away_team)
                is_home_possession = False
            else:
                # Away team got opening kickoff, so home team gets halftime kickoff  
                possession_team = home_team
                defending_team = away_team
                field_position = self._simulate_kickoff(away_team, home_team)
                is_home_possession = True
            down = 1
            yards_for_first_down = 10
        
        drives_in_quarter = 0
        
        while time_remaining > 0:
            drives_in_quarter += 1
            
            # Start drive reporting
            if self.reporter:
                self.reporter.start_drive(drives_in_quarter, possession_team, defending_team, field_position)
            
            # Simulate drive with time tracking
            drive_result = self._simulate_drive_with_time(
                possession_team, defending_team, is_home_possession, field_position, time_remaining
            )
            
            # Update time remaining
            time_remaining -= drive_result['time_elapsed']
            
            # End drive reporting
            if self.reporter:
                self.reporter.end_drive(drive_result['result'], drive_result['points'], drive_result['final_field_position'])
            
            # Update score
            if is_home_possession:
                home_points += drive_result['points']
            else:
                away_points += drive_result['points']
            
            # If quarter time is up, save possession state for next quarter (Q1->Q2, Q3->Q4)
            if time_remaining <= 0:
                if quarter == 1 or quarter == 3:
                    # Drive was cut short by end of quarter - save possession state
                    if drive_result['result'] == 'end_of_quarter':
                        self.quarter_possession = {
                            'team': possession_team,
                            'opponent': defending_team,
                            'field_position': drive_result['final_field_position'],
                            'down': drive_result.get('down', 1),
                            'yards_for_first_down': drive_result.get('yards_for_first_down', 10)
                        }
                        self.logger.info(f"Q{quarter} ends mid-drive: {possession_team.name} retains ball at {drive_result['final_field_position']}-yard line")
                    else:
                        # Drive completed normally, clear possession
                        self.quarter_possession = None
                else:
                    # Q2 or Q4 ending - clear possession
                    self.quarter_possession = None
                break
            
            # Determine next possession and field position based on drive result
            next_possession = self._handle_drive_transition(
                drive_result, possession_team, defending_team
            )
            
            # Update possession
            possession_team = next_possession['team']
            defending_team = next_possession['opponent']
            is_home_possession = (possession_team == home_team)
            field_position = next_possession['field_position']

        return home_points, away_points

    def _simulate_play(self, offense: Team, defense: Team, is_home: bool, down: int, yards_for_first: int, yards_to_goal: int) -> dict:
        """
        Simulate a single play.
        
        Args:
            offense: Team with possession
            defense: Defending team
            is_home: Whether the offensive team is playing at home
            down: Current down (1-4)
            yards_for_first: Yards needed for first down
            yards_to_goal: Yards to goal line
            
        Returns:
            Dictionary with play type and yards gained
        """
        # Calculate play success based on team ratings and situation
        off_rating = offense.stats.offensive_rating
        def_rating = defense.stats.defensive_rating
        
        # Home field advantage
        home_bonus = 2 if is_home else 0
        
        # Down and distance modifiers
        situation_modifier = self._get_situation_modifier(down, yards_for_first, yards_to_goal)
        
        # Base success rating - improve offensive efficiency
        success_rating = (off_rating + home_bonus - def_rating + situation_modifier) / 90.0  # Changed from 100 to 90 for better scoring
        
        # Determine play type based on situation
        play_type = self._choose_play_type(down, yards_for_first, yards_to_goal)
        
        # Simulate play outcome
        if play_type == "run":
            yards_gained = self._simulate_run_play(success_rating, yards_to_goal)
        elif play_type == "pass":
            yards_gained = self._simulate_pass_play(success_rating, yards_for_first, yards_to_goal)
        else:  # Special play
            yards_gained = self._simulate_special_play(success_rating)
        
        # Check for turnover
        turnover_chance = self._calculate_turnover_chance(play_type, success_rating, down)
        if random.random() < turnover_chance:
            return {
                'play_type': 'turnover',
                'yards_gained': 0
            }
        
        # Ensure we don't go backwards past our own goal line
        yards_gained = max(yards_gained, -(100 - yards_to_goal))
        
        return {
            'play_type': play_type,
            'yards_gained': yards_gained
        }
    
    def _get_situation_modifier(self, down: int, yards_for_first: int, yards_to_goal: int) -> float:
        """Get modifier based on down and distance situation."""
        modifier = 0
        
        # Down modifiers
        if down == 1:
            modifier += 5  # Fresh set of downs
        elif down == 2:
            modifier += 2
        elif down == 3:
            modifier -= 3  # Pressure situation
        else:  # 4th down
            modifier -= 8  # High pressure
        
        # Distance modifiers
        if yards_for_first <= 3:
            modifier += 3  # Short yardage
        elif yards_for_first >= 10:
            modifier -= 5  # Long yardage
        
        # Red zone bonus
        if yards_to_goal <= 20:
            modifier += 3
        
        return modifier
    
    def _choose_play_type(self, down: int, yards_for_first: int, yards_to_goal: int) -> str:
        """Choose play type based on situation."""
        # Base probabilities
        run_prob = 0.45
        pass_prob = 0.55
        
        # Adjust based on down and distance
        if yards_for_first <= 3:  # Short yardage - more running
            run_prob = 0.65
            pass_prob = 0.35
        elif yards_for_first >= 10:  # Long yardage - more passing
            run_prob = 0.25
            pass_prob = 0.75
        
        # Adjust based on down
        if down >= 3 and yards_for_first > 5:  # 3rd/4th and long - mostly passing
            run_prob = 0.15
            pass_prob = 0.85
        
        # Goal line situations - more running
        if yards_to_goal <= 5:
            run_prob = 0.70
            pass_prob = 0.30
        
        return "run" if random.random() < run_prob else "pass"
    
    def _simulate_run_play(self, success_rating: float, yards_to_goal: int) -> int:
        """Simulate a running play."""
        # Base yards for running play - more aggressive improvement
        base_yards = 4.2  # Improved further from 3.8
        
        # Success rating affects average
        adjusted_avg = base_yards + (success_rating * 2.5)  # Improved from 2.2
        
        # Apply weather effects
        if self.weather_effects:
            adjusted_avg *= self.weather_effects.rushing_yards_modifier
        
        # Use normal distribution for realistic yard distribution
        yards = np.random.normal(adjusted_avg, 2.5)
        
        # Cap at reasonable values
        yards = max(-3, min(yards, 25))
        
        # Goal line adjustments
        if yards_to_goal <= 5:
            yards = max(0, min(yards, yards_to_goal + 2))
        
        return int(round(yards))
    
    def _simulate_pass_play(self, success_rating: float, yards_for_first: int, yards_to_goal: int) -> int:
        """Simulate a passing play."""
        # Base completion probability - more aggressive improvement
        completion_prob = 0.70 + (success_rating * 0.20)  # Improved further
        completion_prob = max(0.45, min(0.90, completion_prob))  # Much better bounds
        
        # Apply weather effects to completion probability
        if self.weather_effects:
            completion_prob *= self.weather_effects.passing_accuracy_modifier
            completion_prob *= self.weather_effects.visibility_modifier
            completion_prob = max(0.15, min(0.90, completion_prob))
        
        if random.random() < completion_prob:
            # Completed pass
            base_yards = 8.5  # Improved from 7.5
            
            # Adjust for distance needed
            if yards_for_first > 10:
                base_yards = yards_for_first * 0.90  # Improved from 0.85
            
            # Success rating affects average
            adjusted_avg = base_yards + (success_rating * 4.0)  # Improved from 3.5
            
            # Apply weather effects to passing distance
            if self.weather_effects:
                adjusted_avg *= self.weather_effects.passing_distance_modifier
            
            yards = np.random.normal(adjusted_avg, 4.0)
            
            # Cap at reasonable values
            yards = max(0, min(yards, 40))
            
            # Goal line adjustments
            if yards_to_goal <= 10:
                yards = max(0, min(yards, yards_to_goal + 2))
        else:
            # Incomplete pass
            yards = 0
        
        return int(round(yards))
    
    def _simulate_special_play(self, success_rating: float) -> int:
        """Simulate special plays (trick plays, etc.)."""
        # Special plays are high risk, high reward
        if random.random() < 0.3 + (success_rating * 0.2):
            # Success - big gain
            return random.randint(8, 25)
        else:
            # Failure - loss or no gain
            return random.randint(-5, 2)
    
    def _calculate_turnover_chance(self, play_type: str, success_rating: float, down: int) -> float:
        """Calculate chance of turnover on this play."""
        base_turnover = 0.015  # Reduced from 2% to 1.5%
        
        if play_type == "pass":
            base_turnover = 0.018  # Reduced interception rate
        elif play_type == "run":
            base_turnover = 0.012  # Reduced fumble rate
        
        # Success rating affects turnover chance (better teams turn it over less)
        turnover_chance = base_turnover - (success_rating * 0.015)  # Increased skill factor
        
        # Apply weather effects to turnover chance
        if self.weather_effects:
            if play_type == "run":
                # Weather affects fumble chance
                turnover_chance *= self.weather_effects.fumble_chance_modifier
            else:
                # Poor visibility and field conditions can affect interceptions
                visibility_effect = 2.0 - self.weather_effects.visibility_modifier  # Invert (worse visibility = more turnovers)
                field_effect = 2.0 - self.weather_effects.field_condition_modifier
                turnover_chance *= (visibility_effect + field_effect) / 2.0
        
        # Pressure situations increase turnovers
        if down >= 3:
            turnover_chance *= 1.5
        
        return max(0.005, min(0.12, turnover_chance))  # Keep between 0.5% and 12% (increased max for weather)
    
    def _attempt_field_goal(self, offense: Team, yards_to_goal: int, is_home: bool) -> bool:
        """Attempt a field goal."""
        # Field goal distance (add 17 yards for end zone and snap)
        fg_distance = yards_to_goal + 17
        
        # Base success rate depends on distance - improved rates
        if fg_distance <= 30:
            base_success = 0.98  # Very high for short kicks
        elif fg_distance <= 40:
            base_success = 0.90  # Improved from 0.85
        elif fg_distance <= 50:
            base_success = 0.78  # Improved from 0.70
        else:
            base_success = 0.58  # Improved from 0.50
        
        # Team special teams rating affects success
        st_rating = getattr(offense.stats, 'kicking_game', 75)  # Use kicking_game rating
        rating_modifier = (st_rating - 75) / 100.0  # Normalize around 75
        
        # Home field advantage
        home_bonus = 0.05 if is_home else 0.0
        
        success_prob = base_success + rating_modifier + home_bonus
        
        # Apply weather effects to field goal accuracy
        if self.weather_effects:
            success_prob *= self.weather_effects.kicking_accuracy_modifier
            # Adjust for distance effects from weather (wind/conditions)
            distance_factor = 1.0
            if fg_distance > 40:  # Longer kicks more affected by weather
                distance_factor = self.weather_effects.kicking_distance_modifier
                success_prob *= distance_factor
        
        success_prob = max(0.15, min(0.98, success_prob))
        
        return random.random() < success_prob

    def _simulate_overtime(self, home_team: Team, away_team: Team) -> Tuple[int, int]:
        """
        Simulate overtime period (simplified sudden death).
        
        Returns:
            Tuple of (home_points, away_points)
        """
        self.logger.info("Simulating overtime")
        
        # Coin toss to determine first possession (simplified - random choice)
        first_team = home_team if random.random() < 0.5 else away_team
        second_team = away_team if first_team == home_team else home_team
          # First team's drive (start at 25-yard line for overtime)
        first_is_home = (first_team == home_team)
        first_drive = self._simulate_drive_with_time(first_team, second_team, first_is_home, 25, 900)  # 15 minutes max
        
        if first_drive['points'] >= 7:  # Touchdown ends the game
            if first_team == home_team:
                return first_drive['points'], 0
            else:
                return 0, first_drive['points']
        
        # Second team gets a chance (also starts at 25-yard line)
        second_is_home = (second_team == home_team)
        second_drive = self._simulate_drive_with_time(second_team, first_team, second_is_home, 25, 900)  # 15 minutes max
        
        # Return points based on which team scored
        if first_team == home_team:
            return first_drive['points'], second_drive['points']
        else:
            return second_drive['points'], first_drive['points']

    def _update_team_records(self, result: GameResult) -> None:
        """Update team win/loss records based on game result."""
        if result.home_score > result.away_score:
            # Home team wins
            result.home_team.wins += 1
            result.away_team.losses += 1
        elif result.away_score > result.home_score:
            # Away team wins  
            result.away_team.wins += 1
            result.home_team.losses += 1
        else:
            # Tie game
            result.home_team.ties += 1
            result.away_team.ties += 1

    def _simulate_kickoff(self, kicking_team: Team, receiving_team: Team) -> int:
        """
        Simulate a kickoff return.
        
        Args:
            kicking_team: Team performing the kickoff
            receiving_team: Team receiving the kickoff
            
        Returns:
            Starting field position for the receiving team (0-100)
        """
        # Kickoff return average is around 23-25 yards from the 25-yard line
        # This puts the ball around the 25-30 yard line typically
        base_return = 25
        
        # Add some variance based on team special teams ratings
        kicking_strength = kicking_team.stats.kicking_game / 100.0
        return_strength = receiving_team.stats.return_game / 100.0
        
        # Calculate return distance with some randomness
        return_variance = random.normalvariate(0, 8)  # Standard deviation of 8 yards
        return_distance = base_return + return_variance + (return_strength - kicking_strength) * 5
        
        # Clamp to reasonable bounds (10-50 yard line)
        return_distance = max(10, min(50, return_distance))
        
        self.logger.debug(f"Kickoff return: {receiving_team.name} starts at {return_distance}-yard line")
        return int(return_distance)

    def _handle_drive_transition(self, drive_result: dict, offense: Team, defense: Team) -> dict:
        """
        Handle the transition between drives based on the previous drive result.
        
        Args:
            drive_result: Result of the previous drive
            offense: Team that had possession
            defense: Team that was defending
            
        Returns:
            Dictionary with next possession team and field position
        """
        result_type = drive_result['result']
        final_position = drive_result['final_field_position']
        
        if result_type in ['touchdown', 'field_goal']:
            # Scoring play - kickoff to other team
            next_team = defense
            next_opponent = offense
            field_position = self._simulate_kickoff(offense, defense)
            
        elif result_type == 'turnover':
            # Turnover - defense takes over at current position
            next_team = defense
            next_opponent = offense
            # Defense gets ball where turnover occurred
            field_position = 100 - final_position  # Flip field position
            
        elif result_type == 'punt':
            # Punt - simulate punt return
            next_team = defense
            next_opponent = offense
            field_position = self._simulate_punt(offense, defense, final_position)
            
        elif result_type == 'missed_fg':
            # Missed field goal - defense gets ball at spot of attempt
            next_team = defense
            next_opponent = offense
            field_position = 100 - final_position  # Flip field position
            
        else:
            # Default case - shouldn't happen but handle gracefully
            next_team = defense
            next_opponent = offense
            field_position = 20  # Default starting position
            
        return {
            'team': next_team,
            'opponent': next_opponent,
            'field_position': field_position
        }

    def _simulate_punt(self, punting_team: Team, receiving_team: Team, punt_from: int) -> int:
        """
        Simulate a punt and return.
        
        Args:
            punting_team: Team punting the ball
            receiving_team: Team receiving the punt
            punt_from: Field position where punt occurred
            
        Returns:
            Starting field position for receiving team
        """
        # Average punt distance is around 40-45 yards
        base_punt_distance = 42
          # Add variance and team skill factors
        punt_variance = random.normalvariate(0, 8)
        punt_skill = punting_team.stats.kicking_game / 100.0
        return_skill = receiving_team.stats.return_game / 100.0
        
        # Calculate punt distance
        punt_distance = base_punt_distance + punt_variance + (punt_skill * 5)
        punt_distance = max(25, min(60, punt_distance))  # Reasonable bounds
        
        # Calculate where punt lands (from punting team's perspective)
        punt_lands_at = punt_from + punt_distance
        
        # Handle touchback
        if punt_lands_at >= 100:
            receiving_field_position = 20  # Touchback
        else:
            # Simulate return (usually 5-15 yards)
            return_distance = random.normalvariate(8, 4) + (return_skill * 3)
            return_distance = max(0, min(20, return_distance))
            
            # Calculate final position (from receiving team's perspective)
            receiving_field_position = 100 - punt_lands_at + return_distance
            receiving_field_position = max(1, min(99, receiving_field_position))
        
        self.logger.debug(f"Punt: {receiving_team.name} starts at {receiving_field_position}-yard line")
        return int(receiving_field_position)

    def _simulate_drive_with_time(self, offense: Team, defense: Team, is_home: bool, field_position: int, time_remaining: int) -> dict:
        """
        Simulate a single offensive drive with time tracking.
        
        Args:
            offense: Team with possession
            defense: Defending team
            is_home: Whether the offensive team is playing at home
            field_position: Starting field position (0-100, where 0 is offense's goal line)
            time_remaining: Time remaining in quarter (seconds)
            
        Returns:
            Dictionary with drive result, points scored, and time elapsed
        """
        yards_to_go = 100 - field_position  # Yards needed to reach end zone
        down = 1
        yards_for_first_down = 10
        plays_in_drive = 0
        max_plays = 20  # Safety limit to prevent infinite drives
        current_field_position = field_position
        drive_time_elapsed = 0
        
        # Initialize result variables
        result = None
        points = 0
        
        self.logger.debug(f"{offense.name} starting drive at {field_position}-yard line")
        
        while plays_in_drive < max_plays and drive_time_elapsed < time_remaining:
            plays_in_drive += 1
            
            # Simulate individual play with time
            play_result = self._simulate_play_with_time(offense, defense, is_home, down, yards_for_first_down, current_field_position)
            
            # Add time for this play
            drive_time_elapsed += play_result['time_elapsed']
            
            # Add play to reporting
            if self.reporter:
                self.reporter.add_play(
                    plays_in_drive, down, yards_for_first_down, current_field_position,
                    play_result['play_type'], play_result['yards_gained'], 
                    current_field_position + play_result['yards_gained']
                )
            
            # Update field position
            yards_gained = play_result['yards_gained']
            current_field_position += yards_gained
            yards_to_go = 100 - current_field_position
            yards_for_first_down -= yards_gained
            
            self.logger.debug(f"Play {plays_in_drive}: {play_result['play_type']} for {yards_gained} yards. "
                            f"At {current_field_position}-yard line, {down} down, {max(0, yards_for_first_down)} to go")
            
            # Check for scoring (field position >= 100 means touchdown)
            if current_field_position >= 100:
                if play_result['play_type'] == 'turnover':
                    result = "turnover"
                    points = 0
                else:
                    result = "touchdown"
                    points = 7  # TD + extra point
                    current_field_position = 100  # Cap at goal line for reporting
                break
            
            # Check for turnover
            if play_result['play_type'] == 'turnover':
                result = "turnover"
                points = 0
                break
            
            # Check for first down
            if yards_for_first_down <= 0:
                down = 1
                yards_for_first_down = 10
                continue
            
            # Advance down
            down += 1
            
            # Check for turnover on downs
            if down > 4:
                # Attempt field goal if in range (inside 45-yard line from goal, increased from 40)
                if current_field_position >= 55:  # Within field goal range (was 60)
                    fg_success = self._attempt_field_goal(offense, 100 - current_field_position, is_home)
                    if fg_success:
                        result = "field_goal"
                        points = 3
                    else:
                        result = "missed_fg"
                        points = 0
                else:
                    result = "punt"
                    points = 0
                break
        
        # If we hit time limit or max plays limit and no result was set
        if result is None:
            if drive_time_elapsed >= time_remaining:
                if down > 4:
                    result = "punt"
                    points = 0
                else:
                    # Drive ended due to time - preserve possession state
                    result = "end_of_quarter"
                    points = 0
            elif plays_in_drive >= max_plays:
                result = "punt"
                points = 0
            else:
                # This shouldn't happen, but provide a default
                result = "punt"
                points = 0

        self.logger.debug(f"{offense.name} drive result: {result} ({points} points) in {plays_in_drive} plays, {drive_time_elapsed}s")
        
        return {
            'result': result,
            'points': points,
            'plays': plays_in_drive,
            'final_field_position': current_field_position,
            'time_elapsed': drive_time_elapsed,
            'down': down,
            'yards_for_first_down': yards_for_first_down
        }

    def _simulate_play_with_time(self, offense: Team, defense: Team, is_home: bool, down: int, yards_for_first: int, yards_to_goal: int) -> dict:
        """
        Simulate a single play with time tracking.
        
        Args:
            offense: Team with possession
            defense: Defending team
            is_home: Whether the offensive team is playing at home
            down: Current down (1-4)
            yards_for_first: Yards needed for first down
            yards_to_goal: Yards to goal line
            
        Returns:
            Dictionary with play type, yards gained, and time elapsed
        """
        # Get normal play result
        play_result = self._simulate_play(offense, defense, is_home, down, yards_for_first, yards_to_goal)
        
        # Calculate time elapsed for this play
        time_elapsed = self._calculate_play_time(play_result['play_type'], play_result['yards_gained'], down)
        
        return {
            'play_type': play_result['play_type'],
            'yards_gained': play_result['yards_gained'],
            'time_elapsed': time_elapsed
        }

    def _calculate_play_time(self, play_type: str, yards_gained: int, down: int) -> int:
        """
        Calculate realistic time elapsed for a play.
        
        Args:
            play_type: Type of play (run, pass, turnover)
            yards_gained: Yards gained on the play
            down: Current down
            
        Returns:
            Time elapsed in seconds
        """
        if play_type == "run":
            # Running plays typically take less clock time
            if yards_gained > 0:
                # Successful runs - runner goes out of bounds sometimes
                if random.random() < 0.2:  # 20% chance of going out of bounds
                    play_time = random.randint(2, 4)  # Clock stops
                else:
                    play_time = random.randint(3, 6)  # Clock runs
            else:
                play_time = random.randint(2, 4)  # Tackle for loss
                
        elif play_type == "pass":
            if yards_gained > 0:
                # Completed pass
                if random.random() < 0.3:  # 30% chance of going out of bounds
                    play_time = random.randint(3, 5)  # Clock stops
                else:
                    play_time = random.randint(4, 7)  # Clock runs
            else:
                # Incomplete pass - clock stops
                play_time = random.randint(1, 3)
                
        elif play_type == "turnover":
            play_time = random.randint(3, 6)  # Fumble recovery or interception
            
        else:
            play_time = random.randint(3, 5)  # Default for special plays
        
        # Add time between plays (huddle, snap count, etc.)
        # This varies based on game situation
        if down >= 3:
            # More urgency on 3rd/4th down
            between_plays = random.randint(10, 20)
        else:
            between_plays = random.randint(15, 25)
        
        total_time = play_time + between_plays
        
        # Add some variance for timeouts, penalties, etc. (simplified)
        if random.random() < 0.03:  # 3% chance of extra delay
            total_time += random.randint(15, 45)
        
        return total_time
