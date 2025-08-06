"""
Playoff models and structures for the football simulation.

Defines playoff bracket structure, game types, and seeding logic
for NFL-style postseason tournament.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta

from models.team import Team


class PlayoffRound(Enum):
    """Playoff round types."""
    WILD_CARD = "wild_card"
    DIVISIONAL = "divisional"
    CONFERENCE_CHAMPIONSHIP = "conference_championship"
    SUPER_BOWL = "super_bowl"


class PlayoffSeed(Enum):
    """Playoff seeding numbers."""
    SEED_1 = 1
    SEED_2 = 2
    SEED_3 = 3
    SEED_4 = 4
    SEED_5 = 5
    SEED_6 = 6
    SEED_7 = 7


@dataclass
class PlayoffTeam:
    """Represents a team qualified for playoffs with seeding info."""
    team: Team
    seed: int
    division_winner: bool
    wild_card: bool
    wins: int
    losses: int
    ties: int
    win_percentage: float
    points_for: int
    points_against: int
    point_differential: int
    division_wins: int
    conference_wins: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            'team': {
                'name': self.team.name,
                'city': self.team.city,
                'abbreviation': self.team.abbreviation,
                'conference': self.team.conference,
                'division': self.team.division
            },
            'seed': self.seed,
            'division_winner': self.division_winner,
            'wild_card': self.wild_card,
            'record': f"{self.wins}-{self.losses}-{self.ties}",
            'win_percentage': round(self.win_percentage, 3),
            'points_for': self.points_for,
            'points_against': self.points_against,
            'point_differential': self.point_differential,
            'division_wins': self.division_wins,
            'conference_wins': self.conference_wins
        }


@dataclass
class PlayoffGame:
    """Represents a playoff game."""
    game_id: str
    round: PlayoffRound
    conference: str
    game_number: int  # Game number within the round
    higher_seed: Optional[PlayoffTeam]
    lower_seed: Optional[PlayoffTeam]
    home_team: Optional[Team] = None
    away_team: Optional[Team] = None
    scheduled_date: Optional[datetime] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    winner: Optional[Team] = None
    overtime: bool = False
    completed: bool = False
    
    def __post_init__(self):
        """Set home/away teams based on seeding."""
        if self.higher_seed and self.lower_seed:
            # Higher seed (lower number) gets home field advantage
            self.home_team = self.higher_seed.team
            self.away_team = self.lower_seed.team
    
    @property
    def is_ready_to_play(self) -> bool:
        """Check if both teams are determined."""
        return self.higher_seed is not None and self.lower_seed is not None
    
    @property
    def matchup_description(self) -> str:
        """Get a description of the matchup."""
        if not self.is_ready_to_play or not self.higher_seed or not self.lower_seed:
            return "TBD"
        
        return f"({self.higher_seed.seed}) {self.higher_seed.team.abbreviation} vs ({self.lower_seed.seed}) {self.lower_seed.team.abbreviation}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            'game_id': self.game_id,
            'round': self.round.value,
            'conference': self.conference,
            'game_number': self.game_number,
            'higher_seed': self.higher_seed.to_dict() if self.higher_seed else None,
            'lower_seed': self.lower_seed.to_dict() if self.lower_seed else None,
            'home_team': {
                'name': self.home_team.name,
                'city': self.home_team.city,
                'abbreviation': self.home_team.abbreviation
            } if self.home_team else None,
            'away_team': {
                'name': self.away_team.name,
                'city': self.away_team.city,
                'abbreviation': self.away_team.abbreviation
            } if self.away_team else None,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'winner': self.winner.abbreviation if self.winner else None,
            'overtime': self.overtime,
            'completed': self.completed,
            'matchup_description': self.matchup_description,
            'is_ready_to_play': self.is_ready_to_play
        }


@dataclass
class PlayoffBracket:
    """Represents the complete playoff bracket structure."""
    season_year: int
    afc_teams: List[PlayoffTeam] = field(default_factory=list)
    nfc_teams: List[PlayoffTeam] = field(default_factory=list)
    
    # Games by round and conference
    wild_card_games: List[PlayoffGame] = field(default_factory=list)
    divisional_games: List[PlayoffGame] = field(default_factory=list)
    conference_championship_games: List[PlayoffGame] = field(default_factory=list)
    super_bowl: Optional[PlayoffGame] = None
    
    # Championship winners
    afc_champion: Optional[PlayoffTeam] = None
    nfc_champion: Optional[PlayoffTeam] = None
    super_bowl_champion: Optional[PlayoffTeam] = None
    
    current_round: PlayoffRound = PlayoffRound.WILD_CARD
    
    def get_all_games(self) -> List[PlayoffGame]:
        """Get all playoff games in chronological order."""
        games = []
        games.extend(self.wild_card_games)
        games.extend(self.divisional_games)
        games.extend(self.conference_championship_games)
        if self.super_bowl:
            games.append(self.super_bowl)
        return games
    
    def get_games_by_round(self, round: PlayoffRound) -> List[PlayoffGame]:
        """Get games for a specific round."""
        if round == PlayoffRound.WILD_CARD:
            return self.wild_card_games
        elif round == PlayoffRound.DIVISIONAL:
            return self.divisional_games
        elif round == PlayoffRound.CONFERENCE_CHAMPIONSHIP:
            return self.conference_championship_games
        elif round == PlayoffRound.SUPER_BOWL:
            return [self.super_bowl] if self.super_bowl else []
        return []
    
    def get_next_games_to_play(self) -> List[PlayoffGame]:
        """Get the next games that can be played."""
        for round in PlayoffRound:
            games = self.get_games_by_round(round)
            ready_games = [game for game in games if game.is_ready_to_play and not game.completed]
            if ready_games:
                return ready_games
        return []
    
    def is_round_complete(self, round: PlayoffRound) -> bool:
        """Check if all games in a round are completed."""
        games = self.get_games_by_round(round)
        return all(game.completed for game in games)
    
    def advance_to_next_round(self) -> bool:
        """Advance to the next round if current round is complete."""
        if not self.is_round_complete(self.current_round):
            return False
        
        if self.current_round == PlayoffRound.WILD_CARD:
            self.current_round = PlayoffRound.DIVISIONAL
            self._setup_divisional_games()
        elif self.current_round == PlayoffRound.DIVISIONAL:
            self.current_round = PlayoffRound.CONFERENCE_CHAMPIONSHIP
            self._setup_conference_championship_games()
        elif self.current_round == PlayoffRound.CONFERENCE_CHAMPIONSHIP:
            self.current_round = PlayoffRound.SUPER_BOWL
            self._setup_super_bowl()
        elif self.current_round == PlayoffRound.SUPER_BOWL:
            # Playoffs complete
            return False
        
        return True
    
    def _setup_divisional_games(self):
        """Set up divisional round games based on wild card results."""
        # This will be implemented when we set up the bracket
        pass
    
    def _setup_conference_championship_games(self):
        """Set up conference championship games based on divisional results."""
        # This will be implemented when we set up the bracket
        pass
    
    def _setup_super_bowl(self):
        """Set up Super Bowl based on conference championship results."""
        # This will be implemented when we set up the bracket
        pass
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            'season_year': self.season_year,
            'current_round': self.current_round.value,
            'afc_teams': [team.to_dict() for team in self.afc_teams],
            'nfc_teams': [team.to_dict() for team in self.nfc_teams],
            'wild_card_games': [game.to_dict() for game in self.wild_card_games],
            'divisional_games': [game.to_dict() for game in self.divisional_games],
            'conference_championship_games': [game.to_dict() for game in self.conference_championship_games],
            'super_bowl': self.super_bowl.to_dict() if self.super_bowl else None,
            'afc_champion': self.afc_champion.to_dict() if self.afc_champion else None,
            'nfc_champion': self.nfc_champion.to_dict() if self.nfc_champion else None,
            'super_bowl_champion': self.super_bowl_champion.to_dict() if self.super_bowl_champion else None,
            'next_games': [game.to_dict() for game in self.get_next_games_to_play()],
            'is_complete': self.current_round == PlayoffRound.SUPER_BOWL and self.super_bowl and self.super_bowl.completed
        }