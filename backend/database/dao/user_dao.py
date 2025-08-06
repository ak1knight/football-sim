"""
User Data Access Object for the Football Simulation application.

Handles all database operations related to users, including authentication,
profile management, and user-specific queries.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID
import bcrypt
from sqlalchemy import select, and_
from .base import BaseDAO, DAOError
from ..schema import users_table


class UserDAO(BaseDAO):
    """Data Access Object for User entities."""
    
    def __init__(self, db_manager):
        super().__init__(db_manager, users_table)
    
    def create_user(self, username: str, email: str, password: str, 
                   first_name: str | None = None, last_name: str | None = None) -> str:
        """
        Create a new user with hashed password.
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            User ID
            
        Raises:
            DAOError: If user creation fails
        """
        try:
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            user_data = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True
            }
            
            return self.create(user_data)
        except Exception as e:
            self.logger.error(f"Failed to create user {username}: {str(e)}")
            raise DAOError(f"Failed to create user: {str(e)}")
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User dictionary or None if not found
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select(self.table).where(self.table.c.username == username)
                )
                row = result.fetchone()
                return self._row_to_dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get user by username {username}: {str(e)}")
            raise DAOError(f"Failed to get user by username: {str(e)}")
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User dictionary or None if not found
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select(self.table).where(self.table.c.email == email)
                )
                row = result.fetchone()
                return self._row_to_dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get user by email {email}: {str(e)}")
            raise DAOError(f"Failed to get user by email: {str(e)}")
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user by username and password.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User dictionary if authentication successful, None otherwise
        """
        try:
            user = self.get_by_username(username)
            if not user:
                return None
            
            # Check if user is active
            if not user.get('is_active', False):
                return None
            
            # Verify password
            stored_hash = user['password_hash'].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                # Remove password hash from returned data
                user_data = user.copy()
                user_data.pop('password_hash', None)
                return user_data
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to authenticate user {username}: {str(e)}")
            raise DAOError(f"Failed to authenticate user: {str(e)}")
    
    def update_password(self, user_id: Union[str, UUID], new_password: str) -> bool:
        """
        Update user's password.
        
        Args:
            user_id: User ID
            new_password: New plain text password
            
        Returns:
            True if password was updated, False if user not found
        """
        try:
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            return self.update_by_id(user_id, {'password_hash': password_hash})
        except Exception as e:
            self.logger.error(f"Failed to update password for user {user_id}: {str(e)}")
            raise DAOError(f"Failed to update password: {str(e)}")
    
    def deactivate_user(self, user_id: Union[str, UUID]) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was deactivated, False if not found
        """
        return self.update_by_id(user_id, {'is_active': False})
    
    def activate_user(self, user_id: Union[str, UUID]) -> bool:
        """
        Activate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was activated, False if not found
        """
        return self.update_by_id(user_id, {'is_active': True})
    
    def username_exists(self, username: str) -> bool:
        """
        Check if username already exists.
        
        Args:
            username: Username to check
            
        Returns:
            True if username exists, False otherwise
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select([self.table.c.id]).where(self.table.c.username == username)
                )
                return result.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Failed to check username existence {username}: {str(e)}")
            return False
    
    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if email exists, False otherwise
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                result = conn.execute(
                    select([self.table.c.id]).where(self.table.c.email == email)
                )
                return result.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Failed to check email existence {email}: {str(e)}")
            return False
    
    def get_active_users(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all active users.
        
        Args:
            limit: Optional limit on results
            
        Returns:
            List of active user dictionaries (without password hashes)
        """
        try:
            with self.db_manager.get_db_connection() as conn:
                columns = [col for col in self.table.c if col.name != 'password_hash']
                query = select(columns).where(self.table.c.is_active == True)
                
                if limit:
                    query = query.limit(limit)
                
                result = conn.execute(query)
                return self._rows_to_list(result.fetchall())
        except Exception as e:
            self.logger.error(f"Failed to get active users: {str(e)}")
            raise DAOError(f"Failed to get active users: {str(e)}")
    
    def update_profile(self, user_id: Union[str, UUID], profile_data: Dict[str, Any]) -> bool:
        """
        Update user profile information.
        
        Args:
            user_id: User ID
            profile_data: Dictionary of profile fields to update
            
        Returns:
            True if profile was updated, False if user not found
        """
        # Filter out fields that shouldn't be updated directly
        allowed_fields = {'first_name', 'last_name', 'email'}
        filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
        
        if not filtered_data:
            return False
        
        return self.update_by_id(user_id, filtered_data)
    
    def get_user_stats(self, user_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Get user statistics (seasons, games, etc.).
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user statistics
        """
        try:
            # This would typically involve joins with other tables
            # For now, return basic user info
            user = self.get_by_id(user_id)
            if not user:
                return {}
            
            # Remove sensitive information
            user_stats = user.copy()
            user_stats.pop('password_hash', None)
            
            # Add computed statistics (would be implemented with proper joins)
            user_stats.update({
                'total_seasons': 0,  # Would be calculated from seasons table
                'total_games': 0,    # Would be calculated from games table
                'member_since': user.get('created_at'),
                'last_activity': user.get('updated_at')
            })
            
            return user_stats
        except Exception as e:
            self.logger.error(f"Failed to get user stats for {user_id}: {str(e)}")
            raise DAOError(f"Failed to get user stats: {str(e)}")