"""
Database migration management for the Football Simulation application.

This module provides utilities for creating, running, and managing database
schema migrations using SQLAlchemy Core.
"""

import os
import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import text
from .connection import DatabaseManager
from .schema import (
    metadata, 
    season_phase_enum, 
    game_status_enum, 
    playoff_round_enum,
    jsonb_indexes
)

logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Exception raised for migration errors."""
    pass


class MigrationManager:
    """Manages database schema migrations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.migrations_table = 'schema_migrations'
    
    def create_migrations_table(self):
        """Create the migrations tracking table if it doesn't exist."""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.migrations_table} (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            rollback_sql TEXT
        );
        """
        
        try:
            self.db_manager.execute_query(create_table_sql)
            logger.info("Migrations table created or verified")
        except Exception as e:
            logger.error(f"Failed to create migrations table: {str(e)}")
            raise MigrationError(f"Failed to create migrations table: {str(e)}")
    
    def is_migration_applied(self, migration_name: str) -> bool:
        """Check if a migration has been applied."""
        # First check if migrations table exists
        if not self._migrations_table_exists():
            return False
            
        check_sql = f"""
        SELECT COUNT(*) as count
        FROM {self.migrations_table}
        WHERE migration_name = :migration_name
        """
        
        try:
            result = self.db_manager.execute_query(check_sql, {'migration_name': migration_name})
            return result[0]['count'] > 0 if result else False
        except Exception as e:
            logger.error(f"Failed to check migration status: {str(e)}")
            return False
    
    def _migrations_table_exists(self) -> bool:
        """Check if the migrations table exists."""
        check_table_sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = :table_name
        )
        """
        
        try:
            result = self.db_manager.execute_query(check_table_sql, {'table_name': self.migrations_table})
            return result[0]['exists'] if result else False
        except Exception as e:
            logger.debug(f"Failed to check if migrations table exists: {str(e)}")
            return False
    
    def record_migration(self, migration_name: str, rollback_sql: str | None = None):
        """Record that a migration has been applied."""
        insert_sql = f"""
        INSERT INTO {self.migrations_table} (migration_name, rollback_sql)
        VALUES (:migration_name, :rollback_sql)
        """
        
        try:
            self.db_manager.execute_query(insert_sql, {
                'migration_name': migration_name,
                'rollback_sql': rollback_sql
            })
            logger.info(f"Migration '{migration_name}' recorded as applied")
        except Exception as e:
            logger.error(f"Failed to record migration: {str(e)}")
            raise MigrationError(f"Failed to record migration: {str(e)}")
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        # First check if migrations table exists
        if not self._migrations_table_exists():
            return []
            
        query_sql = f"""
        SELECT migration_name
        FROM {self.migrations_table}
        ORDER BY applied_at
        """
        
        try:
            result = self.db_manager.execute_query(query_sql)
            return [row['migration_name'] for row in result] if result else []
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {str(e)}")
            return []


