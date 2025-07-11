"""
Player model for the football simulation.

This module defines the Player class with statistics and attributes
relevant to American football simulation.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum

class Position(Enum):
    """Player positions in American football."""
    # Offense
    QB = "Quarterback"
    RB = "Running Back"
    WR = "Wide Receiver"
    TE = "Tight End"
    OL = "Offensive Line"
    
    # Defense
    DL = "Defensive Line"
    LB = "Linebacker"
    CB = "Cornerback"
    S = "Safety"
    
    # Special Teams
    K = "Kicker"
    P = "Punter"

@dataclass
class PlayerStats:
    """Statistics for a player."""
    # General stats
    overall_rating: int = 70  # 0-100 scale
    speed: int = 70
    strength: int = 70
    awareness: int = 70
    
    # Offensive stats
    passing_accuracy: Optional[int] = None
    passing_power: Optional[int] = None
    rushing_ability: Optional[int] = None
    receiving_ability: Optional[int] = None
    blocking: Optional[int] = None
    
    # Defensive stats
    tackling: Optional[int] = None
    coverage: Optional[int] = None
    pass_rush: Optional[int] = None
    
    # Special teams
    kicking_accuracy: Optional[int] = None
    kicking_power: Optional[int] = None

@dataclass
class Player:
    """
    Represents a football player with position, stats, and attributes.
    """
    name: str
    position: Position
    jersey_number: int
    stats: PlayerStats
    age: int = 25
    years_pro: int = 2
    injury_status: bool = False  # False = healthy, True = injured
    
    def __post_init__(self):
        """Validate player data after initialization."""
        if not 1 <= self.jersey_number <= 99:
            raise ValueError("Jersey number must be between 1 and 99")
        
        if not 18 <= self.age <= 45:
            raise ValueError("Player age must be between 18 and 45")
            
        if not 0 <= self.stats.overall_rating <= 100:
            raise ValueError("Overall rating must be between 0 and 100")
    
    def is_available(self) -> bool:
        """Check if player is available to play (not injured)."""
        return not self.injury_status
    
    def get_position_group(self) -> str:
        """Get the general position group (Offense, Defense, Special Teams)."""
        offense_positions = {Position.QB, Position.RB, Position.WR, Position.TE, Position.OL}
        defense_positions = {Position.DL, Position.LB, Position.CB, Position.S}
        special_teams_positions = {Position.K, Position.P}
        
        if self.position in offense_positions:
            return "Offense"
        elif self.position in defense_positions:
            return "Defense"
        elif self.position in special_teams_positions:
            return "Special Teams"
        else:
            return "Unknown"
    
    def __str__(self) -> str:
        """String representation of the player."""
        return f"#{self.jersey_number} {self.name} ({self.position.value}) - OVR: {self.stats.overall_rating}"
