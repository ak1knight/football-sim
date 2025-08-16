"""
Season management engine for American football simulation.

This module handles season scheduling, standings tracking, playoff scenarios,
and provides APIs for frontend integration. Separates season management
from individual game simulation.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set, TYPE_CHECKING
from enum import Enum
from collections import defaultdict
from datetime import datetime, timedelta

from models.team import Team
from simulation.schedule_generators import ScheduleGenerator, NFLScheduleGenerator

if TYPE_CHECKING:
    from simulation.playoff_engine import PlayoffEngine


class GameStatus(Enum):
    """Status of a scheduled game."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    POSTPONED = "postponed"


class SeasonPhase(Enum):
    """Current phase of the season."""
    PRESEASON = "preseason"
    REGULAR_SEASON = "regular_season"
    PLAYOFFS = "playoffs"
    OFFSEASON = "offseason"


@dataclass
class ScheduledGame:
    """Represents a scheduled game in the season."""
    game_id: str
    home_team: Team
    away_team: Team
    week: int
    status: GameStatus = GameStatus.SCHEDULED
    scheduled_date: Optional[datetime] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    overtime: bool = False
    game_duration: int = 60  # minutes
    
    @property
    def is_completed(self) -> bool:
        """Check if the game has been completed."""
        return self.status == GameStatus.COMPLETED
    
    @property
    def winner(self) -> Optional[Team]:
        """Get the winning team if game is completed."""
        if not self.is_completed or self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None  # Tie game
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            'game_id': self.game_id,
            'home_team': {
                'name': self.home_team.name,
                'city': self.home_team.city,
                'abbreviation': self.home_team.abbreviation
            },
            'away_team': {
                'name': self.away_team.name,
                'city': self.away_team.city,
                'abbreviation': self.away_team.abbreviation
            },
            'week': self.week,
            'status': self.status.value,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'overtime': self.overtime,
            'winner': self.winner.abbreviation if self.winner else None
        }

    @staticmethod
    def from_dict(data: Dict, team_map: Dict[str, 'Team']) -> 'ScheduledGame':
        """Deserialize from dict (e.g., DB row), using a team_map of abbreviation->Team."""
        home_team = team_map[data['home_team_abbr']]
        away_team = team_map[data['away_team_abbr']]
        scheduled_date = (
            datetime.fromisoformat(data['scheduled_date']) if data.get('scheduled_date') else None
        )
        return ScheduledGame(
            game_id=data['game_id'],
            home_team=home_team,
            away_team=away_team,
            week=int(data['week']),
            status=GameStatus(data['status']) if 'status' in data else GameStatus.SCHEDULED,
            scheduled_date=scheduled_date,
            home_score=data.get('home_score'),
            away_score=data.get('away_score'),
            overtime=data.get('overtime', False),
            game_duration=data.get('game_duration', 60)
        )

    def to_db_dict(self) -> Dict:
        """Serialize for DB storage (flat, with team abbreviations)."""
        return {
            'game_id': self.game_id,
            'home_team_abbr': self.home_team.abbreviation,
            'away_team_abbr': self.away_team.abbreviation,
            'week': self.week,
            'status': self.status.value,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'overtime': self.overtime,
            'game_duration': self.game_duration
        }


