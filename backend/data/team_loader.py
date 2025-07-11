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
    """Load all 32 NFL teams with realistic ratings."""
    teams = []
    
    # All 32 NFL teams with 2024-2025 season inspired ratings
    team_configs = [
        # AFC East
        {
            'name': 'Bills',
            'city': 'Buffalo',
            'abbreviation': 'BUF',
            'conference': 'AFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=87, passing_offense=90, rushing_offense=84,
                defensive_rating=85, pass_defense=87, run_defense=83,
                red_zone_efficiency=85, red_zone_defense=82,
                kicking_game=78, return_game=75, coaching_rating=85
            )
        },
        {
            'name': 'Dolphins',
            'city': 'Miami',
            'abbreviation': 'MIA',
            'conference': 'AFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=82, passing_offense=88, rushing_offense=76,
                defensive_rating=78, pass_defense=75, run_defense=81,
                red_zone_efficiency=79, red_zone_defense=77,
                kicking_game=82, return_game=85, coaching_rating=75
            )
        },
        {
            'name': 'Patriots',
            'city': 'New England',
            'abbreviation': 'NE',
            'conference': 'AFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=72, passing_offense=70, rushing_offense=74,
                defensive_rating=82, pass_defense=84, run_defense=80,
                red_zone_efficiency=68, red_zone_defense=85,
                kicking_game=88, return_game=72, coaching_rating=85
            )
        },
        {
            'name': 'Jets',
            'city': 'New York',
            'abbreviation': 'NYJ',
            'conference': 'AFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=75, passing_offense=72, rushing_offense=78,
                defensive_rating=85, pass_defense=88, run_defense=82,
                red_zone_efficiency=71, red_zone_defense=87,
                kicking_game=75, return_game=78, coaching_rating=72
            )
        },
        
        # AFC North
        {
            'name': 'Ravens',
            'city': 'Baltimore',
            'abbreviation': 'BAL',
            'conference': 'AFC',
            'division': 'North',
            'stats': TeamStats(
                offensive_rating=88, passing_offense=85, rushing_offense=91,
                defensive_rating=86, pass_defense=83, run_defense=89,
                red_zone_efficiency=87, red_zone_defense=84,
                kicking_game=85, return_game=82, coaching_rating=88
            )
        },
        {
            'name': 'Bengals',
            'city': 'Cincinnati',
            'abbreviation': 'CIN',
            'conference': 'AFC',
            'division': 'North',
            'stats': TeamStats(
                offensive_rating=85, passing_offense=90, rushing_offense=80,
                defensive_rating=78, pass_defense=76, run_defense=80,
                red_zone_efficiency=83, red_zone_defense=75,
                kicking_game=82, return_game=77, coaching_rating=80
            )
        },
        {
            'name': 'Browns',
            'city': 'Cleveland',
            'abbreviation': 'CLE',
            'conference': 'AFC',
            'division': 'North',
            'stats': TeamStats(
                offensive_rating=76, passing_offense=74, rushing_offense=78,
                defensive_rating=83, pass_defense=80, run_defense=86,
                red_zone_efficiency=73, red_zone_defense=85,
                kicking_game=79, return_game=75, coaching_rating=75
            )
        },
        {
            'name': 'Steelers',
            'city': 'Pittsburgh',
            'abbreviation': 'PIT',
            'conference': 'AFC',
            'division': 'North',
            'stats': TeamStats(
                offensive_rating=80, passing_offense=78, rushing_offense=82,
                defensive_rating=87, pass_defense=85, run_defense=89,
                red_zone_efficiency=78, red_zone_defense=88,
                kicking_game=83, return_game=80, coaching_rating=90
            )
        },
        
        # AFC South
        {
            'name': 'Texans',
            'city': 'Houston',
            'abbreviation': 'HOU',
            'conference': 'AFC',
            'division': 'South',
            'stats': TeamStats(
                offensive_rating=83, passing_offense=85, rushing_offense=81,
                defensive_rating=80, pass_defense=78, run_defense=82,
                red_zone_efficiency=81, red_zone_defense=79,
                kicking_game=77, return_game=83, coaching_rating=82
            )
        },
        {
            'name': 'Colts',
            'city': 'Indianapolis',
            'abbreviation': 'IND',
            'conference': 'AFC',
            'division': 'South',
            'stats': TeamStats(
                offensive_rating=78, passing_offense=76, rushing_offense=80,
                defensive_rating=75, pass_defense=73, run_defense=77,
                red_zone_efficiency=76, red_zone_defense=74,
                kicking_game=85, return_game=72, coaching_rating=78
            )
        },
        {
            'name': 'Jaguars',
            'city': 'Jacksonville',
            'abbreviation': 'JAX',
            'conference': 'AFC',
            'division': 'South',
            'stats': TeamStats(
                offensive_rating=74, passing_offense=72, rushing_offense=76,
                defensive_rating=76, pass_defense=74, run_defense=78,
                red_zone_efficiency=71, red_zone_defense=75,
                kicking_game=73, return_game=76, coaching_rating=70
            )
        },
        {
            'name': 'Titans',
            'city': 'Tennessee',
            'abbreviation': 'TEN',
            'conference': 'AFC',
            'division': 'South',
            'stats': TeamStats(
                offensive_rating=72, passing_offense=69, rushing_offense=75,
                defensive_rating=74, pass_defense=72, run_defense=76,
                red_zone_efficiency=68, red_zone_defense=73,
                kicking_game=76, return_game=71, coaching_rating=73
            )
        },
        
        # AFC West
        {
            'name': 'Chiefs',
            'city': 'Kansas City',
            'abbreviation': 'KC',
            'conference': 'AFC',
            'division': 'West',
            'stats': TeamStats(
                offensive_rating=90, passing_offense=95, rushing_offense=85,
                defensive_rating=82, pass_defense=80, run_defense=84,
                red_zone_efficiency=92, red_zone_defense=83,
                kicking_game=90, return_game=85, coaching_rating=95
            )
        },
        {
            'name': 'Chargers',
            'city': 'Los Angeles',
            'abbreviation': 'LAC',
            'conference': 'AFC',
            'division': 'West',
            'stats': TeamStats(
                offensive_rating=84, passing_offense=88, rushing_offense=80,
                defensive_rating=83, pass_defense=85, run_defense=81,
                red_zone_efficiency=82, red_zone_defense=84,
                kicking_game=82, return_game=79, coaching_rating=82
            )
        },
        {
            'name': 'Broncos',
            'city': 'Denver',
            'abbreviation': 'DEN',
            'conference': 'AFC',
            'division': 'West',
            'stats': TeamStats(
                offensive_rating=79, passing_offense=77, rushing_offense=81,
                defensive_rating=84, pass_defense=86, run_defense=82,
                red_zone_efficiency=76, red_zone_defense=86,
                kicking_game=78, return_game=74, coaching_rating=81
            )
        },
        {
            'name': 'Raiders',
            'city': 'Las Vegas',
            'abbreviation': 'LV',
            'conference': 'AFC',
            'division': 'West',
            'stats': TeamStats(
                offensive_rating=76, passing_offense=78, rushing_offense=74,
                defensive_rating=73, pass_defense=71, run_defense=75,
                red_zone_efficiency=74, red_zone_defense=72,
                kicking_game=74, return_game=78, coaching_rating=70
            )
        },
        
        # NFC East
        {
            'name': 'Eagles',
            'city': 'Philadelphia',
            'abbreviation': 'PHI',
            'conference': 'NFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=86, passing_offense=83, rushing_offense=89,
                defensive_rating=81, pass_defense=78, run_defense=84,
                red_zone_efficiency=85, red_zone_defense=80,
                kicking_game=84, return_game=81, coaching_rating=87
            )
        },
        {
            'name': 'Cowboys',
            'city': 'Dallas',
            'abbreviation': 'DAL',
            'conference': 'NFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=83, passing_offense=87, rushing_offense=79,
                defensive_rating=78, pass_defense=80, run_defense=76,
                red_zone_efficiency=81, red_zone_defense=77,
                kicking_game=86, return_game=83, coaching_rating=75
            )
        },
        {
            'name': 'Commanders',
            'city': 'Washington',
            'abbreviation': 'WAS',
            'conference': 'NFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=81, passing_offense=84, rushing_offense=78,
                defensive_rating=76, pass_defense=74, run_defense=78,
                red_zone_efficiency=79, red_zone_defense=75,
                kicking_game=79, return_game=76, coaching_rating=79
            )
        },
        {
            'name': 'Giants',
            'city': 'New York',
            'abbreviation': 'NYG',
            'conference': 'NFC',
            'division': 'East',
            'stats': TeamStats(
                offensive_rating=73, passing_offense=71, rushing_offense=75,
                defensive_rating=77, pass_defense=75, run_defense=79,
                red_zone_efficiency=70, red_zone_defense=76,
                kicking_game=81, return_game=73, coaching_rating=72
            )
        },
        
        # NFC North
        {
            'name': 'Lions',
            'city': 'Detroit',
            'abbreviation': 'DET',
            'conference': 'NFC',
            'division': 'North',
            'stats': TeamStats(
                offensive_rating=89, passing_offense=87, rushing_offense=91,
                defensive_rating=77, pass_defense=75, run_defense=79,
                red_zone_efficiency=90, red_zone_defense=76,
                kicking_game=83, return_game=80, coaching_rating=88
            )
        },
        {
            'name': 'Packers',
            'city': 'Green Bay',
            'abbreviation': 'GB',
            'conference': 'NFC',
            'division': 'North',
            'stats': TeamStats(
                offensive_rating=85, passing_offense=91, rushing_offense=79,
                defensive_rating=79, pass_defense=81, run_defense=77,
                red_zone_efficiency=86, red_zone_defense=78,
                kicking_game=87, return_game=75, coaching_rating=85
            )
        },
        {
            'name': 'Vikings',
            'city': 'Minnesota',
            'abbreviation': 'MIN',
            'conference': 'NFC',
            'division': 'North',
            'stats': TeamStats(
                offensive_rating=82, passing_offense=85, rushing_offense=79,
                defensive_rating=81, pass_defense=83, run_defense=79,
                red_zone_efficiency=80, red_zone_defense=82,
                kicking_game=75, return_game=78, coaching_rating=83
            )
        },
        {
            'name': 'Bears',
            'city': 'Chicago',
            'abbreviation': 'CHI',
            'conference': 'NFC',
            'division': 'North',
            'stats': TeamStats(
                offensive_rating=76, passing_offense=74, rushing_offense=78,
                defensive_rating=83, pass_defense=81, run_defense=85,
                red_zone_efficiency=73, red_zone_defense=84,
                kicking_game=77, return_game=74, coaching_rating=78
            )
        },
        
        # NFC South
        {
            'name': 'Saints',
            'city': 'New Orleans',
            'abbreviation': 'NO',
            'conference': 'NFC',
            'division': 'South',
            'stats': TeamStats(
                offensive_rating=79, passing_offense=82, rushing_offense=76,
                defensive_rating=80, pass_defense=78, run_defense=82,
                red_zone_efficiency=78, red_zone_defense=81,
                kicking_game=85, return_game=77, coaching_rating=82
            )
        },
        {
            'name': 'Falcons',
            'city': 'Atlanta',
            'abbreviation': 'ATL',
            'conference': 'NFC',
            'division': 'South',
            'stats': TeamStats(
                offensive_rating=81, passing_offense=84, rushing_offense=78,
                defensive_rating=75, pass_defense=73, run_defense=77,
                red_zone_efficiency=80, red_zone_defense=74,
                kicking_game=79, return_game=82, coaching_rating=77
            )
        },
        {
            'name': 'Buccaneers',
            'city': 'Tampa Bay',
            'abbreviation': 'TB',
            'conference': 'NFC',
            'division': 'South',
            'stats': TeamStats(
                offensive_rating=84, passing_offense=88, rushing_offense=80,
                defensive_rating=78, pass_defense=76, run_defense=80,
                red_zone_efficiency=83, red_zone_defense=77,
                kicking_game=82, return_game=78, coaching_rating=83
            )
        },
        {
            'name': 'Panthers',
            'city': 'Carolina',
            'abbreviation': 'CAR',
            'conference': 'NFC',
            'division': 'South',
            'stats': TeamStats(
                offensive_rating=71, passing_offense=68, rushing_offense=74,
                defensive_rating=74, pass_defense=72, run_defense=76,
                red_zone_efficiency=68, red_zone_defense=73,
                kicking_game=76, return_game=71, coaching_rating=71
            )
        },
        
        # NFC West
        {
            'name': '49ers',
            'city': 'San Francisco',
            'abbreviation': 'SF',
            'conference': 'NFC',
            'division': 'West',
            'stats': TeamStats(
                offensive_rating=87, passing_offense=85, rushing_offense=89,
                defensive_rating=88, pass_defense=86, run_defense=90,
                red_zone_efficiency=86, red_zone_defense=89,
                kicking_game=84, return_game=82, coaching_rating=92
            )
        },
        {
            'name': 'Seahawks',
            'city': 'Seattle',
            'abbreviation': 'SEA',
            'conference': 'NFC',
            'division': 'West',
            'stats': TeamStats(
                offensive_rating=82, passing_offense=86, rushing_offense=78,
                defensive_rating=80, pass_defense=82, run_defense=78,
                red_zone_efficiency=81, red_zone_defense=79,
                kicking_game=78, return_game=85, coaching_rating=85
            )
        },
        {
            'name': 'Rams',
            'city': 'Los Angeles',
            'abbreviation': 'LAR',
            'conference': 'NFC',
            'division': 'West',
            'stats': TeamStats(
                offensive_rating=80, passing_offense=84, rushing_offense=76,
                defensive_rating=82, pass_defense=84, run_defense=80,
                red_zone_efficiency=79, red_zone_defense=83,
                kicking_game=81, return_game=76, coaching_rating=86
            )
        },
        {
            'name': 'Cardinals',
            'city': 'Arizona',
            'abbreviation': 'ARI',
            'conference': 'NFC',
            'division': 'West',
            'stats': TeamStats(
                offensive_rating=77, passing_offense=79, rushing_offense=75,
                defensive_rating=73, pass_defense=71, run_defense=75,
                red_zone_efficiency=75, red_zone_defense=72,
                kicking_game=77, return_game=79, coaching_rating=74
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
