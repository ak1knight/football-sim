"""
Data Access Object (DAO) package for the Football Simulation application.

This package provides database access layer functionality using SQLAlchemy Core,
with specific DAOs for each entity type.
"""

from .base import BaseDAO, UserScopedDAO, DAOError
from .user_dao import UserDAO
from .team_dao import TeamDAO
from .player_dao import PlayerDAO
from .season_dao import SeasonDAO
from .season_team_dao import SeasonTeamDAO
from .season_game_dao import SeasonGameDAO
# Additional DAOs will be imported as they are created
# from .game_stats_dao import GameStatsDAO
# from .playoff_dao import PlayoffBracketDAO
# from .league_dao import UserLeagueDAO
# from .session_dao import UserSessionDAO

__all__ = [
    'BaseDAO',
    'UserScopedDAO',
    'DAOError',
    'UserDAO',
    'TeamDAO',
    'PlayerDAO',
    'SeasonDAO',
    'SeasonTeamDAO',
    'SeasonGameDAO'
    # Additional DAOs will be added as they are created
    # 'GameStatsDAO',
    # 'PlayoffBracketDAO',
    # 'UserLeagueDAO',
    # 'UserSessionDAO'
]