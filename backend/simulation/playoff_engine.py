"""
Playoff engine for NFL-style postseason tournament.

Handles playoff seeding, bracket generation, and playoff game simulation
with proper advancement logic through Wild Card, Divisional, Conference
Championship, and Super Bowl rounds.
"""

import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from models.team import Team
from models.playoff import PlayoffBracket, PlayoffTeam, PlayoffGame, PlayoffRound
from simulation.season_engine import SeasonEngine, TeamRecord


class PlayoffEngine:
    """
    Core playoff management engine.
    
    Handles playoff qualification, seeding, bracket generation,
    and playoff game management with proper NFL playoff rules.
    """
    
    def __init__(self, season_engine: SeasonEngine):
        """
        Initialize playoff engine with completed regular season.
        
        Args:
            season_engine: Completed regular season with all games played
        """
        self.season_engine = season_engine
        self.bracket: Optional[PlayoffBracket] = None
        
    def generate_playoff_bracket(self) -> PlayoffBracket:
        """
        Generate the complete playoff bracket based on regular season results.
        
        Returns:
            Complete playoff bracket with seeded teams and initial matchups
        """
        # Get qualified teams for each conference
        afc_teams = self._get_playoff_teams('AFC')
        nfc_teams = self._get_playoff_teams('NFC')
        
        # Create bracket
        self.bracket = PlayoffBracket(
            season_year=self.season_engine.season_year,
            afc_teams=afc_teams,
            nfc_teams=nfc_teams
        )
        
        # Generate wild card games
        self._generate_wild_card_games()
        
        return self.bracket
    
    def _get_playoff_teams(self, conference: str) -> List[PlayoffTeam]:
        """
        Get the 7 playoff teams from a conference with proper seeding.
        
        Args:
            conference: 'AFC' or 'NFC'
            
        Returns:
            List of 7 playoff teams sorted by seed (1-7)
        """
        # Get all teams from this conference
        conference_teams = [
            record for record in self.season_engine.records.values()
            if record.team.conference == conference
        ]
        
        # Find division winners (4 teams)
        division_winners = self._get_division_winners(conference_teams)
        
        # Sort division winners by record for seeding 1-4
        division_winners.sort(key=lambda x: (
            -x.win_percentage,
            -x.point_differential,
            -x.division_wins,
            -x.conference_wins
        ))
        
        # Get remaining teams for wild card spots (3 teams)
        wild_card_candidates = [
            team for team in conference_teams 
            if team not in division_winners
        ]
        
        # Sort wild card candidates
        wild_card_candidates.sort(key=lambda x: (
            -x.win_percentage,
            -x.point_differential,
            -x.conference_wins,
            -x.points_for
        ))
        
        wild_card_teams = wild_card_candidates[:3]
        
        # Create playoff teams with seeding
        playoff_teams = []
        
        # Seeds 1-4: Division winners
        for i, team_record in enumerate(division_winners):
            playoff_teams.append(PlayoffTeam(
                team=team_record.team,
                seed=i + 1,
                division_winner=True,
                wild_card=False,
                wins=team_record.wins,
                losses=team_record.losses,
                ties=team_record.ties,
                win_percentage=team_record.win_percentage,
                points_for=team_record.points_for,
                points_against=team_record.points_against,
                point_differential=team_record.point_differential,
                division_wins=team_record.division_wins,
                conference_wins=team_record.conference_wins
            ))
        
        # Seeds 5-7: Wild card teams
        for i, team_record in enumerate(wild_card_teams):
            playoff_teams.append(PlayoffTeam(
                team=team_record.team,
                seed=i + 5,
                division_winner=False,
                wild_card=True,
                wins=team_record.wins,
                losses=team_record.losses,
                ties=team_record.ties,
                win_percentage=team_record.win_percentage,
                points_for=team_record.points_for,
                points_against=team_record.points_against,
                point_differential=team_record.point_differential,
                division_wins=team_record.division_wins,
                conference_wins=team_record.conference_wins
            ))
        
        return playoff_teams
    
    def _get_division_winners(self, conference_teams: List[TeamRecord]) -> List[TeamRecord]:
        """Get the 4 division winners from a conference."""
        divisions = defaultdict(list)
        
        # Group teams by division
        for team_record in conference_teams:
            division_key = f"{team_record.team.conference} {team_record.team.division}"
            divisions[division_key].append(team_record)
        
        # Get winner from each division
        winners = []
        for division, teams in divisions.items():
            if teams:
                winner = max(teams, key=lambda x: (
                    x.win_percentage,
                    x.point_differential,
                    x.division_wins,
                    x.conference_wins
                ))
                winners.append(winner)
        
        return winners
    
    def _generate_wild_card_games(self):
        """Generate the 6 wild card round games."""
        if not self.bracket:
            return
        
        # Wild Card Weekend schedule:
        # AFC: 2v7, 3v6, 4v5 (1 seed gets bye)
        # NFC: 2v7, 3v6, 4v5 (1 seed gets bye)
        
        base_date = datetime(self.season_engine.season_year, 1, 13)  # Mid-January
        
        game_counter = 1
        
        # AFC Wild Card games
        afc_matchups = [(2, 7), (3, 6), (4, 5)]
        for i, (higher, lower) in enumerate(afc_matchups):
            higher_seed = next(t for t in self.bracket.afc_teams if t.seed == higher)
            lower_seed = next(t for t in self.bracket.afc_teams if t.seed == lower)
            
            game = PlayoffGame(
                game_id=f"{self.season_engine.season_year}_WC_AFC_{game_counter}",
                round=PlayoffRound.WILD_CARD,
                conference="AFC",
                game_number=game_counter,
                higher_seed=higher_seed,
                lower_seed=lower_seed,
                scheduled_date=base_date + timedelta(days=i)
            )
            
            self.bracket.wild_card_games.append(game)
            game_counter += 1
        
        # NFC Wild Card games
        nfc_matchups = [(2, 7), (3, 6), (4, 5)]
        for i, (higher, lower) in enumerate(nfc_matchups):
            higher_seed = next(t for t in self.bracket.nfc_teams if t.seed == higher)
            lower_seed = next(t for t in self.bracket.nfc_teams if t.seed == lower)
            
            game = PlayoffGame(
                game_id=f"{self.season_engine.season_year}_WC_NFC_{game_counter}",
                round=PlayoffRound.WILD_CARD,
                conference="NFC",
                game_number=game_counter,
                higher_seed=higher_seed,
                lower_seed=lower_seed,
                scheduled_date=base_date + timedelta(days=i + 3)  # NFC games on different days
            )
            
            self.bracket.wild_card_games.append(game)
            game_counter += 1
    
    def advance_bracket(self, game_id: str, winner: Team, home_score: int, away_score: int, overtime: bool = False):
        """
        Process a playoff game result and advance the bracket.
        
        Args:
            game_id: ID of the completed game
            winner: Winning team
            home_score: Home team score
            away_score: Away team score
            overtime: Whether game went to overtime
        """
        if not self.bracket:
            return False
        
        # Find the game
        game = None
        for playoff_game in self.bracket.get_all_games():
            if playoff_game.game_id == game_id:
                game = playoff_game
                break
        
        if not game or not game.home_team or not game.away_team:
            return False
        
        # Update game result
        game.home_score = home_score
        game.away_score = away_score
        game.winner = winner
        game.overtime = overtime
        game.completed = True
        
        # Check if we can advance to next round
        if self.bracket.is_round_complete(self.bracket.current_round):
            self._advance_bracket_to_next_round()
        
        return True
    
    def _advance_bracket_to_next_round(self):
        """Advance the bracket to the next round and set up new games."""
        if not self.bracket:
            return
        
        if self.bracket.current_round == PlayoffRound.WILD_CARD:
            self.bracket.current_round = PlayoffRound.DIVISIONAL
            self._setup_divisional_games()
        elif self.bracket.current_round == PlayoffRound.DIVISIONAL:
            self.bracket.current_round = PlayoffRound.CONFERENCE_CHAMPIONSHIP
            self._setup_conference_championship_games()
        elif self.bracket.current_round == PlayoffRound.CONFERENCE_CHAMPIONSHIP:
            self.bracket.current_round = PlayoffRound.SUPER_BOWL
            self._setup_super_bowl()
    
    def _setup_conference_championship_games(self):
        """Set up conference championship games based on divisional results."""
        if not self.bracket:
            return
        
        # Get divisional round winners
        afc_winners = self._get_divisional_winners('AFC')
        nfc_winners = self._get_divisional_winners('NFC')
        
        base_date = datetime(self.season_engine.season_year, 1, 27)  # Conference championship weekend
        
        game_counter = 1
        
        # AFC Championship
        if len(afc_winners) >= 2:
            # Higher seed hosts
            afc_winners.sort(key=lambda x: x.seed)
            higher_seed = afc_winners[0]
            lower_seed = afc_winners[1]
            
            game = PlayoffGame(
                game_id=f"{self.season_engine.season_year}_CONF_AFC_{game_counter}",
                round=PlayoffRound.CONFERENCE_CHAMPIONSHIP,
                conference="AFC",
                game_number=game_counter,
                higher_seed=higher_seed,
                lower_seed=lower_seed,
                scheduled_date=base_date
            )
            self.bracket.conference_championship_games.append(game)
            game_counter += 1
        
        # NFC Championship
        if len(nfc_winners) >= 2:
            # Higher seed hosts
            nfc_winners.sort(key=lambda x: x.seed)
            higher_seed = nfc_winners[0]
            lower_seed = nfc_winners[1]
            
            game = PlayoffGame(
                game_id=f"{self.season_engine.season_year}_CONF_NFC_{game_counter}",
                round=PlayoffRound.CONFERENCE_CHAMPIONSHIP,
                conference="NFC",
                game_number=game_counter,
                higher_seed=higher_seed,
                lower_seed=lower_seed,
                scheduled_date=base_date + timedelta(days=1)
            )
            self.bracket.conference_championship_games.append(game)
    
    def _get_divisional_winners(self, conference: str) -> List[PlayoffTeam]:
        """Get divisional round winners from a conference."""
        winners = []
        if not self.bracket:
            return winners
            
        for game in self.bracket.divisional_games:
            if game.conference == conference and game.completed and game.winner:
                # Find the playoff team that matches the winner
                conf_teams = self.bracket.afc_teams if conference == 'AFC' else self.bracket.nfc_teams
                winner_team = next((t for t in conf_teams if t.team.abbreviation == game.winner.abbreviation), None)
                if winner_team:
                    winners.append(winner_team)
        
        return winners
    
    def _setup_super_bowl(self):
        """Set up Super Bowl based on conference championship results."""
        if not self.bracket:
            return
        
        # Get conference champions
        afc_champion = None
        nfc_champion = None
        
        for game in self.bracket.conference_championship_games:
            if game.completed and game.winner:
                if game.conference == 'AFC':
                    conf_teams = self.bracket.afc_teams
                    afc_champion = next((t for t in conf_teams if t.team.abbreviation == game.winner.abbreviation), None)
                    self.bracket.afc_champion = afc_champion
                elif game.conference == 'NFC':
                    conf_teams = self.bracket.nfc_teams
                    nfc_champion = next((t for t in conf_teams if t.team.abbreviation == game.winner.abbreviation), None)
                    self.bracket.nfc_champion = nfc_champion
        
        # Create Super Bowl game
        if afc_champion and nfc_champion:
            # Higher seed gets "home" field (neutral site but better designation)
            higher_seed = afc_champion if afc_champion.seed < nfc_champion.seed else nfc_champion
            lower_seed = nfc_champion if higher_seed == afc_champion else afc_champion
            
            super_bowl_date = datetime(self.season_engine.season_year, 2, 10)  # Second Sunday in February
            
            self.bracket.super_bowl = PlayoffGame(
                game_id=f"{self.season_engine.season_year}_SB_001",
                round=PlayoffRound.SUPER_BOWL,
                conference="NFL",  # Super Bowl is neutral
                game_number=1,
                higher_seed=higher_seed,
                lower_seed=lower_seed,
                scheduled_date=super_bowl_date
            )
    
    def _setup_divisional_games(self):
        """Set up divisional round games based on wild card results."""
        if not self.bracket:
            return
        
        # Get wild card winners by conference
        afc_winners = self._get_wild_card_winners('AFC')
        nfc_winners = self._get_wild_card_winners('NFC')
        
        base_date = datetime(self.season_engine.season_year, 1, 20)  # Divisional weekend
        
        # AFC Divisional games
        afc_1_seed = next(t for t in self.bracket.afc_teams if t.seed == 1)
        afc_matchups = self._create_divisional_matchups(afc_1_seed, afc_winners)
        
        game_counter = 1
        for i, (higher, lower) in enumerate(afc_matchups):
            game = PlayoffGame(
                game_id=f"{self.season_engine.season_year}_DIV_AFC_{game_counter}",
                round=PlayoffRound.DIVISIONAL,
                conference="AFC",
                game_number=game_counter,
                higher_seed=higher,
                lower_seed=lower,
                scheduled_date=base_date + timedelta(days=i)
            )
            self.bracket.divisional_games.append(game)
            game_counter += 1
        
        # NFC Divisional games
        nfc_1_seed = next(t for t in self.bracket.nfc_teams if t.seed == 1)
        nfc_matchups = self._create_divisional_matchups(nfc_1_seed, nfc_winners)
        
        for i, (higher, lower) in enumerate(nfc_matchups):
            game = PlayoffGame(
                game_id=f"{self.season_engine.season_year}_DIV_NFC_{game_counter}",
                round=PlayoffRound.DIVISIONAL,
                conference="NFC",
                game_number=game_counter,
                higher_seed=higher,
                lower_seed=lower,
                scheduled_date=base_date + timedelta(days=i + 2)
            )
            self.bracket.divisional_games.append(game)
            game_counter += 1
    
    def _get_wild_card_winners(self, conference: str) -> List[PlayoffTeam]:
        """Get wild card round winners from a conference."""
        winners = []
        if not self.bracket:
            return winners
            
        for game in self.bracket.wild_card_games:
            if game.conference == conference and game.completed and game.winner:
                # Find the playoff team that matches the winner
                conf_teams = self.bracket.afc_teams if conference == 'AFC' else self.bracket.nfc_teams
                winner_team = next((t for t in conf_teams if t.team.abbreviation == game.winner.abbreviation), None)
                if winner_team:
                    winners.append(winner_team)
        
        return winners
    
    def _create_divisional_matchups(self, one_seed: PlayoffTeam, wild_card_winners: List[PlayoffTeam]) -> List[Tuple[PlayoffTeam, PlayoffTeam]]:
        """Create divisional round matchups based on NFL reseeding rules."""
        # Sort winners by original seed
        wild_card_winners.sort(key=lambda x: x.seed)
        
        if len(wild_card_winners) < 2:
            return []
        
        # NFL rule: #1 seed plays lowest remaining seed
        # #2 seed (if still alive) plays the other team
        matchups = []
        
        # Find the lowest seed among winners for #1 seed
        lowest_seed = wild_card_winners[-1]  # Highest seed number = lowest seed
        matchups.append((one_seed, lowest_seed))
        
        # Remaining teams play each other
        remaining = [t for t in wild_card_winners if t != lowest_seed]
        if len(remaining) >= 2:
            # Sort by seed and pair them
            remaining.sort(key=lambda x: x.seed)
            matchups.append((remaining[0], remaining[1]))
        
        return matchups
    
    def get_bracket_status(self) -> Dict:
        """Get current playoff bracket status."""
        if not self.bracket:
            return {'error': 'No playoff bracket generated'}
        
        return self.bracket.to_dict()
    
    def get_next_playoff_games(self) -> List[PlayoffGame]:
        """Get the next playoff games that can be played."""
        if not self.bracket:
            return []
        
        return self.bracket.get_next_games_to_play()
    
    def is_playoffs_complete(self) -> bool:
        """Check if playoffs are completely finished."""
        if not self.bracket:
            return False
        
        return (self.bracket.current_round == PlayoffRound.SUPER_BOWL and
                self.bracket.super_bowl is not None and
                self.bracket.super_bowl.completed)


# Monkey patch the bracket methods to use the engine
def _setup_divisional_games_patch(self):
    """Setup divisional games - patched version."""
    # This will be called by the engine
    pass

def _setup_conference_championship_games_patch(self):
    """Setup conference championship games - patched version."""
    # This will be called by the engine
    pass

def _setup_super_bowl_patch(self):
    """Setup Super Bowl - patched version."""
    # This will be called by the engine
    pass

# Apply patches
PlayoffBracket._setup_divisional_games = _setup_divisional_games_patch
PlayoffBracket._setup_conference_championship_games = _setup_conference_championship_games_patch
PlayoffBracket._setup_super_bowl = _setup_super_bowl_patch