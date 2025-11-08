"""
Authentication module for LabLink System
Handles password hashing, JWT token generation, and token validation
"""
from datetime import timedelta
from functools import wraps
import bcrypt
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    verify_jwt_in_request,
    get_jwt
)
from backend.models import User, UserRole, db


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with cost factor 12
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password to verify
        password_hash: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_tokens(user: User) -> dict:
    """
    Generate JWT access and refresh tokens for a user
    
    Args:
        user: User object
        
    Returns:
        Dictionary containing access_token and refresh_token
    """
    # Create token identity with user ID (must be string for JWT)
    identity = str(user.id)
    
    # Add user role and username to token claims
    additional_claims = {
        'role': user.role.value,
        'username': user.username
    }
    
    # Generate tokens with 1 hour expiration for access, 30 days for refresh
    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )
    
    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=additional_claims,
        expires_delta=timedelta(days=30)
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def get_current_user() -> User:
    """
    Get the current authenticated user from JWT token
    
    Returns:
        User object of the authenticated user
        
    Raises:
        Exception if user not found
    """
    user_id = get_jwt_identity()
    # Convert string ID back to integer
    user = User.query.get(int(user_id))
    
    if not user:
        raise Exception('User not found')
    
    return user


def get_current_user_role() -> str:
    """
    Get the role of the current authenticated user from JWT claims
    
    Returns:
        User role as string ('student' or 'faculty')
    """
    claims = get_jwt()
    return claims.get('role')


def jwt_required(fn):
    """
    Decorator to protect routes requiring authentication
    Validates JWT token and ensures user exists
    
    Usage:
        @app.route('/protected')
        @jwt_required
        def protected_route():
            return jsonify(message='Access granted')
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Verify JWT token is present and valid
            verify_jwt_in_request()
            
            # Verify user still exists in database
            user = get_current_user()
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'error': 'Authentication required',
                'message': str(e)
            }), 401
    
    return wrapper


def role_required(*allowed_roles):
    """
    Decorator to protect routes requiring specific user roles
    Must be used after @jwt_required decorator
    
    Args:
        allowed_roles: Variable number of role strings ('student', 'faculty')
        
    Usage:
        @app.route('/faculty-only')
        @jwt_required
        @role_required('faculty')
        def faculty_route():
            return jsonify(message='Faculty access granted')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Get user role from JWT claims
                user_role = get_current_user_role()
                
                # Check if user role is in allowed roles
                if user_role not in allowed_roles:
                    return jsonify({
                        'error': 'Authorization failed',
                        'message': f'Access denied. Required role: {", ".join(allowed_roles)}'
                    }), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Authorization failed',
                    'message': str(e)
                }), 403
        
        return wrapper
    return decorator
