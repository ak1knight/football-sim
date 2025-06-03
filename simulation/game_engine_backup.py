"""
Game simulation engine for American football.

This module contains the core logic for simulating football games,
including play-by-play simulation, scoring, and game flow.
"""

import random
import logging
from dataclasses import dataclass
from typing import List, Tuple, Optional

from models.team import Team


@dataclass
class GameResult:
    """Result of a simulated game."""
    home_team: Team
    away_team: Team
    home_score: int
    away_score: int
    duration: int  # Game duration in minutes
    
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
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the game engine.
        
        Args:
            seed: Random seed for reproducible simulations
        """
        self.logger = logging.getLogger(__name__)
        self.seed = seed
        if seed is not None:
            random.seed(seed)

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
            
        self.logger.info(f"Starting simulation: {away_team.name} @ {home_team.name}")
        
        # Initialize scores
        home_score = 0
        away_score = 0
        
        # Simulate four quarters
        for quarter in range(1, 5):
            self.logger.info(f"Quarter {quarter}")
            
            quarter_home, quarter_away = self._simulate_quarter(
                home_team, away_team, quarter
            )
            home_score += quarter_home
            away_score += quarter_away
            
            self.logger.info(f"End Q{quarter}: {home_team.name} {home_score}, {away_team.name} {away_score}")
        
        # Check for overtime
        game_duration = 60  # Regular game duration
        if home_score == away_score:
            self.logger.info("Game tied, going to overtime")
            ot_home, ot_away = self._simulate_overtime(home_team, away_team)
            home_score += ot_home
            away_score += ot_away
            game_duration += 15  # Add overtime period
        
        result = GameResult(
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            duration=game_duration
        )
        
        # Update team records
        self._update_team_records(result)
        
        self.logger.info(f"Final: {home_team.name} {home_score}, {away_team.name} {away_score}")
        return result

    def _simulate_quarter(self, home_team: Team, away_team: Team, quarter: int) -> Tuple[int, int]:
        """
        Simulate one quarter of gameplay.
        
        Returns:
            Tuple of (home_points, away_points) scored in this quarter
        """
        home_points = 0
        away_points = 0
        
        # Each quarter has approximately 2-4 drives per team
        num_drives = random.randint(2, 4)
        
        for drive_num in range(num_drives):
            # Alternate possession (simplified)
            if drive_num % 2 == 0:
                # Home team has possession
                drive_result = self._simulate_drive(home_team, away_team, is_home=True)
                home_points += drive_result['points']
            else:
                # Away team has possession  
                drive_result = self._simulate_drive(away_team, home_team, is_home=False)
                away_points += drive_result['points']
        
        return home_points, away_points

    def _simulate_drive(self, offense: Team, defense: Team, is_home: bool) -> dict:
        """
        Simulate a single offensive drive.
        
        Args:
            offense: Team with possession
            defense: Defending team
            is_home: Whether the offensive team is playing at home
            
        Returns:
            Dictionary with drive result and points scored
        """
        # Calculate drive success probability
        success_prob = self._calculate_drive_probability(offense, defense, is_home)
        
        # Determine drive outcome
        outcome_roll = random.random()
        
        if outcome_roll < success_prob * 0.6:  # 60% of successful drives are TDs
            result = "touchdown"
        elif outcome_roll < success_prob * 0.9:  # 30% are field goals
            result = "field_goal"
        elif outcome_roll < success_prob:  # 10% reach red zone but don't score
            result = "failed_in_red_zone"
        else:
            result = "punt"
        
        points = self._calculate_points(result)
        
        self.logger.debug(f"{offense.name} drive: {result} ({points} points)")
        
        return {
            'result': result,
            'points': points
        }

    def _calculate_drive_probability(self, offense: Team, defense: Team, is_home: bool) -> float:
        """Calculate the probability of a successful drive."""
        # Base probability from team ratings
        off_rating = (offense.stats.offensive_rating + offense.stats.red_zone_efficiency) / 2
        def_rating = defense.stats.defensive_rating
        
        # Home field advantage
        home_bonus = 0.05 if is_home else 0.0
        
        # Calculate relative strength
        strength_diff = (off_rating - def_rating) / 100.0
        base_prob = 0.35 + (strength_diff * 0.3) + home_bonus
        
        # Keep probability in reasonable bounds
        return max(0.1, min(0.7, base_prob))

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
        
        # First team's drive
        first_is_home = (first_team == home_team)
        first_drive = self._simulate_drive(first_team, second_team, first_is_home)
        
        if first_drive['points'] >= 7:  # Touchdown ends the game
            if first_team == home_team:
                return first_drive['points'], 0
            else:
                return 0, first_drive['points']
        
        # Second team gets a chance
        second_is_home = (second_team == home_team)
        second_drive = self._simulate_drive(second_team, first_team, second_is_home)
        
        # Return points based on which team scored
        if first_team == home_team:
            return first_drive['points'], second_drive['points']
        else:
            return second_drive['points'], first_drive['points']

    def _calculate_success_probability(self, offensive_rating: float, defensive_rating: float) -> float:
        """Calculate success probability from raw offensive and defensive ratings."""
        # Calculate relative strength
        strength_diff = (offensive_rating - defensive_rating) / 100.0
        base_prob = 0.35 + (strength_diff * 0.3)
        
        # Keep probability in reasonable bounds
        return max(0.1, min(0.8, base_prob))
    
    def _calculate_points(self, outcome: str) -> int:
        """Calculate points for different play outcomes."""
        points_map = {
            'touchdown': 7,
            'field_goal': 3,
            'safety': 2,
            'missed_fg': 0,
            'punt': 0,
            'failed_in_red_zone': 0
        }
        return points_map.get(outcome, 0)

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
