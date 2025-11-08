"""
Authentication API routes for LabLink System
Provides endpoints for user registration, login, and token refresh
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User, UserRole, db
from backend.auth import hash_password, verify_password, generate_tokens


# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request Body:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "SecurePass123",
            "role": "student"  # or "faculty"
        }
    
    Returns:
        201: User registered successfully
        400: Validation error or user already exists
        500: Server error
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Validation error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        role = data['role'].lower()
        
        # Validate username and email are not empty
        if not username or not email:
            return jsonify({
                'error': 'Validation error',
                'message': 'Username and email cannot be empty'
            }), 400
        
        # Validate password length
        if len(password) < 6:
            return jsonify({
                'error': 'Validation error',
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        # Validate role
        if role not in ['student', 'faculty']:
            return jsonify({
                'error': 'Validation error',
                'message': 'Role must be either "student" or "faculty"'
            }), 400
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({
                'error': 'Validation error',
                'message': 'Username already exists'
            }), 400
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({
                'error': 'Validation error',
                'message': 'Email already exists'
            }), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user role enum
        user_role = UserRole.STUDENT if role == 'student' else UserRole.FACULTY
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=user_role
        )
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': new_user.id,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens
    
    Request Body:
        {
            "username": "john_doe",
            "password": "SecurePass123"
        }
    
    Returns:
        200: Login successful with tokens
        400: Missing credentials
        401: Invalid credentials
        500: Server error
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Username and password are required'
            }), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Validate credentials are not empty
        if not username or not password:
            return jsonify({
                'error': 'Validation error',
                'message': 'Username and password cannot be empty'
            }), 400
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if not user or not verify_password(password, user.password_hash):
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid username or password'
            }), 401
        
        # Generate tokens
        tokens = generate_tokens(user)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    
    Headers:
        Authorization: Bearer <refresh_token>
    
    Returns:
        200: New access token generated
        401: Invalid or expired refresh token
        500: Server error
    """
    try:
        # Get current user from refresh token
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'Authentication failed',
                'message': 'User not found'
            }), 401
        
        # Generate new tokens
        tokens = generate_tokens(user)
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token']
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500
