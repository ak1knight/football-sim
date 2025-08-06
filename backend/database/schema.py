"""
Database schema definitions using SQLAlchemy Core.

This module defines all database tables using SQLAlchemy Table objects
for the Football Simulation application.
"""

from sqlalchemy import (
    Table, Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy import MetaData, func

# Create metadata object
metadata = MetaData()

# Custom PostgreSQL ENUMs
season_phase_enum = ENUM(
    'regular_season', 'playoffs', 'offseason', 'complete',
    name='season_phase',
    create_type=False
)

game_status_enum = ENUM(
    'scheduled', 'in_progress', 'completed', 'cancelled',
    name='game_status',
    create_type=False
)

playoff_round_enum = ENUM(
    'wild_card', 'divisional', 'conference_championship', 'super_bowl',
    name='playoff_round',
    create_type=False
)

# Users table
users_table = Table(
    'users',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('username', String(50), nullable=False, unique=True),
    Column('email', String(255), nullable=False, unique=True),
    Column('password_hash', String(255), nullable=False),
    Column('first_name', String(100)),
    Column('last_name', String(100)),
    Column('is_active', Boolean, default=True),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp()),
)

# Teams table
teams_table = Table(
    'teams',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('name', String(100), nullable=False),
    Column('city', String(100), nullable=False),
    Column('abbreviation', String(10), nullable=False, unique=True),
    Column('conference', String(10), nullable=False),
    Column('division', String(20), nullable=False),
    Column('team_stats', JSONB, nullable=False, server_default='{}'),
    Column('logo_url', String(255)),
    Column('primary_color', String(7)),
    Column('secondary_color', String(7)),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp()),
    CheckConstraint("conference IN ('AFC', 'NFC')", name='check_conference'),
    CheckConstraint("division IN ('East', 'West', 'North', 'South')", name='check_division')
)

# Players table
players_table = Table(
    'players',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('team_id', UUID(as_uuid=True), ForeignKey('teams.id', ondelete='SET NULL')),
    Column('name', String(100), nullable=False),
    Column('position', String(20), nullable=False),
    Column('jersey_number', Integer),
    Column('age', Integer),
    Column('years_pro', Integer, default=0),
    Column('player_stats', JSONB, nullable=False, server_default='{}'),
    Column('injury_status', Boolean, default=False),
    Column('contract_details', JSONB, server_default='{}'),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp()),
    CheckConstraint('jersey_number BETWEEN 1 AND 99', name='check_jersey_number'),
    CheckConstraint('age BETWEEN 18 AND 45', name='check_age'),
    UniqueConstraint('team_id', 'jersey_number', name='unique_team_jersey')
)

# User leagues table
user_leagues_table = Table(
    'user_leagues',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('name', String(200), nullable=False),
    Column('description', Text),
    Column('settings', JSONB, nullable=False, server_default='{}'),
    Column('is_active', Boolean, default=True),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp()),
)

# Seasons table
seasons_table = Table(
    'seasons',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('league_id', UUID(as_uuid=True), ForeignKey('user_leagues.id', ondelete='SET NULL')),
    Column('season_year', Integer, nullable=False),
    Column('name', String(200), nullable=False),
    Column('current_week', Integer, default=1),
    Column('phase', season_phase_enum, default='regular_season'),
    Column('settings', JSONB, nullable=False, server_default='{}'),
    Column('started_at', DateTime(timezone=True)),
    Column('completed_at', DateTime(timezone=True)),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp()),
)

# Season teams table
season_teams_table = Table(
    'season_teams',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('season_id', UUID(as_uuid=True), ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False),
    Column('team_id', UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
    Column('wins', Integer, default=0),
    Column('losses', Integer, default=0),
    Column('ties', Integer, default=0),
    Column('points_for', Integer, default=0),
    Column('points_against', Integer, default=0),
    Column('division_wins', Integer, default=0),
    Column('conference_wins', Integer, default=0),
    Column('season_stats', JSONB, server_default='{}'),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp()),
    UniqueConstraint('season_id', 'team_id', name='unique_season_team')
)

