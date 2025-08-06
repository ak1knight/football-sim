"""
Base Data Access Object (DAO) classes for the Football Simulation application.

This module provides abstract base classes and common functionality for all DAOs
using SQLAlchemy Core.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
import logging
from sqlalchemy import Table, select, insert, update, delete, and_, or_
from sqlalchemy.engine import Connection
from ..connection import DatabaseManager

logger = logging.getLogger(__name__)


class DAOError(Exception):
    """Exception raised for DAO operations."""
    pass


class BaseDAO(ABC):
    """
    Abstract base class for Data Access Objects.
    
    Provides common database operations and patterns for all entities.
    """
    
    def __init__(self, db_manager: DatabaseManager, table: Table):
        """
        Initialize the DAO.
        
        Args:
            db_manager: DatabaseManager instance
            table: SQLAlchemy Table object
        """
        self.db_manager = db_manager
        self.table = table
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def _row_to_dict(self, row: Any) -> Dict[str, Any]:
        """Convert a database row to dictionary."""
        if row is None:
            return {}
        return dict(row._mapping) if hasattr(row, '_mapping') else dict(row)
    
    def _rows_to_list(self, rows: List[Any]) -> List[Dict[str, Any]]:
        """Convert database rows to list of dictionaries."""
        return [self._row_to_dict(row) for row in rows]
    
    def create(self, data: Dict[str, Any]) -> str:
        """
        Create a new record.
        
        Args:
            data: Dictionary of field values
            
        Returns:
            ID of the created record
            
        Raises:
            DAOError: If creation fails
        """
        try:
            with self.db_manager.get_db_transaction() as conn:
                result = conn.execute(
                    insert(self.table).values(**data).returning(self.table.c.id)
                )
                record_id = result.fetchone()[0]
                self.logger.debug(f"Created {self.table.name} record with ID: {record_id}")
                return str(record_id)
        except Exception as e:
            self.logger.error(f"Failed to create {self.table.name} record: {str(e)}")
            raise DAOError(f"Failed to create {self.table.name} record: {str(e)}")
    
    def get_by_id(self, record_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        Get a record by ID.
        
        Args:
            record_id: Record ID
            
        Returns:
            Dictionary representation of the record or None if not found
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select(self.table).where(self.table.c.id == record_id)
                )
                row = result.fetchone()
                return self._row_to_dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get {self.table.name} by ID {record_id}: {str(e)}")
            raise DAOError(f"Failed to get {self.table.name} by ID: {str(e)}")
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all records.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of record dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                query = select(self.table).offset(offset)
                if limit:
                    query = query.limit(limit)
                
                result = conn.execute(query)
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get all {self.table.name} records: {str(e)}")
            raise DAOError(f"Failed to get all {self.table.name} records: {str(e)}")
    
    def update_by_id(self, record_id: Union[str, UUID], data: Dict[str, Any]) -> bool:
        """
        Update a record by ID.
        
        Args:
            record_id: Record ID
            data: Dictionary of field values to update
            
        Returns:
            True if record was updated, False if not found
            
        Raises:
            DAOError: If update fails
        """
        try:
            with self.db_manager.get_db_transaction() as conn:
                result = conn.execute(
                    update(self.table)
                    .where(self.table.c.id == record_id)
                    .values(**data)
                )
                updated = result.rowcount > 0
                if updated:
                    self.logger.debug(f"Updated {self.table.name} record ID: {record_id}")
                return updated
        except Exception as e:
            self.logger.error(f"Failed to update {self.table.name} record {record_id}: {str(e)}")
            raise DAOError(f"Failed to update {self.table.name} record: {str(e)}")
    
    def delete_by_id(self, record_id: Union[str, UUID]) -> bool:
        """
        Delete a record by ID.
        
        Args:
            record_id: Record ID
            
        Returns:
            True if record was deleted, False if not found
            
        Raises:
            DAOError: If deletion fails
        """
        try:
            with self.db_manager.get_db_transaction() as conn:
                result = conn.execute(
                    delete(self.table).where(self.table.c.id == record_id)
                )
                deleted = result.rowcount > 0
                if deleted:
                    self.logger.debug(f"Deleted {self.table.name} record ID: {record_id}")
                return deleted
        except Exception as e:
            self.logger.error(f"Failed to delete {self.table.name} record {record_id}: {str(e)}")
            raise DAOError(f"Failed to delete {self.table.name} record: {str(e)}")
    
    def exists(self, record_id: Union[str, UUID]) -> bool:
        """
        Check if a record exists by ID.
        
        Args:
            record_id: Record ID
            
        Returns:
            True if record exists, False otherwise
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select([self.table.c.id]).where(self.table.c.id == record_id)
                )
                return result.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Failed to check existence of {self.table.name} record {record_id}: {str(e)}")
            return False
    
    def count(self, where_clause=None) -> int:
        """
        Count records in the table.
        
        Args:
            where_clause: Optional WHERE clause condition
            
        Returns:
            Number of records
        """
        try:
            from sqlalchemy import func
            
            with self.db_manager.get_db_connection() as conn:
                query = select([func.count(self.table.c.id)])
                if where_clause is not None:
                    query = query.where(where_clause)
                
                result = conn.execute(query)
                return result.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Failed to count {self.table.name} records: {str(e)}")
            raise DAOError(f"Failed to count {self.table.name} records: {str(e)}")
    
    def find_by_fields(self, fields: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find records by field values.
        
        Args:
            fields: Dictionary of field names and values
            limit: Optional limit on number of results
            
        Returns:
            List of matching record dictionaries
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                conditions = []
                for field_name, value in fields.items():
                    if hasattr(self.table.c, field_name):
                        conditions.append(getattr(self.table.c, field_name) == value)
                
                if not conditions:
                    raise ValueError("No valid fields provided")
                
                query = select(self.table).where(and_(*conditions))
                if limit:
                    query = query.limit(limit)
                
                result = conn.execute(query)
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to find {self.table.name} records by fields: {str(e)}")
            raise DAOError(f"Failed to find {self.table.name} records by fields: {str(e)}")
    
    def bulk_insert(self, records: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple records in a single transaction.
        
        Args:
            records: List of record dictionaries
            
        Returns:
            List of created record IDs
            
        Raises:
            DAOError: If bulk insert fails
        """
        if not records:
            return []
        
        try:
            with self.db_manager.get_db_transaction() as conn:
                result = conn.execute(
                    insert(self.table).values(records).returning(self.table.c.id)
                )
                record_ids = [str(row[0]) for row in result.fetchall()]
                self.logger.debug(f"Bulk inserted {len(record_ids)} {self.table.name} records")
                return record_ids
        except Exception as e:
            self.logger.error(f"Failed to bulk insert {self.table.name} records: {str(e)}")
            raise DAOError(f"Failed to bulk insert {self.table.name} records: {str(e)}")


class UserScopedDAO(BaseDAO):
    """
    Base DAO for entities that are scoped to users.
    
    Provides additional methods for filtering by user ID.
    """
    
    def get_by_user_id(self, user_id: Union[str, UUID], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get records for a specific user.
        
        Args:
            user_id: User ID
            limit: Optional limit on results
            
        Returns:
            List of user's record dictionaries
        """
        return self.find_by_fields({'user_id': user_id}, limit=limit)
    
    def count_by_user_id(self, user_id: Union[str, UUID]) -> int:
        """
        Count records for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of user's records
        """
        return self.count(where_clause=(self.table.c.user_id == user_id))
    
    def delete_by_user_id(self, user_id: Union[str, UUID]) -> int:
        """
        Delete all records for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of records deleted
            
        Raises:
            DAOError: If deletion fails
        """
        try:
            with self.db_manager.get_db_transaction() as conn:
                result = conn.execute(
                    delete(self.table).where(self.table.c.user_id == user_id)
                )
                deleted_count = result.rowcount
                if deleted_count > 0:
                    self.logger.debug(f"Deleted {deleted_count} {self.table.name} records for user {user_id}")
                return deleted_count
        except Exception as e:
            self.logger.error(f"Failed to delete {self.table.name} records for user {user_id}: {str(e)}")
            raise DAOError(f"Failed to delete {self.table.name} records for user: {str(e)}")