@dataclass
class TeamRecord:
    """Team's record and statistics for the season."""
    team: Team
    wins: int = 0
    losses: int = 0
    ties: int = 0
    points_for: int = 0
    points_against: int = 0
    division_wins: int = 0
    division_losses: int = 0
    conference_wins: int = 0
    conference_losses: int = 0
    
    @property
    def win_percentage(self) -> float:
        """Calculate win percentage."""
        total_games = self.wins + self.losses + self.ties
        if total_games == 0:
            return 0.0
        return (self.wins + 0.5 * self.ties) / total_games
    
    @property
    def point_differential(self) -> int:
        """Calculate point differential."""
        return self.points_for - self.points_against
    
    @property
    def games_played(self) -> int:
        """Total games played."""
        return self.wins + self.losses + self.ties
    
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
            'wins': self.wins,
            'losses': self.losses,
            'ties': self.ties,
            'win_percentage': round(self.win_percentage, 3),
            'points_for': self.points_for,
            'points_against': self.points_against,
            'point_differential': self.point_differential,
            'division_record': f"{self.division_wins}-{self.division_losses}",
            'conference_record': f"{self.conference_wins}-{self.conference_losses}",
            'games_played': self.games_played
        }

    @staticmethod
    def from_dict(data: Dict, team: 'Team') -> 'TeamRecord':
        """Deserialize from dict (e.g., DB row), using a Team object."""
        return TeamRecord(
            team=team,
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            ties=data.get('ties', 0),
            points_for=data.get('points_for', 0),
            points_against=data.get('points_against', 0),
            division_wins=data.get('division_wins', 0),
            division_losses=data.get('division_losses', 0),
            conference_wins=data.get('conference_wins', 0),
            conference_losses=data.get('conference_losses', 0)
        )

    def to_db_dict(self) -> Dict:
        """Serialize for DB storage (flat, with team abbreviation)."""
        return {
            'team_abbr': self.team.abbreviation,
            'wins': self.wins,
            'losses': self.losses,
            'ties': self.ties,
            'points_for': self.points_for,
            'points_against': self.points_against,
            'division_wins': self.division_wins,
            'division_losses': self.division_losses,
            'conference_wins': self.conference_wins,
            'conference_losses': self.conference_losses
        }


