"""
Game reporter for detailed play-by-play and drive tracking.

This module provides detailed reporting capabilities for football simulations,
including play-by-play narratives and drive summaries.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.team import Team


@dataclass
class PlayReport:
    """Report for a single play."""    
    play_number: int
    down: int
    yards_to_go: int
    field_position: int
    play_type: str
    yards_gained: int
    new_field_position: int
    description: str


@dataclass
class DriveReport:
    """Report for a complete drive."""
    drive_number: int
    offense: str
    defense: str
    starting_position: int
    result: str = ""
    points: int = 0
    plays: List[PlayReport] = field(default_factory=list)
    total_plays: int = 0
    total_yards: int = 0
    time_of_possession: str = "0:00"  # Simplified for now


@dataclass
class QuarterReport:
    """Report for a quarter."""
    quarter: int
    drives: List[DriveReport] = field(default_factory=list)
    home_points: int = 0
    away_points: int = 0


@dataclass
class GameReport:
    """Complete game report with detailed information."""
    home_team: str
    away_team: str
    quarters: List[QuarterReport] = field(default_factory=list)
    final_home_score: int = 0
    final_away_score: int = 0
    game_duration: int = 60
    overtime: bool = False


class GameReporter:
    """
    Tracks and reports detailed game information.
    
    This class works alongside the GameEngine to provide detailed
    play-by-play reporting and drive summaries.
    """
    
    def __init__(self):
        """Initialize the game reporter."""
        self.current_game: Optional[GameReport] = None
        self.current_quarter: Optional[QuarterReport] = None
        self.current_drive: Optional[DriveReport] = None
        self.verbose = False
    
    def start_game(self, home_team: Team, away_team: Team, verbose: bool = False):
        """Start tracking a new game."""
        self.verbose = verbose
        self.current_game = GameReport(
            home_team=home_team.name,
            away_team=away_team.name
        )
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"GAME START: {away_team.name} @ {home_team.name}")
            print(f"{'='*60}")
    
    def start_quarter(self, quarter: int):
        """Start tracking a new quarter."""
        self.current_quarter = QuarterReport(quarter=quarter)
        if self.verbose:
            print(f"\n--- QUARTER {quarter} ---")
    
    def end_quarter(self, home_points: int, away_points: int):
        """End the current quarter."""
        if self.current_quarter and self.current_game:
            self.current_quarter.home_points = home_points
            self.current_quarter.away_points = away_points
            self.current_game.quarters.append(self.current_quarter)
            
            if self.verbose:
                total_home = sum(q.home_points for q in self.current_game.quarters)
                total_away = sum(q.away_points for q in self.current_game.quarters)
                print(f"End Q{self.current_quarter.quarter}: {self.current_game.home_team} {total_home}, {self.current_game.away_team} {total_away}")
    
    def start_drive(self, drive_number: int, offense: Team, defense: Team, field_position: int):
        """Start tracking a new drive."""
        self.current_drive = DriveReport(
            drive_number=drive_number,
            offense=offense.name,
            defense=defense.name,
            starting_position=field_position
        )
        
        if self.verbose:
            print(f"\nDrive {drive_number}: {offense.name} starting at {field_position}-yard line")
    
    def add_play(self, play_number: int, down: int, yards_to_go: int, field_position: int, 
                 play_type: str, yards_gained: int, new_field_position: int):
        """Add a play to the current drive."""
        if not self.current_drive:
            return
            
        # Create description
        description = self._create_play_description(
            down, yards_to_go, field_position, play_type, yards_gained, new_field_position
        )
        
        play_report = PlayReport(
            play_number=play_number,
            down=down,
            yards_to_go=yards_to_go,
            field_position=field_position,
            play_type=play_type,
            yards_gained=yards_gained,
            new_field_position=new_field_position,
            description=description
        )
        
        self.current_drive.plays.append(play_report)
        
        if self.verbose:
            print(f"  {play_number}: {description}")
    
    def end_drive(self, result: str, points: int, final_position: int):
        """End the current drive."""
        if not self.current_drive:
            return
            
        self.current_drive.result = result
        self.current_drive.points = points
        self.current_drive.total_plays = len(self.current_drive.plays)
        
        # Calculate total yards
        if self.current_drive.plays:
            self.current_drive.total_yards = sum(play.yards_gained for play in self.current_drive.plays)
        
        # Add to current quarter
        if self.current_quarter:
            self.current_quarter.drives.append(self.current_drive)
        
        if self.verbose:
            result_description = self._get_result_description(result, points)
            print(f"  Drive Result: {result_description}")
            print(f"  {self.current_drive.total_plays} plays, {self.current_drive.total_yards} yards")
    
    def end_game(self, home_score: int, away_score: int, duration: int, overtime: bool = False):
        """End the game and finalize the report."""
        if self.current_game is not None:
            self.current_game.final_home_score = home_score
            self.current_game.final_away_score = away_score
            self.current_game.game_duration = duration
            self.current_game.overtime = overtime
            
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"FINAL: {self.current_game.home_team} {home_score}, {self.current_game.away_team} {away_score}")
                if overtime:
                    print("Game went to overtime")
                print(f"{'='*60}")
    
    def get_game_summary(self) -> str:
        """Get a summary of the game."""
        if not self.current_game:
            return "No game data available"
        
        summary = []
        summary.append(f"Game: {self.current_game.away_team} @ {self.current_game.home_team}")
        summary.append(f"Final Score: {self.current_game.home_team} {self.current_game.final_home_score}, {self.current_game.away_team} {self.current_game.final_away_score}")
        
        if self.current_game.overtime:
            summary.append("Game went to overtime")
        
        summary.append(f"Duration: {self.current_game.game_duration} minutes")
        summary.append("")
        
        # Quarter by quarter
        for quarter in self.current_game.quarters:
            summary.append(f"Quarter {quarter.quarter}: {quarter.home_points} - {quarter.away_points}")
        
        return "\n".join(summary)
    
    def get_drive_summary(self) -> str:
        """Get a summary of all drives in the game."""
        if not self.current_game:
            return "No game data available"
        
        summary = []
        summary.append("DRIVE SUMMARY")
        summary.append("=" * 50)
        
        drive_count = 0
        for quarter in self.current_game.quarters:
            for drive in quarter.drives:
                drive_count += 1
                summary.append(f"\nDrive {drive_count}: {drive.offense} ({drive.total_plays} plays, {drive.total_yards} yards)")
                summary.append(f"  Started at {drive.starting_position}-yard line")
                summary.append(f"  Result: {self._get_result_description(drive.result, drive.points)}")
        
        return "\n".join(summary)
    
    def get_detailed_report(self) -> str:
        """Get a detailed play-by-play report."""
        if not self.current_game:
            return "No game data available"
        
        report = []
        report.append(f"DETAILED GAME REPORT")
        report.append("=" * 60)
        report.append(f"Game: {self.current_game.away_team} @ {self.current_game.home_team}")
        report.append(f"Final Score: {self.current_game.home_team} {self.current_game.final_home_score}, {self.current_game.away_team} {self.current_game.final_away_score}")
        report.append("")
        
        for quarter in self.current_game.quarters:
            report.append(f"\n--- QUARTER {quarter.quarter} ---")
            
            for drive in quarter.drives:
                report.append(f"\nDrive {drive.drive_number}: {drive.offense} starting at {drive.starting_position}-yard line")
                
                for play in drive.plays:
                    report.append(f"  {play.play_number}: {play.description}")
                
                result_desc = self._get_result_description(drive.result, drive.points)
                report.append(f"  Drive Result: {result_desc}")
                report.append(f"  {drive.total_plays} plays, {drive.total_yards} yards")
        
        return "\n".join(report)
    
    def _create_play_description(self, down: int, yards_to_go: int, field_position: int, 
                                play_type: str, yards_gained: int, new_field_position: int) -> str:
        """Create a human-readable description of a play."""
        down_text = self._get_down_text(down)
        
        if play_type == 'turnover':
            if yards_gained == 0:
                return f"{down_text} and {yards_to_go} at {field_position}: TURNOVER"
            else:
                return f"{down_text} and {yards_to_go} at {field_position}: TURNOVER after {yards_gained} yards"
        
        play_action = "run" if play_type == "run" else "pass"
        
        if yards_gained == 0:
            return f"{down_text} and {yards_to_go} at {field_position}: {play_action} for no gain"
        elif yards_gained < 0:
            return f"{down_text} and {yards_to_go} at {field_position}: {play_action} for {abs(yards_gained)} yard loss"
        else:
            if yards_gained >= yards_to_go:
                return f"{down_text} and {yards_to_go} at {field_position}: {play_action} for {yards_gained} yards, FIRST DOWN"
            else:
                return f"{down_text} and {yards_to_go} at {field_position}: {play_action} for {yards_gained} yards"
    
    def _get_down_text(self, down: int) -> str:
        """Convert down number to text."""
        down_map = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
        return down_map.get(down, f"{down}th")
    
    def _get_result_description(self, result: str, points: int) -> str:
        """Get a human-readable description of a drive result."""
        descriptions = {
            'touchdown': f'TOUCHDOWN ({points} points)',
            'field_goal': f'FIELD GOAL ({points} points)',
            'punt': 'Punt',
            'turnover': 'Turnover',
            'missed_fg': 'Missed field goal',
            'safety': f'SAFETY ({points} points)'
        }
        return descriptions.get(result, f'{result} ({points} points)')
