#!/usr/bin/env python3
"""
Database management utility for the Football Simulation application.

This script provides command-line tools for managing the database schema,
running migrations, and performing maintenance tasks.
"""

import os
import sys
import argparse
import logging
from typing import Any

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import initialize_database_manager, close_database_manager
from database.migrations import (
    create_database_schema, 
    verify_database_schema, 
    drop_database_schema,
    MigrationManager
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database(args: Any):
    """Initialize the database with schema and seed data."""
    try:
        logger.info("Initializing database...")
        
        # Initialize database manager
        db_manager = initialize_database_manager()
        
        # Test connection
        if not db_manager.test_connection():
            logger.error("Database connection failed")
            return False
        
        # Create schema
        create_database_schema(db_manager, force=args.force)
        
        # Verify schema
        verification = verify_database_schema(db_manager)
        if verification['tables_exist']:
            logger.info("Database schema verified successfully")
            logger.info(f"Tables created: {len(verification['tables'])}")
            logger.info(f"Indexes created: {len(verification['indexes'])}")
        else:
            logger.error("Database schema verification failed")
            return False
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False
    finally:
        close_database_manager()


def verify_database(args: Any):
    """Verify the database schema."""
    try:
        logger.info("Verifying database schema...")
        
        db_manager = initialize_database_manager()
        
        if not db_manager.test_connection():
            logger.error("Database connection failed")
            return False
        
        verification = verify_database_schema(db_manager)
        
        print("\n=== Database Verification Report ===")
        print(f"Tables exist: {verification['tables_exist']}")
        print(f"Tables found: {len(verification['tables'])}")
        print(f"Indexes found: {len(verification['indexes'])}")
        print(f"Custom types found: {len(verification['types'])}")
        
        if verification['tables']:
            print(f"\nTables: {', '.join(verification['tables'])}")
        
        if verification['types']:
            print(f"Custom types: {', '.join(verification['types'])}")
        
        if verification['errors']:
            print(f"\nErrors: {verification['errors']}")
            return False
        
        print("\nDatabase verification completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database verification failed: {str(e)}")
        return False
    finally:
        close_database_manager()


def drop_database(args: Any):
    """Drop all database schema objects."""
    if not args.confirm:
        print("WARNING: This will destroy all data in the database!")
        print("Use --confirm flag to proceed.")
        return False
    
    try:
        logger.info("Dropping database schema...")
        
        db_manager = initialize_database_manager()
        
        if not db_manager.test_connection():
            logger.error("Database connection failed")
            return False
        
        drop_database_schema(db_manager)
        
        logger.info("Database schema dropped successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to drop database schema: {str(e)}")
        return False
    finally:
        close_database_manager()


def show_status(args: Any):
    """Show database status and information."""
    try:
        logger.info("Checking database status...")
        
        db_manager = initialize_database_manager()
        
        if not db_manager.test_connection():
            print("❌ Database connection: FAILED")
            return False
        
        print("✅ Database connection: SUCCESS")
        
        # Show engine info
        engine_info = db_manager.get_engine_info()
        print(f"\nDatabase URL: {engine_info['url']}")
        print(f"Driver: {engine_info['driver']}")
        print(f"Pool size: {engine_info['pool_size']}")
        print(f"Checked out: {engine_info['checked_out']}")
        print(f"Overflow: {engine_info['overflow']}")
        
        # Show migration status
        migration_manager = MigrationManager(db_manager)
        try:
            applied_migrations = migration_manager.get_applied_migrations()
            print(f"\nApplied migrations: {len(applied_migrations)}")
            for migration in applied_migrations:
                print(f"  - {migration}")
        except Exception as e:
            print(f"Could not check migrations: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to check database status: {str(e)}")
        return False
    finally:
        close_database_manager()


def test_connection(args: Any):
    """Test database connection."""
    try:
        logger.info("Testing database connection...")
        
        db_manager = initialize_database_manager()
        
        if db_manager.test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        print(f"❌ Database connection failed: {str(e)}")
        return False
    finally:
        close_database_manager()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Football Simulation Database Management")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize database schema')
    init_parser.add_argument('--force', action='store_true', 
                           help='Drop existing tables before creating')
    init_parser.set_defaults(func=init_database)
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify database schema')
    verify_parser.set_defaults(func=verify_database)
    
    # Drop command
    drop_parser = subparsers.add_parser('drop', help='Drop database schema')
    drop_parser.add_argument('--confirm', action='store_true', 
                           help='Confirm destructive operation')
    drop_parser.set_defaults(func=drop_database)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show database status')
    status_parser.set_defaults(func=show_status)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test database connection')
    test_parser.set_defaults(func=test_connection)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the command
    try:
        success = args.func(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Command failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()