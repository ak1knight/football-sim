"""
API module for the football simulation engine.

This module provides REST API endpoints for the React frontend,
including team management, simulation runs, and result retrieval.
"""

from .simulation_api import SimulationAPI
from .team_api import TeamAPI

__all__ = ['SimulationAPI', 'TeamAPI']
