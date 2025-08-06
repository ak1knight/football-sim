"""
Season management API for the football simulation engine.

Provides REST API endpoints for season management, scheduling,
standings tracking, and game result processing.
"""

from typing import Dict, List, Optional, Any
from dataclasses import asdict

from simulation.season_engine import SeasonEngine, SeasonPhase, GameStatus
from data.team_loader import load_sample_teams


class SeasonAPI:
    """
    REST API for season management.
    
    Handles season creation, game scheduling, result processing,
    and standings queries for frontend integration.
    """
    
    def __init__(self):
        """Initialize the Season API."""
        self.current_season: Optional[SeasonEngine] = None
        self.teams = load_sample_teams()
    
    def create_season(self, season_year: int = 2024, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a new season.
        
        Args:
            season_year: Year for the season
            seed: Random seed for reproducible scheduling
            
        Returns:
            Season creation confirmation and initial status
        """
        try:
            self.current_season = SeasonEngine(
                teams=self.teams,
                season_year=season_year,
                seed=seed
            )
            
            return {
                'success': True,
                'message': f'Season {season_year} created successfully',
                'season_status': self.current_season.get_season_status(),
                'total_teams': len(self.teams),
                'total_games': len(self.current_season.schedule)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create season: {str(e)}'
            }
    
    def get_season_status(self) -> Dict[str, Any]:
        """
        Get current season status.
        
        Returns:
            Current season information and progress
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            status = self.current_season.get_season_status()
            
            return {
                'success': True,
                'season_status': status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get season status: {str(e)}'
            }
    
    def get_next_games(self, limit: int = 16) -> Dict[str, Any]:
        """
        Get next games that need to be simulated.
        
        Args:
            limit: Maximum number of games to return
            
        Returns:
            List of games ready for simulation
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            next_games = self.current_season.get_next_games(limit)
            
            return {
                'success': True,
                'games': [game.to_dict() for game in next_games],
                'count': len(next_games),
                'current_week': self.current_season.current_week
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get next games: {str(e)}'
            }
    
    def get_week_games(self, week: int) -> Dict[str, Any]:
        """
        Get all games for a specific week.
        
        Args:
            week: Week number (1-18 for regular season)
            
        Returns:
            List of games for the specified week
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            week_games = self.current_season.get_week_games(week)
            
            return {
                'success': True,
                'week': week,
                'games': [game.to_dict() for game in week_games],
                'count': len(week_games)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get week {week} games: {str(e)}'
            }
    
    def submit_game_result(self, game_id: str, home_score: int, away_score: int,
                          overtime: bool = False, game_duration: int = 60) -> Dict[str, Any]:
        """
        Submit the result of a completed game.
        
        Args:
            game_id: Unique game identifier
            home_score: Home team's final score
            away_score: Away team's final score
            overtime: Whether game went to overtime
            game_duration: Game duration in minutes
            
        Returns:
            Confirmation of result processing and updated standings
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            # Validate scores
            if home_score < 0 or away_score < 0:
                return {
                    'success': False,
                    'error': 'Scores cannot be negative'
                }
            
            # Process the game result
            success = self.current_season.process_game_result(
                game_id=game_id,
                home_score=home_score,
                away_score=away_score,
                overtime=overtime,
                game_duration=game_duration
            )
            
            if not success:
                return {
                    'success': False,
                    'error': f'Game {game_id} not found or already completed'
                }
            
            # Get updated season status
            season_status = self.current_season.get_season_status()
            
            return {
                'success': True,
                'message': f'Game {game_id} result processed successfully',
                'game_result': {
                    'game_id': game_id,
                    'home_score': home_score,
                    'away_score': away_score,
                    'overtime': overtime,
                    'duration': game_duration
                },
                'season_status': season_status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to process game result: {str(e)}'
            }
    
    def get_standings(self, by_division: bool = True) -> Dict[str, Any]:
        """
        Get current league standings.
        
        Args:
            by_division: Whether to organize by division (True) or conference (False)
            
        Returns:
            Current standings organized by division or conference
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            standings = self.current_season.get_standings(by_division=by_division)
            
            return {
                'success': True,
                'standings': standings,
                'organization': 'division' if by_division else 'conference',
                'last_updated': self.current_season.current_week
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get standings: {str(e)}'
            }
    
    def get_team_schedule(self, team_abbreviation: str) -> Dict[str, Any]:
        """
        Get complete schedule for a specific team.
        
        Args:
            team_abbreviation: Team's abbreviation (e.g., 'KC', 'BUF')
            
        Returns:
            Complete schedule for the team
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            # Validate team exists
            team_abbreviations = [team.abbreviation for team in self.teams]
            if team_abbreviation not in team_abbreviations:
                return {
                    'success': False,
                    'error': f'Team {team_abbreviation} not found'
                }
            
            schedule = self.current_season.get_team_schedule(team_abbreviation)
            
            # Get team record
            team_record = self.current_season.records.get(team_abbreviation)
            
            return {
                'success': True,
                'team': team_abbreviation,
                'schedule': schedule,
                'record': team_record.to_dict() if team_record else None,
                'total_games': len(schedule)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get team schedule: {str(e)}'
            }
    
    def get_playoff_picture(self) -> Dict[str, Any]:
        """
        Get current playoff standings and scenarios.
        
        Returns:
            Playoff picture for both conferences
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            playoff_picture = self.current_season.get_playoff_picture()
            
            if not playoff_picture:
                return {
                    'success': True,
                    'message': 'Playoffs not applicable in current season phase',
                    'current_phase': self.current_season.current_phase.value
                }
            
            return {
                'success': True,
                'playoff_picture': playoff_picture,
                'current_week': self.current_season.current_week
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get playoff picture: {str(e)}'
            }
    
    def get_all_teams(self) -> Dict[str, Any]:
        """
        Get all available teams.
        
        Returns:
            List of all teams with basic information
        """
        try:
            teams_data = []
            for team in self.teams:
                teams_data.append({
                    'name': team.name,
                    'city': team.city,
                    'abbreviation': team.abbreviation,
                    'conference': team.conference,
                    'division': team.division
                })
            
            # Organize by conference and division
            organized_teams = {}
            for team_data in teams_data:
                conf = team_data['conference']
                div = team_data['division']
                
                if conf not in organized_teams:
                    organized_teams[conf] = {}
                if div not in organized_teams[conf]:
                    organized_teams[conf][div] = []
                
                organized_teams[conf][div].append(team_data)
            
            return {
                'success': True,
                'teams': teams_data,
                'organized_teams': organized_teams,
                'total_teams': len(teams_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get teams: {str(e)}'
            }
    
    def simulate_through_week(self, target_week: int) -> Dict[str, Any]:
        """
        Get all games that need to be simulated through a target week.
        
        Args:
            target_week: Week to simulate through (1-18)
            
        Returns:
            List of games to simulate in order
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            if target_week < 1 or target_week > 18:
                return {
                    'success': False,
                    'error': 'Week must be between 1 and 18'
                }
            
            if target_week < self.current_season.current_week:
                return {
                    'success': False,
                    'error': f'Target week {target_week} is in the past (current week: {self.current_season.current_week})'
                }
            
            # Get all games from current week through target week
            games_to_simulate = []
            for week in range(self.current_season.current_week, target_week + 1):
                week_games = self.current_season.get_week_games(week)
                for game in week_games:
                    if game.status == GameStatus.SCHEDULED:
                        games_to_simulate.append(game.to_dict())
            
            return {
                'success': True,
                'games_to_simulate': games_to_simulate,
                'count': len(games_to_simulate),
                'weeks_covered': list(range(self.current_season.current_week, target_week + 1))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get simulation plan: {str(e)}'
            }
    
    def get_playoff_bracket(self) -> Dict[str, Any]:
        """
        Get the current playoff bracket.
        
        Returns:
            Complete playoff bracket with all rounds and matchups
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            bracket = self.current_season.get_playoff_bracket()
            
            if not bracket:
                return {
                    'success': True,
                    'message': 'Playoffs not yet available',
                    'current_phase': self.current_season.current_phase.value,
                    'playoff_picture': self.current_season.get_playoff_picture()
                }
            
            return {
                'success': True,
                'bracket': bracket,
                'current_phase': self.current_season.current_phase.value
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get playoff bracket: {str(e)}'
            }
    
    def get_next_playoff_games(self) -> Dict[str, Any]:
        """
        Get the next playoff games that can be played.
        
        Returns:
            List of playoff games ready for simulation
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            games = self.current_season.get_next_playoff_games()
            
            return {
                'success': True,
                'games': games,
                'count': len(games),
                'current_phase': self.current_season.current_phase.value
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get next playoff games: {str(e)}'
            }
    
    def simulate_playoff_game(self, game_id: str, home_score: int, away_score: int,
                             overtime: bool = False) -> Dict[str, Any]:
        """
        Submit the result of a completed playoff game.
        
        Args:
            game_id: Playoff game identifier
            home_score: Home team's final score
            away_score: Away team's final score
            overtime: Whether game went to overtime
            
        Returns:
            Confirmation of result processing and updated bracket status
        """
        if not self.current_season:
            return {
                'success': False,
                'error': 'No active season'
            }
        
        try:
            # Validate scores
            if home_score < 0 or away_score < 0:
                return {
                    'success': False,
                    'error': 'Scores cannot be negative'
                }
            
            if home_score == away_score:
                return {
                    'success': False,
                    'error': 'Playoff games cannot end in ties'
                }
            
            # Process the playoff game result
            success = self.current_season.process_playoff_game_result(
                game_id=game_id,
                home_score=home_score,
                away_score=away_score,
                overtime=overtime
            )
            
            if not success:
                return {
                    'success': False,
                    'error': f'Playoff game {game_id} not found or could not be processed'
                }
            
            # Get updated bracket status
            bracket_status = self.current_season.get_playoff_bracket()
            
            return {
                'success': True,
                'message': f'Playoff game {game_id} result processed successfully',
                'game_result': {
                    'game_id': game_id,
                    'home_score': home_score,
                    'away_score': away_score,
                    'overtime': overtime
                },
                'bracket_status': bracket_status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to process playoff game result: {str(e)}'
            }
