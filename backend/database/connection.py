"""
Database connection management for the Football Simulation application.

This module provides the DatabaseManager class for handling PostgreSQL connections
using SQLAlchemy Core with connection pooling, transaction management, and error handling.
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class DatabaseManager:
    """
    Manages database connections and provides utilities for database operations.
    
    Uses SQLAlchemy Core for database operations with connection pooling
    and transaction management.
    """
    
    def __init__(self, database_url: Optional[str] = None, **engine_kwargs):
        """
        Initialize the database manager.
        
        Args:
            database_url: Database connection URL. If None, reads from DATABASE_URL env var.
            **engine_kwargs: Additional arguments to pass to create_engine.
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise DatabaseError("Database URL not provided and DATABASE_URL environment variable not set")
        
        # Default engine configuration for PostgreSQL
        default_engine_config = {
            'poolclass': QueuePool,
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 3600,  # 1 hour
            'echo': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        }
        
        # Merge user-provided config with defaults
        engine_config = {**default_engine_config, **engine_kwargs}
        
        try:
            self.engine = create_engine(self.database_url, **engine_config)
            self.metadata = MetaData()
            logger.info("Database engine created successfully")
        except Exception as e:
            logger.error(f"Failed to create database engine: {str(e)}")
            raise DatabaseError(f"Failed to create database engine: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the database connection.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def get_connection(self) -> Connection:
        """
        Get a database connection.
        
        Returns:
            SQLAlchemy Connection object.
            
        Raises:
            DatabaseError: If connection fails.
        """
        try:
            return self.engine.connect()
        except Exception as e:
            logger.error(f"Failed to get database connection: {str(e)}")
            raise DatabaseError(f"Failed to get database connection: {str(e)}")
    
    @contextmanager
    def get_db_connection(self):
        """
        Context manager for database connections.
        
        Automatically handles connection cleanup.
        
        Yields:
            SQLAlchemy Connection object.
            
        Example:
            with db_manager.get_db_connection() as conn:
                result = conn.execute(text("SELECT * FROM users"))
        """
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise DatabaseError(f"Database operation failed: {str(e)}")
        finally:
            if connection:
                connection.close()
    
    @contextmanager
    def get_db_transaction(self):
        """
        Context manager for database transactions.
        
        Automatically handles transaction commit/rollback and connection cleanup.
        
        Yields:
            SQLAlchemy Connection object with an active transaction.
            
        Example:
            with db_manager.get_db_transaction() as conn:
                conn.execute(text("INSERT INTO users ..."))
                # Transaction automatically committed if no exception
        """
        connection = None
        transaction = None
        try:
            connection = self.get_connection()
            transaction = connection.begin()
            yield connection
            transaction.commit()
            logger.debug("Database transaction committed")
        except Exception as e:
            if transaction:
                transaction.rollback()
                logger.debug("Database transaction rolled back")
            logger.error(f"Database transaction error: {str(e)}")
            raise DatabaseError(f"Database transaction failed: {str(e)}")
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string.
            params: Dictionary of parameters for the query.
            
        Returns:
            Query result.
            
        Raises:
            DatabaseError: If query execution fails.
        """
        try:
            with self.get_db_connection() as conn:
                result = conn.execute(text(query), params or {})
                if result.returns_rows:
                    return result.fetchall()
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise DatabaseError(f"Query execution failed: {str(e)}")
    
    def execute_transaction(self, queries: list, params_list: Optional[list] = None) -> None:
        """
        Execute multiple queries in a single transaction.
        
        Args:
            queries: List of SQL query strings.
            params_list: List of parameter dictionaries (one per query).
            
        Raises:
            DatabaseError: If any query fails.
        """
        if params_list and len(queries) != len(params_list):
            raise ValueError("Number of queries and parameter sets must match")
        
        try:
            with self.get_db_transaction() as conn:
                for i, query in enumerate(queries):
                    params = params_list[i] if params_list else {}
                    conn.execute(text(query), params)
                logger.debug(f"Executed {len(queries)} queries in transaction")
        except Exception as e:
            logger.error(f"Transaction execution failed: {str(e)}")
            raise DatabaseError(f"Transaction execution failed: {str(e)}")
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the database engine.
        
        Returns:
            Dictionary with engine information.
        """
        return {
            'url': str(self.engine.url).replace(self.engine.url.password or '', '***'),
            'driver': self.engine.dialect.driver,
            'pool_size': self.engine.pool.size(),
            'checked_out': self.engine.pool.checkedout(),
            'overflow': self.engine.pool.overflow(),
        }
    
    def close(self) -> None:
        """Close the database engine and all connections."""
        try:
            self.engine.dispose()
            logger.info("Database engine closed")
        except Exception as e:
            logger.error(f"Error closing database engine: {str(e)}")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def initialize_database_manager(database_url: Optional[str] = None, **engine_kwargs) -> DatabaseManager:
    """
    Initialize the global database manager instance.
    
    Args:
        database_url: Database connection URL.
        **engine_kwargs: Additional engine configuration.
        
    Returns:
        DatabaseManager instance.
    """
    global _db_manager
    _db_manager = DatabaseManager(database_url, **engine_kwargs)
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager instance.
        
    Raises:
        RuntimeError: If database manager not initialized.
    """
    if _db_manager is None:
        raise RuntimeError("Database manager not initialized. Call initialize_database_manager() first.")
    return _db_manager


def close_database_manager() -> None:
    """Close the global database manager."""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None