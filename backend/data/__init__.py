"""
Data module for the football simulation engine.

This module handles loading and managing team and player data.
"""

from .team_loader import load_sample_teams, create_sample_player, load_team_data, save_team_data

__all__ = ['load_sample_teams', 'create_sample_player', 'load_team_data', 'save_team_data']
