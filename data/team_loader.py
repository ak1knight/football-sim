"""
Team data loader for the football simulation.

This module provides functions to load team and player data,
including sample teams for testing and demonstration.
"""

from typing import List
from models.team import Team, TeamStats
from models.player import Player, Position, PlayerStats

def create_sample_player(name: str, position: Position, jersey_number: int, 
                        overall_rating: int = 75) -> Player:
    """Create a sample player with basic stats."""
    stats = PlayerStats(overall_rating=overall_rating)
    
    # Set position-specific stats based on position
    if position == Position.QB:
        stats.passing_accuracy = overall_rating
        stats.passing_power = overall_rating - 5
        stats.awareness = overall_rating + 5
    elif position in [Position.RB]:
        stats.rushing_ability = overall_rating
        stats.speed = overall_rating + 5
        stats.strength = overall_rating
    elif position in [Position.WR, Position.TE]:
        stats.receiving_ability = overall_rating
        stats.speed = overall_rating + 3
        stats.awareness = overall_rating
    elif position == Position.OL:
        stats.blocking = overall_rating
        stats.strength = overall_rating + 5
        stats.awareness = overall_rating
    elif position in [Position.DL, Position.LB]:
        stats.tackling = overall_rating
        stats.strength = overall_rating + 3
        stats.pass_rush = overall_rating - 5
    elif position in [Position.CB, Position.S]:
        stats.coverage = overall_rating
        stats.speed = overall_rating + 5
        stats.tackling = overall_rating - 10
    elif position == Position.K:
        stats.kicking_accuracy = overall_rating
        stats.kicking_power = overall_rating - 5
    elif position == Position.P:
        stats.kicking_power = overall_rating
        stats.kicking_accuracy = overall_rating - 10
    
    return Player(name=name, position=position, jersey_number=jersey_number, stats=stats)

def create_sample_team_roster(team_name: str) -> List[Player]:
    """Create a sample roster for a team."""
    players = []
    
    # Create a basic roster with key positions
    roster_template = [
        # Offense
        (f"{team_name} QB1", Position.QB, 1, 82),
        (f"{team_name} QB2", Position.QB, 12, 68),
        (f"{team_name} RB1", Position.RB, 21, 80),
        (f"{team_name} RB2", Position.RB, 28, 72),
        (f"{team_name} WR1", Position.WR, 11, 85),
        (f"{team_name} WR2", Position.WR, 19, 78),
        (f"{team_name} WR3", Position.WR, 83, 74),
        (f"{team_name} TE1", Position.TE, 87, 76),
        (f"{team_name} TE2", Position.TE, 88, 70),
        
        # Offensive Line
        (f"{team_name} C", Position.OL, 55, 77),
        (f"{team_name} LG", Position.OL, 66, 75),
        (f"{team_name} RG", Position.OL, 67, 75),
        (f"{team_name} LT", Position.OL, 77, 79),
        (f"{team_name} RT", Position.OL, 78, 79),
        
        # Defense
        (f"{team_name} DE1", Position.DL, 91, 81),
        (f"{team_name} DE2", Position.DL, 94, 76),
        (f"{team_name} DT1", Position.DL, 98, 79),
        (f"{team_name} DT2", Position.DL, 99, 74),
        (f"{team_name} LB1", Position.LB, 54, 80),
        (f"{team_name} LB2", Position.LB, 56, 77),
        (f"{team_name} LB3", Position.LB, 58, 74),
        (f"{team_name} CB1", Position.CB, 24, 82),
        (f"{team_name} CB2", Position.CB, 25, 78),
        (f"{team_name} CB3", Position.CB, 26, 72),
        (f"{team_name} FS", Position.S, 32, 79),
        (f"{team_name} SS", Position.S, 33, 77),
        
        # Special Teams
        (f"{team_name} K", Position.K, 4, 75),
        (f"{team_name} P", Position.P, 5, 73),
    ]
    
    for name, position, jersey, rating in roster_template:
        players.append(create_sample_player(name, position, jersey, rating))
    
    return players

def load_sample_teams() -> List[Team]:
    """Load sample teams for testing and demonstration."""
    teams = []
    
    # Create sample teams with different strengths
    team_configs = [
        {
            'name': 'Eagles',
            'city': 'Philadelphia',
            'abbreviation': 'PHI',
            'conference': 'NFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=85,
                passing_offense=82,
                rushing_offense=88,
                defensive_rating=78,
                pass_defense=75,
                run_defense=81,
                coaching_rating=83
            )
        },
        {
            'name': 'Cowboys',
            'city': 'Dallas',
            'abbreviation': 'DAL',
            'conference': 'NFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=80,
                passing_offense=85,
                rushing_offense=75,
                defensive_rating=82,
                pass_defense=84,
                run_defense=80,
                coaching_rating=78
            )
        },
        {
            'name': 'Chiefs',
            'city': 'Kansas City',
            'abbreviation': 'KC',
            'conference': 'AFC',
            'division': 'West',
            'stats': TeamStats(
                offensive_rating=90,
                passing_offense=95,
                rushing_offense=85,
                defensive_rating=75,
                pass_defense=73,
                run_defense=77,
                coaching_rating=88
            )
        },
        {
            'name': 'Bills',
            'city': 'Buffalo',
            'abbreviation': 'BUF',
            'conference': 'AFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=87,
                passing_offense=90,
                rushing_offense=84,
                defensive_rating=85,
                pass_defense=87,
                run_defense=83,
                coaching_rating=85
            )
        }
    ]
    
    for config in team_configs:
        team = Team(
            name=config['name'],
            city=config['city'],
            abbreviation=config['abbreviation'],
            conference=config['conference'],
            division=config['division'],
            stats=config['stats']
        )
        
        # Add players to the team
        roster = create_sample_team_roster(config['name'])
        for player in roster:
            team.add_player(player)
        
        teams.append(team)
    
    return teams

def save_team_data(teams: List[Team], filename: str = "teams.json") -> None:
    """Save team data to a JSON file (placeholder for future implementation)."""
    # This would implement JSON serialization of team data
    # For now, it's a placeholder
    pass

def load_team_data(filename: str = "teams.json") -> List[Team]:
    """Load team data from a JSON file (placeholder for future implementation)."""
    # This would implement JSON deserialization of team data
    # For now, return sample teams
    return load_sample_teams()
