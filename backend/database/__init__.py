"""
Database package for the Football Simulation application.

This package provides database connection management, schema definitions,
data access layers, and utilities for working with PostgreSQL using SQLAlchemy Core.
"""

from .connection import DatabaseManager, get_db_manager
from .schema import (
    users_table, 
    teams_table, 
    players_table,
    seasons_table,
    season_teams_table,
    season_games_table,
    game_stats_table,
    playoff_brackets_table,
    user_sessions_table,
    user_leagues_table
)

__all__ = [
    'DatabaseManager',
    'get_db_manager',
    'users_table',
    'teams_table', 
    'players_table',
    'seasons_table',
    'season_teams_table',
    'season_games_table',
    'game_stats_table',
    'playoff_brackets_table',
    'user_sessions_table',
    'user_leagues_table'
]