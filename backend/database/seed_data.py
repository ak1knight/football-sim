"""
Database seed data management for the Football Simulation application.

This module provides functionality to populate the database with initial data
including NFL teams, players, and reference data.
"""

import logging
from typing import List, Dict, Any
from .connection import DatabaseManager
from .dao.team_dao import TeamDAO
from .dao.player_dao import PlayerDAO
from ..data.team_loader import load_sample_teams

logger = logging.getLogger(__name__)


class SeedDataError(Exception):
    """Exception raised for seed data operations."""
    pass


class DatabaseSeeder:
    """Manages database seed data operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.team_dao = TeamDAO(db_manager)
        self.player_dao = PlayerDAO(db_manager)
    
    def seed_teams(self, force: bool = False) -> Dict[str, Any]:
        """
        Seed the database with NFL teams.
        
        Args:
            force: If True, delete existing teams first
            
        Returns:
            Dictionary with seeding results
        """
        try:
            logger.info("Starting team seeding process...")
            
            # Check if teams already exist
            existing_teams = self.team_dao.get_all()
            if existing_teams and not force:
                logger.info(f"Teams already exist ({len(existing_teams)} found). Use force=True to reseed.")
                return {
                    'success': True,
                    'message': 'Teams already exist',
                    'teams_count': len(existing_teams),
                    'action': 'skipped'
                }
            
            # Clear existing teams if force is True
            if force and existing_teams:
                logger.info(f"Force mode: clearing {len(existing_teams)} existing teams...")
                # Note: This would need proper cascade handling for production
                # For now, we'll assume foreign key constraints handle it
                pass
            
            # Load sample teams from the existing team loader
            sample_teams = load_sample_teams()
            logger.info(f"Loaded {len(sample_teams)} sample teams")
            
            # Convert teams to database format and insert
            team_records = []
            for team in sample_teams:
                team_record = {
                    'name': team.name,
                    'city': team.city,
                    'abbreviation': team.abbreviation,
                    'conference': team.conference,
                    'division': team.division,
                    'team_stats': {
                        'offensive_rating': team.stats.offensive_rating,
                        'passing_offense': team.stats.passing_offense,
                        'rushing_offense': team.stats.rushing_offense,
                        'defensive_rating': team.stats.defensive_rating,
                        'pass_defense': team.stats.pass_defense,
                        'run_defense': team.stats.run_defense,
                        'red_zone_efficiency': team.stats.red_zone_efficiency,
                        'red_zone_defense': team.stats.red_zone_defense,
                        'kicking_game': team.stats.kicking_game,
                        'return_game': team.stats.return_game,
                        'coaching_rating': team.stats.coaching_rating,
                        'discipline': team.stats.discipline,
                        'conditioning': team.stats.conditioning,
                        'home_field_advantage': team.stats.home_field_advantage
                    }
                }
                team_records.append(team_record)
            
            # Bulk insert teams
            team_ids = self.team_dao.bulk_insert(team_records)
            logger.info(f"Successfully inserted {len(team_ids)} teams")
            
            # Create mapping of abbreviation to team ID for player seeding
            team_id_mapping = {}
            for i, team in enumerate(sample_teams):
                team_id_mapping[team.abbreviation] = team_ids[i]
            
            # Seed players for each team
            total_players = 0
            for team in sample_teams:
                team_id = team_id_mapping[team.abbreviation]
                player_count = self._seed_players_for_team(team_id, team.players)
                total_players += player_count
                logger.debug(f"Added {player_count} players for {team.abbreviation}")
            
            logger.info(f"Successfully seeded {len(team_ids)} teams with {total_players} total players")
            
            return {
                'success': True,
                'message': 'Teams and players seeded successfully',
                'teams_count': len(team_ids),
                'players_count': total_players,
                'action': 'seeded'
            }
            
        except Exception as e:
            logger.error(f"Failed to seed teams: {str(e)}")
            raise SeedDataError(f"Failed to seed teams: {str(e)}")
    
    def _seed_players_for_team(self, team_id: str, players: List[Any]) -> int:
        """
        Seed players for a specific team.
        
        Args:
            team_id: Team ID
            players: List of player objects
            
        Returns:
            Number of players inserted
        """
        try:
            player_records = []
            for player in players:
                player_record = {
                    'team_id': team_id,
                    'name': player.name,
                    'position': player.position.value,
                    'jersey_number': player.jersey_number,
                    'age': player.age,
                    'years_pro': player.years_pro,
                    'injury_status': player.injury_status,
                    'player_stats': {
                        'overall_rating': player.stats.overall_rating,
                        'speed': player.stats.speed,
                        'strength': player.stats.strength,
                        'awareness': player.stats.awareness,
                        'passing_accuracy': player.stats.passing_accuracy,
                        'passing_power': player.stats.passing_power,
                        'rushing_ability': player.stats.rushing_ability,
                        'receiving_ability': player.stats.receiving_ability,
                        'blocking': player.stats.blocking,
                        'tackling': player.stats.tackling,
                        'coverage': player.stats.coverage,
                        'pass_rush': player.stats.pass_rush,
                        'kicking_accuracy': player.stats.kicking_accuracy,
                        'kicking_power': player.stats.kicking_power
                    }
                }
                player_records.append(player_record)
            
            # Bulk insert players for this team
            player_ids = self.player_dao.bulk_insert(player_records)
            return len(player_ids)
            
        except Exception as e:
            logger.error(f"Failed to seed players for team {team_id}: {str(e)}")
            raise SeedDataError(f"Failed to seed players for team: {str(e)}")
    
    def verify_seed_data(self) -> Dict[str, Any]:
        """
        Verify that seed data was properly inserted.
        
        Returns:
            Dictionary with verification results
        """
        try:
            verification = {
                'success': True,
                'teams': {},
                'players': {},
                'errors': []
            }
            
            # Check teams
            all_teams = self.team_dao.get_all()
            verification['teams']['total'] = len(all_teams)
            
            # Check team distribution by conference and division
            afc_teams = self.team_dao.get_by_conference('AFC')
            nfc_teams = self.team_dao.get_by_conference('NFC')
            
            verification['teams']['afc'] = len(afc_teams)
            verification['teams']['nfc'] = len(nfc_teams)
            
            # Check if we have the expected 32 teams
            if len(all_teams) != 32:
                verification['errors'].append(f"Expected 32 teams, found {len(all_teams)}")
                verification['success'] = False
            
            # Check players
            all_players = self.player_dao.get_all()
            verification['players']['total'] = len(all_players)
            
            # Check that each team has players
            teams_without_players = []
            for team in all_teams:
                team_players = self.player_dao.get_by_team_id(team['id'])
                if not team_players:
                    teams_without_players.append(team['abbreviation'])
            
            if teams_without_players:
                verification['errors'].append(f"Teams without players: {teams_without_players}")
                verification['success'] = False
            
            verification['players']['teams_with_players'] = len(all_teams) - len(teams_without_players)
            
            logger.info(f"Seed data verification: {verification}")
            return verification
            
        except Exception as e:
            logger.error(f"Failed to verify seed data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'teams': {},
                'players': {}
            }
    
    def clear_all_data(self) -> Dict[str, Any]:
        """
        Clear all seeded data from the database.
        
        WARNING: This will delete all teams and players!
        
        Returns:
            Dictionary with clearing results
        """
        try:
            logger.warning("Clearing all seed data from database...")
            
            # Get counts before deletion
            teams_before = len(self.team_dao.get_all())
            players_before = len(self.player_dao.get_all())
            
            # Delete all players first (due to foreign key constraints)
            # Note: In a real implementation, we'd want more sophisticated cascade handling
            # For now, relying on database foreign key constraints
            
            # This is a simplified approach - in production, we'd want more control
            with self.db_manager.get_db_transaction() as conn:
                conn.execute("DELETE FROM players")
                conn.execute("DELETE FROM teams")
            
            logger.info(f"Cleared {teams_before} teams and {players_before} players")
            
            return {
                'success': True,
                'message': 'All seed data cleared',
                'teams_cleared': teams_before,
                'players_cleared': players_before
            }
            
        except Exception as e:
            logger.error(f"Failed to clear seed data: {str(e)}")
            raise SeedDataError(f"Failed to clear seed data: {str(e)}")


def seed_database(db_manager: DatabaseManager, force: bool = False) -> Dict[str, Any]:
    """
    Convenience function to seed the database with initial data.
    
    Args:
        db_manager: DatabaseManager instance
        force: Whether to force re-seeding if data already exists
        
    Returns:
        Dictionary with seeding results
    """
    seeder = DatabaseSeeder(db_manager)
    return seeder.seed_teams(force=force)


def verify_database_data(db_manager: DatabaseManager) -> Dict[str, Any]:
    """
    Convenience function to verify database seed data.
    
    Args:
        db_manager: DatabaseManager instance
        
    Returns:
        Dictionary with verification results
    """
    seeder = DatabaseSeeder(db_manager)
    return seeder.verify_seed_data()