def create_database_schema(db_manager: DatabaseManager, force: bool = False):
    """
    Create the complete database schema.
    
    Args:
        db_manager: DatabaseManager instance
        force: If True, drop existing tables first
    """
    migration_manager = MigrationManager(db_manager)
    migration_name = "001_initial_schema"
    
    try:
        # Create migrations table
        migration_manager.create_migrations_table()
        
        # Check if initial schema migration already applied
        if migration_manager.is_migration_applied(migration_name) and not force:
            logger.info("Initial schema already applied, skipping")
            return
        
        logger.info("Creating database schema...")
        
        with db_manager.get_db_transaction() as conn:
            # Create extensions and custom types
            logger.info("Creating extensions and custom types...")
            
            # Enable UUID extension
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            
            # Create custom ENUM types
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE season_phase AS ENUM ('regular_season', 'playoffs', 'offseason', 'complete');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE game_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE playoff_round AS ENUM ('wild_card', 'divisional', 'conference_championship', 'super_bowl');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # Drop tables if force is True
            if force:
                logger.info("Dropping existing tables...")
                # Drop in reverse dependency order
                table_names = [
                    'user_sessions', 'game_stats', 'playoff_brackets', 
                    'season_games', 'season_teams', 'seasons', 
                    'user_leagues', 'players', 'teams', 'users'
                ]
                for table_name in table_names:
                    conn.execute(text(f'DROP TABLE IF EXISTS {table_name} CASCADE'))
            
            # Create all tables using SQLAlchemy metadata
            logger.info("Creating tables...")
            metadata.create_all(bind=conn, checkfirst=True)
            
            # Create JSONB indexes
            logger.info("Creating JSONB indexes...")
            for index_name, column in jsonb_indexes:
                try:
                    conn.execute(text(f'CREATE INDEX IF NOT EXISTS {index_name} ON {column.table.name} USING GIN ({column.name})'))
                    logger.debug(f"Created JSONB index: {index_name}")
                except Exception as e:
                    logger.warning(f"Failed to create JSONB index {index_name}: {str(e)}")
            
            # Create trigger function for updating timestamps
            logger.info("Creating trigger functions...")
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """))
            
            # Create triggers for updated_at columns
            tables_with_updated_at = [
                'users', 'teams', 'players', 'seasons', 
                'season_teams', 'season_games', 'user_leagues', 'playoff_brackets'
            ]
            
            for table_name in tables_with_updated_at:
                trigger_name = f"update_{table_name}_updated_at"
                conn.execute(text(f"""
                    DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};
                    CREATE TRIGGER {trigger_name} 
                    BEFORE UPDATE ON {table_name} 
                    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                """))
                logger.debug(f"Created trigger: {trigger_name}")
        
        # Record migration
        rollback_sql = """
            DROP TABLE IF EXISTS user_sessions CASCADE;
            DROP TABLE IF EXISTS game_stats CASCADE;
            DROP TABLE IF EXISTS playoff_brackets CASCADE;
            DROP TABLE IF EXISTS season_games CASCADE;
            DROP TABLE IF EXISTS season_teams CASCADE;
            DROP TABLE IF EXISTS seasons CASCADE;
            DROP TABLE IF EXISTS user_leagues CASCADE;
            DROP TABLE IF EXISTS players CASCADE;
            DROP TABLE IF EXISTS teams CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
            DROP TYPE IF EXISTS season_phase CASCADE;
            DROP TYPE IF EXISTS game_status CASCADE;
            DROP TYPE IF EXISTS playoff_round CASCADE;
            DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
        """
        
        migration_manager.record_migration(migration_name, rollback_sql)
        logger.info("Database schema created successfully!")
        
    except Exception as e:
        logger.error(f"Failed to create database schema: {str(e)}")
        raise MigrationError(f"Failed to create database schema: {str(e)}")


def verify_database_schema(db_manager: DatabaseManager) -> Dict[str, Any]:
    """
    Verify that the database schema is properly set up.
    
    Returns:
        Dictionary with verification results
    """
    results = {
        'tables_exist': False,
        'tables': [],
        'indexes': [],
        'triggers': [],
        'types': [],
        'errors': []
    }
    
    try:
        # Check if tables exist
        table_query = """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
        """
        
        table_result = db_manager.execute_query(table_query)
        results['tables'] = [row['tablename'] for row in table_result] if table_result else []
        
        expected_tables = [
            'users', 'teams', 'players', 'user_leagues', 'seasons', 
            'season_teams', 'season_games', 'game_stats', 'playoff_brackets', 
            'user_sessions', 'schema_migrations'
        ]
        
        results['tables_exist'] = all(table in results['tables'] for table in expected_tables)
        
        # Check indexes
        index_query = """
        SELECT indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY indexname
        """
        
        index_result = db_manager.execute_query(index_query)
        results['indexes'] = [row['indexname'] for row in index_result] if index_result else []
        
        # Check custom types
        type_query = """
        SELECT typname 
        FROM pg_type 
        WHERE typname IN ('season_phase', 'game_status', 'playoff_round')
        ORDER BY typname
        """
        
        type_result = db_manager.execute_query(type_query)
        results['types'] = [row['typname'] for row in type_result] if type_result else []
        
        logger.info("Database schema verification completed")
        
    except Exception as e:
        error_msg = f"Schema verification failed: {str(e)}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
    
    return results


def drop_database_schema(db_manager: DatabaseManager):
    """
    Drop all database schema objects.
    
    WARNING: This will destroy all data!
    """
    logger.warning("Dropping database schema - this will destroy all data!")
    
    try:
        with db_manager.get_db_transaction() as conn:
            # Drop tables in reverse dependency order
            table_names = [
                'user_sessions', 'game_stats', 'playoff_brackets',
                'season_games', 'season_teams', 'seasons', 
                'user_leagues', 'players', 'teams', 'users',
                'schema_migrations'
            ]
            
            for table_name in table_names:
                conn.execute(text(f'DROP TABLE IF EXISTS {table_name} CASCADE'))
                logger.debug(f"Dropped table: {table_name}")
            
            # Drop custom types
            conn.execute(text('DROP TYPE IF EXISTS season_phase CASCADE'))
            conn.execute(text('DROP TYPE IF EXISTS game_status CASCADE'))
            conn.execute(text('DROP TYPE IF EXISTS playoff_round CASCADE'))
            
            # Drop functions
            conn.execute(text('DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE'))
            
        logger.info("Database schema dropped successfully")
        
    except Exception as e:
        logger.error(f"Failed to drop database schema: {str(e)}")
        raise MigrationError(f"Failed to drop database schema: {str(e)}")