class SeasonEngine:
    """
    Core season management engine.
    
    Handles scheduling, standings tracking, playoff scenarios,
    and provides clean APIs for frontend integration.
    """
    
    def __init__(self, teams: List[Team], season_year: int = 2024, seed: Optional[int] = None,
                 schedule_generator: Optional[ScheduleGenerator] = None,
                 current_week: Optional[int] = None,
                 current_phase: Optional[str] = None,
                 schedule: Optional[List[ScheduledGame]] = None,
                 records: Optional[Dict[str, TeamRecord]] = None,
                 completed_games: Optional[List[ScheduledGame]] = None):
        """
        Initialize the season engine.
        
        Args:
            teams: List of all teams in the league
            season_year: Year of the season
            seed: Random seed for reproducible scheduling
            schedule_generator: Optional schedule generator instance (defaults to NFLScheduleGenerator)
        """
        self.teams = teams
        self.season_year = season_year
        self.seed = seed
        self.schedule_generator = schedule_generator or NFLScheduleGenerator()
        if seed is not None:
            random.seed(seed)

        # State from DB or defaults
        self.current_week = current_week if current_week is not None else 1
        self.current_phase = SeasonPhase(current_phase) if current_phase else SeasonPhase.REGULAR_SEASON
        self.schedule: List[ScheduledGame] = schedule if schedule is not None else []
        self.records: Dict[str, TeamRecord] = records if records is not None else {t.abbreviation: TeamRecord(t) for t in teams}
        self.completed_games: List[ScheduledGame] = completed_games if completed_games is not None else []
        self.playoff_engine: Optional['PlayoffEngine'] = None

        # If no schedule provided, generate it
        if not self.schedule:
            self._generate_schedule()
    @staticmethod
    def from_db(
        teams: List[Team],
        season_year: int,
        db_schedule: List[Dict],
        db_records: List[Dict],
        current_week: int,
        current_phase: str,
        completed_games: Optional[List[Dict]] = None,
        schedule_generator: Optional[ScheduleGenerator] = None,
        seed: Optional[int] = None
    ) -> 'SeasonEngine':
        """
        Construct a SeasonEngine from DB data.
        - teams: list of Team objects
        - db_schedule: list of dicts (game rows)
        - db_records: list of dicts (team record rows)
        - completed_games: list of dicts (game rows)
        """
        team_map = {t.abbreviation: t for t in teams}
        schedule = [ScheduledGame.from_dict(g, team_map) for g in db_schedule]
        records = {r['team_abbr']: TeamRecord.from_dict(r, team_map[r['team_abbr']]) for r in db_records}
        completed = [ScheduledGame.from_dict(g, team_map) for g in (completed_games or [])]
        return SeasonEngine(
            teams=teams,
            season_year=season_year,
            seed=seed,
            schedule_generator=schedule_generator,
            current_week=current_week,
            current_phase=current_phase,
            schedule=schedule,
            records=records,
            completed_games=completed
        )

    def to_db(self) -> Dict:
        """
        Serialize the engine state for DB storage.
        Returns a dict with keys: schedule, records, completed_games, current_week, current_phase, season_year, seed
        """
        return {
            'season_year': self.season_year,
            'seed': self.seed,
            'current_week': self.current_week,
            'current_phase': self.current_phase.value,
            'schedule': [g.to_db_dict() for g in self.schedule],
            'records': [r.to_db_dict() for r in self.records.values()],
            'completed_games': [g.to_db_dict() for g in self.completed_games]
        }

    
    
    def _generate_schedule(self) -> None:
        """Generate the complete regular season schedule using the pluggable schedule generator."""
        self.schedule = []
        game_counter = 0
        
        # Week 1 start date (first Sunday in September)
        start_date = datetime(self.season_year, 9, 1)
        while start_date.weekday() != 6:  # Find first Sunday
            start_date += timedelta(days=1)
        
        # Use the schedule generator to create the weekly schedule
        weekly_schedule = self.schedule_generator.generate_schedule(self.teams, self.season_year, self.seed)
        
        # Convert the weekly schedule to ScheduledGame objects
        total_weeks = self.schedule_generator.get_total_weeks()
        
        for week in range(1, total_weeks + 1):
            if week in weekly_schedule:
                for home_team, away_team in weekly_schedule[week]:
                    game_id = f"{self.season_year}_W{week:02d}_G{game_counter:03d}"
                    game_date = start_date + timedelta(weeks=week-1)
                    
                    game = ScheduledGame(
                        game_id=game_id,
                        home_team=home_team,
                        away_team=away_team,
                        week=week,
                        scheduled_date=game_date
                    )
                    
                    self.schedule.append(game)
                    game_counter += 1
    
    def get_next_games(self, limit: int = 16) -> List[ScheduledGame]:
        """
        Get the next games that need to be simulated.
        
        Args:
            limit: Maximum number of games to return
            
        Returns:
            List of games ready to be simulated
        """
        next_games = []
        
        for game in self.schedule:
            if game.status == GameStatus.SCHEDULED and len(next_games) < limit:
                next_games.append(game)
            elif len(next_games) >= limit:
                break
        
        return next_games
    
    def get_week_games(self, week: int) -> List[ScheduledGame]:
        """
        Get all games for a specific week.
        
        Args:
            week: Week number
            
        Returns:
            List of games for that week
        """
        return [game for game in self.schedule if game.week == week]
    
    def process_game_result(self, game_id: str, home_score: int, away_score: int, 
                          overtime: bool = False, game_duration: int = 60) -> bool:
        """
        Process the result of a completed game and update standings.
        
        Args:
            game_id: Unique game identifier
            home_score: Home team's final score
            away_score: Away team's final score
            overtime: Whether the game went to overtime
            game_duration: Game duration in minutes
            
        Returns:
            True if game was found and processed, False otherwise
        """
        # Find the game
        game = None
        for scheduled_game in self.schedule:
            if scheduled_game.game_id == game_id:
                game = scheduled_game
                break
        
        if not game:
            return False
        
        # Update game result
        game.home_score = home_score
        game.away_score = away_score
        game.overtime = overtime
        game.game_duration = game_duration
        game.status = GameStatus.COMPLETED
        
        # Add to completed games
        self.completed_games.append(game)
        
        # Update team records
        self._update_team_records(game)
        
        # Check if we can advance to the next week
        self._check_week_advancement()
        
        return True
    
    def _update_team_records(self, game: ScheduledGame) -> None:
        """Update team records based on game result."""
        home_team = game.home_team
        away_team = game.away_team
        home_record = self.records[home_team.abbreviation]
        away_record = self.records[away_team.abbreviation]

        if game.home_score is None or game.away_score is None:
            return
        
        # Update points
        home_record.points_for += game.home_score
        home_record.points_against += game.away_score
        away_record.points_for += game.away_score
        away_record.points_against += game.home_score
        
        # Determine winner and update W/L records
        if game.home_score > game.away_score:
            # Home team wins
            home_record.wins += 1
            away_record.losses += 1
        elif game.away_score > game.home_score:
            # Away team wins
            away_record.wins += 1
            home_record.losses += 1
        else:
            # Tie game
            home_record.ties += 1
            away_record.ties += 1
        
        # Update division and conference records
        if self._is_division_game(home_team, away_team):
            if game.home_score > game.away_score:
                home_record.division_wins += 1
                away_record.division_losses += 1
            elif game.away_score > game.home_score:
                away_record.division_wins += 1
                home_record.division_losses += 1
        
        if self._is_conference_game(home_team, away_team):
            if game.home_score > game.away_score:
                home_record.conference_wins += 1
                away_record.conference_losses += 1
            elif game.away_score > game.home_score:
                away_record.conference_wins += 1
                home_record.conference_losses += 1
    
    def _is_division_game(self, team1: Team, team2: Team) -> bool:
        """Check if two teams are in the same division."""
        return (team1.conference == team2.conference and 
                team1.division == team2.division)
    
    def _is_conference_game(self, team1: Team, team2: Team) -> bool:
        """Check if two teams are in the same conference."""
        return team1.conference == team2.conference
    
    def _check_week_advancement(self) -> None:
        """Check if all games for current week are complete and advance if so."""
        current_week_games = self.get_week_games(self.current_week)
        
        if all(game.is_completed for game in current_week_games):
            self.current_week += 1
            
            # Check if regular season is complete
            if self.current_week > self.schedule_generator.get_total_weeks():
                self.current_phase = SeasonPhase.PLAYOFFS
                self._initialize_playoffs()
    
    def get_standings(self, by_division: bool = True) -> Dict:
        """
        Get current league standings.
        
        Args:
            by_division: Whether to organize by division (True) or conference (False)
            
        Returns:
            Dictionary containing standings organized by division/conference
        """
        if by_division:
            return self._get_division_standings()
        else:
            return self._get_conference_standings()
    
    def _get_division_standings(self) -> Dict:
        """Get standings organized by division."""
        divisions = defaultdict(list)
        
        for record in self.records.values():
            division_key = f"{record.team.conference} {record.team.division}"
            divisions[division_key].append(record)
        
        # Sort each division by record
        standings = {}
        for division, teams in divisions.items():
            sorted_teams = sorted(teams, key=lambda x: (
                -x.win_percentage,  # Higher win percentage first
                -x.point_differential,  # Higher point differential as tiebreaker
                -x.division_wins  # More division wins as secondary tiebreaker
            ))
            standings[division] = [team.to_dict() for team in sorted_teams]
        
        return standings
    
    def _get_conference_standings(self) -> Dict:
        """Get standings organized by conference."""
        conferences = defaultdict(list)
        
        for record in self.records.values():
            conferences[record.team.conference].append(record)
        
        # Sort each conference by record
        standings = {}
        for conference, teams in conferences.items():
            sorted_teams = sorted(teams, key=lambda x: (
                -x.win_percentage,
                -x.point_differential,
                -x.conference_wins
            ))
            standings[conference] = [team.to_dict() for team in sorted_teams]
        
        return standings
    
    def get_season_status(self) -> Dict:
        """Get comprehensive season status information."""
        total_games = len(self.schedule)
        completed_games = len(self.completed_games)
        total_weeks = self.schedule_generator.get_total_weeks()
        
        # Count all scheduled games (not just next 16)
        scheduled_games = sum(1 for game in self.schedule if game.status == GameStatus.SCHEDULED)
        
        return {
            'season_year': self.season_year,
            'current_week': self.current_week,
            'current_phase': self.current_phase.value,
            'total_games': total_games,
            'completed_games': completed_games,
            'completion_percentage': round((completed_games / total_games) * 100, 1) if total_games > 0 else 0,
            'next_games_count': scheduled_games,
            'weeks_remaining': max(0, total_weeks - self.current_week + 1) if self.current_phase == SeasonPhase.REGULAR_SEASON else 0,
            'schedule_type': self.schedule_generator.get_schedule_name() if hasattr(self.schedule_generator, 'get_schedule_name') else 'Custom Schedule'
        }
    
    def get_team_schedule(self, team_abbreviation: str) -> List[Dict]:
        """
        Get complete schedule for a specific team.
        
        Args:
            team_abbreviation: Team's abbreviation (e.g., 'KC', 'BUF')
            
        Returns:
            List of games for the team
        """
        team_games = []
        
        for game in self.schedule:
            if (game.home_team.abbreviation == team_abbreviation or 
                game.away_team.abbreviation == team_abbreviation):
                
                game_dict = game.to_dict()
                # Add opponent information
                if game.home_team.abbreviation == team_abbreviation:
                    game_dict['is_home'] = True
                    game_dict['opponent'] = game_dict['away_team']
                else:
                    game_dict['is_home'] = False
                    game_dict['opponent'] = game_dict['home_team']
                
                team_games.append(game_dict)
        
        return team_games
    
    def get_playoff_picture(self) -> Dict:
        """
        Get current playoff standings and scenarios.
        
        Returns:
            Dictionary with playoff information for each conference
        """
        if self.current_phase != SeasonPhase.REGULAR_SEASON:
            return {}
        
        # Get conference standings
        conf_standings = self._get_conference_standings()
        
        playoff_picture = {}
        
        for conference, teams in conf_standings.items():
            # In NFL: 7 playoff teams per conference
            # 4 division winners + 3 wild cards
            playoff_teams = teams[:7] if len(teams) >= 7 else teams
            
            playoff_picture[conference] = {
                'playoff_teams': playoff_teams,
                'division_leaders': self._get_division_leaders(conference),
                'wild_card_race': teams[4:10] if len(teams) > 4 else [],
                'eliminated_teams': teams[7:] if len(teams) > 7 else []
            }
        
        return playoff_picture
    
    def _get_division_leaders(self, conference: str) -> List[Dict]:
        """Get division leaders for a conference."""
        divisions = defaultdict(list)
        
        for record in self.records.values():
            if record.team.conference == conference:
                division_key = f"{record.team.conference} {record.team.division}"
                divisions[division_key].append(record)
        
        leaders = []
        for division, teams in divisions.items():
            if teams:
                leader = max(teams, key=lambda x: (
                    x.win_percentage,
                    x.point_differential,
                    x.division_wins
                ))
                leader_dict = leader.to_dict()
                leader_dict['division'] = division
                leaders.append(leader_dict)
        
        return leaders
    
    def _initialize_playoffs(self) -> None:
        """Initialize playoff engine when regular season ends."""
        try:
            # Import here to avoid circular imports
            from simulation.playoff_engine import PlayoffEngine
            
            self.playoff_engine = PlayoffEngine(self)
            if self.playoff_engine:
                self.playoff_engine.generate_playoff_bracket()
        except ImportError:
            # Fallback if playoff engine not available
            pass
    
    def get_playoff_bracket(self) -> Optional[Dict]:
        """
        Get the current playoff bracket.
        
        Returns:
            Playoff bracket data or None if not in playoffs
        """
        if self.current_phase != SeasonPhase.PLAYOFFS or not self.playoff_engine:
            return None
        
        return self.playoff_engine.get_bracket_status()
    
    def get_next_playoff_games(self) -> List[Dict]:
        """
        Get the next playoff games that can be played.
        
        Returns:
            List of playoff games ready to be played
        """
        if self.current_phase != SeasonPhase.PLAYOFFS or not self.playoff_engine:
            return []
        
        games = self.playoff_engine.get_next_playoff_games()
        return [game.to_dict() for game in games]
    
    def process_playoff_game_result(self, game_id: str, home_score: int, away_score: int,
                                  overtime: bool = False) -> bool:
        """
        Process a playoff game result.
        
        Args:
            game_id: Playoff game identifier
            home_score: Home team score
            away_score: Away team score
            overtime: Whether game went to overtime
            
        Returns:
            True if game was processed successfully
        """
        if self.current_phase != SeasonPhase.PLAYOFFS or not self.playoff_engine:
            return False
        
        # Determine winner
        if home_score > away_score:
            # Find home team from game
            playoff_games = self.playoff_engine.get_next_playoff_games()
            game = next((g for g in playoff_games if g.game_id == game_id), None)
            if not game or not game.home_team:
                return False
            winner = game.home_team
        elif away_score > home_score:
            # Find away team from game
            playoff_games = self.playoff_engine.get_next_playoff_games()
            game = next((g for g in playoff_games if g.game_id == game_id), None)
            if not game or not game.away_team:
                return False
            winner = game.away_team
        else:
            # Tie games not allowed in playoffs - this shouldn't happen
            return False
        
        # Process the result
        return self.playoff_engine.advance_bracket(game_id, winner, home_score, away_score, overtime)
    
    def is_season_complete(self) -> bool:
        """
        Check if the entire season (including playoffs) is complete.
        
        Returns:
            True if season is completely finished
        """
        if self.current_phase == SeasonPhase.PLAYOFFS:
            return self.playoff_engine.is_playoffs_complete() if self.playoff_engine else False
        elif self.current_phase == SeasonPhase.OFFSEASON:
            return True
        else:
            return False
