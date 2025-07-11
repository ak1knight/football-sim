"""
Team model for the football simulation.

This module defines the Team class with players, coaching staff,
and team-level statistics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.player import Player, Position

@dataclass
class TeamStats:
    """Team-level statistics and ratings."""
    # Offensive ratings (0-100)
    offensive_rating: int = 70
    passing_offense: int = 70
    rushing_offense: int = 70
    red_zone_efficiency: int = 70
    
    # Defensive ratings (0-100)
    defensive_rating: int = 70
    pass_defense: int = 70
    run_defense: int = 70
    red_zone_defense: int = 70
    
    # Special teams (0-100)
    kicking_game: int = 70
    return_game: int = 70
    
    # Coaching and intangibles
    coaching_rating: int = 70
    discipline: int = 70  # Fewer penalties
    conditioning: int = 70  # Less fatigue in 4th quarter
    
    # Home field advantage
    home_field_advantage: int = 3  # Points added when playing at home

@dataclass
class Team:
    """
    Represents a football team with players, stats, and metadata.
    """
    name: str
    city: str
    abbreviation: str
    conference: str  # "AFC" or "NFC"
    division: str   # "East", "West", "North", "South"
    
    players: List[Player] = field(default_factory=list)
    stats: TeamStats = field(default_factory=TeamStats)
    
    # Season record
    wins: int = 0
    losses: int = 0
    ties: int = 0
    
    def __post_init__(self):
        """Validate team data after initialization."""
        if self.conference not in ["AFC", "NFC"]:
            raise ValueError("Conference must be 'AFC' or 'NFC'")
        
        if self.division not in ["East", "West", "North", "South"]:
            raise ValueError("Division must be 'East', 'West', 'North', or 'South'")
    
    @property
    def full_name(self) -> str:
        """Get the full team name (city + team name)."""
        return f"{self.city} {self.name}"
    
    @property
    def record(self) -> str:
        """Get the team's win-loss-tie record as a string."""
        return f"{self.wins}-{self.losses}-{self.ties}"
    
    @property
    def win_percentage(self) -> float:
        """Calculate the team's winning percentage."""
        total_games = self.wins + self.losses + self.ties
        if total_games == 0:
            return 0.0
        return (self.wins + 0.5 * self.ties) / total_games
    
    def add_player(self, player: Player) -> None:
        """Add a player to the team roster."""
        # Check for duplicate jersey numbers
        existing_numbers = {p.jersey_number for p in self.players}
        if player.jersey_number in existing_numbers:
            raise ValueError(f"Jersey number {player.jersey_number} is already taken")
        
        self.players.append(player)
    
    def get_players_by_position(self, position: Position) -> List[Player]:
        """Get all players at a specific position."""
        return [player for player in self.players if player.position == position]
    
    def get_available_players(self) -> List[Player]:
        """Get all players who are available to play (not injured)."""
        return [player for player in self.players if player.is_available()]
    
    def get_starters_by_position_group(self, group: str) -> List[Player]:
        """
        Get starting players for a position group.
        
        Args:
            group: "Offense", "Defense", or "Special Teams"
        """
        position_players = [p for p in self.get_available_players() 
                          if p.get_position_group() == group]
        
        # Sort by overall rating and return top players
        position_players.sort(key=lambda p: p.stats.overall_rating, reverse=True)
        
        # Return appropriate number of starters based on group
        if group == "Offense":
            return position_players[:11]  # 11 offensive starters
        elif group == "Defense":
            return position_players[:11]  # 11 defensive starters
        else:  # Special Teams
            return position_players[:3]   # Key special teams players
    
    def get_team_overall_rating(self) -> int:
        """Calculate the team's overall rating based on player ratings."""
        if not self.players:
            return 0
        
        available_players = self.get_available_players()
        if not available_players:
            return 0
        
        # Weight by position importance and calculate average
        total_rating = sum(player.stats.overall_rating for player in available_players)
        return int(total_rating / len(available_players))
    
    def update_record(self, won: bool, tied: bool = False) -> None:
        """Update the team's win-loss record."""
        if tied:
            self.ties += 1
        elif won:
            self.wins += 1
        else:
            self.losses += 1
    
    def __str__(self) -> str:
        """String representation of the team."""
        return f"{self.full_name} ({self.record}) - OVR: {self.get_team_overall_rating()}"