# Season games table
season_games_table = Table(
    'season_games',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('season_id', UUID(as_uuid=True), ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False),
    Column('game_id', String(100), nullable=False),
    Column('week', Integer),
    Column('playoff_round', playoff_round_enum),
    Column('home_team_id', UUID(as_uuid=True), ForeignKey('teams.id'), nullable=False),
    Column('away_team_id', UUID(as_uuid=True), ForeignKey('teams.id'), nullable=False),
    Column('home_score', Integer, default=0),
    Column('away_score', Integer, default=0),
    Column('status', game_status_enum, default='scheduled'),
    Column('game_date', DateTime(timezone=True)),
    Column('weather_conditions', JSONB, server_default='{}'),
    Column('game_data', JSONB, server_default='{}'),
    Column('play_by_play', JSONB, server_default='[]'),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp()),
    UniqueConstraint('season_id', 'game_id', name='unique_season_game_id')
)

# Game stats table
game_stats_table = Table(
    'game_stats',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('game_id', UUID(as_uuid=True), ForeignKey('season_games.id', ondelete='CASCADE'), nullable=False),
    Column('team_id', UUID(as_uuid=True), ForeignKey('teams.id'), nullable=False),
    Column('player_id', UUID(as_uuid=True), ForeignKey('players.id', ondelete='SET NULL')),
    Column('stat_type', String(50), nullable=False),
    Column('stat_data', JSONB, nullable=False, server_default='{}'),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
)

# Playoff brackets table
playoff_brackets_table = Table(
    'playoff_brackets',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('season_id', UUID(as_uuid=True), ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False),
    Column('bracket_data', JSONB, nullable=False, server_default='{}'),
    Column('current_round', playoff_round_enum, default='wild_card'),
    Column('afc_champion_id', UUID(as_uuid=True), ForeignKey('teams.id')),
    Column('nfc_champion_id', UUID(as_uuid=True), ForeignKey('teams.id')),
    Column('super_bowl_champion_id', UUID(as_uuid=True), ForeignKey('teams.id')),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp()),
    UniqueConstraint('season_id', name='unique_season_bracket')
)

# User sessions table
user_sessions_table = Table(
    'user_sessions',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('token_hash', String(255), nullable=False),
    Column('expires_at', DateTime(timezone=True), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
    Column('last_used_at', DateTime(timezone=True), server_default=func.current_timestamp()),
)

# Create indexes for performance
Index('idx_users_username', users_table.c.username)
Index('idx_users_email', users_table.c.email)
Index('idx_users_active', users_table.c.is_active, postgresql_where=users_table.c.is_active.is_(True))

Index('idx_teams_abbreviation', teams_table.c.abbreviation)
Index('idx_teams_conference_division', teams_table.c.conference, teams_table.c.division)

Index('idx_players_team_id', players_table.c.team_id)
Index('idx_players_position', players_table.c.position)

Index('idx_seasons_user_id', seasons_table.c.user_id)
Index('idx_seasons_year', seasons_table.c.season_year)
Index('idx_seasons_phase', seasons_table.c.phase)

Index('idx_season_teams_season_id', season_teams_table.c.season_id)
Index('idx_season_teams_team_id', season_teams_table.c.team_id)

Index('idx_season_games_season_id', season_games_table.c.season_id)
Index('idx_season_games_week', season_games_table.c.week)
Index('idx_season_games_status', season_games_table.c.status)
Index('idx_season_games_teams', season_games_table.c.home_team_id, season_games_table.c.away_team_id)
Index('idx_season_games_date', season_games_table.c.game_date)

Index('idx_game_stats_game_id', game_stats_table.c.game_id)
Index('idx_game_stats_team_id', game_stats_table.c.team_id)
Index('idx_game_stats_player_id', game_stats_table.c.player_id)

Index('idx_playoff_brackets_season_id', playoff_brackets_table.c.season_id)

Index('idx_user_sessions_user_id', user_sessions_table.c.user_id)
Index('idx_user_sessions_token', user_sessions_table.c.token_hash)
Index('idx_user_sessions_expires', user_sessions_table.c.expires_at)

# GIN indexes for JSONB columns (will be created separately in migration)
jsonb_indexes = [
    ('idx_teams_stats_gin', teams_table.c.team_stats),
    ('idx_players_stats_gin', players_table.c.player_stats),
    ('idx_season_games_data_gin', season_games_table.c.game_data),
    ('idx_game_stats_data_gin', game_stats_table.c.stat_data),
]

# Export all tables for use in other modules
__all__ = [
    'metadata',
    'users_table',
    'teams_table', 
    'players_table',
    'user_leagues_table',
    'seasons_table',
    'season_teams_table',
    'season_games_table',
    'game_stats_table',
    'playoff_brackets_table',
    'user_sessions_table',
    'season_phase_enum',
    'game_status_enum',
    'playoff_round_enum',
    'jsonb_indexes'
]