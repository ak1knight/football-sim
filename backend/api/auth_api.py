"""
Authentication API for user registration and login.

Provides endpoints for registering new users and authenticating existing users.
"""
from flask import Blueprint, request, jsonify
from database.connection import get_db_manager
from database.dao import UserDAO
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600

def get_user_id_from_jwt(request):
    """Extract user_id from Authorization header JWT."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except Exception as e:
        return None

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    Expects JSON: { "username": ..., "email": ..., "password": ..., "first_name": ..., "last_name": ... }
    """
    data = request.get_json()
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

    db_manager = get_db_manager()
    if not db_manager:
        return jsonify({'success': False, 'error': 'Database connection not available'}), 500

    user_dao = UserDAO(db_manager)
    if user_dao.username_exists(data['username']):
        return jsonify({'success': False, 'error': 'Username already exists'}), 400
    if user_dao.email_exists(data['email']):
        return jsonify({'success': False, 'error': 'Email already exists'}), 400

    try:
        user_id = user_dao.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        return jsonify({'success': True, 'user_id': user_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user.
    Expects JSON: { "username": ..., "password": ... }
    Returns JWT on success.
    """
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'error': 'Username and password required'}), 400

    db_manager = get_db_manager()
    if not db_manager:
        return jsonify({'success': False, 'error': 'Database connection not available'}), 500

    user_dao = UserDAO(db_manager)
    user = user_dao.authenticate_user(data['username'], data['password'])
    if user:
        # Convert UUID fields to strings for JSON serialization
        import uuid
        user_serializable = {}
        for k, v in user.items():
            if isinstance(v, uuid.UUID):
                user_serializable[k] = str(v)
            else:
                user_serializable[k] = v

        payload = {
            "user_id": str(user["id"]) if isinstance(user["id"], uuid.UUID) else user["id"],
            "username": user["username"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return jsonify({'success': True, 'token': token, 'user': user_serializable})
    else:
        return jsonify({'success': False, 'error': 'Invalid username or password'}), 401