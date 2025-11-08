"""
Middleware decorators for LabLink System
Provides authentication and authorization middleware for route protection
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from backend.auth import get_current_user, get_current_user_role


def jwt_required(fn):
    """
    Decorator to protect routes requiring authentication
    Validates JWT token and ensures user exists in database
    
    This decorator:
    - Verifies JWT token is present and valid
    - Checks token hasn't expired
    - Ensures user still exists in database
    - Returns 401 error for authentication failures
    
    Usage:
        @app.route('/protected')
        @jwt_required
        def protected_route():
            user = get_current_user()
            return jsonify(message=f'Hello {user.username}')
    
    Returns:
        401: Authentication required or token invalid/expired
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Verify JWT token is present and valid
            verify_jwt_in_request()
            
            # Verify user still exists in database
            user = get_current_user()
            
            # Call the protected route
            return fn(*args, **kwargs)
            
        except Exception as e:
            error_message = str(e)
            
            # Provide specific error messages for common issues
            if 'expired' in error_message.lower():
                return jsonify({
                    'error': 'Token expired',
                    'message': 'Your session has expired. Please login again.'
                }), 401
            elif 'not found' in error_message.lower():
                return jsonify({
                    'error': 'User not found',
                    'message': 'User account no longer exists.'
                }), 401
            else:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Valid authentication token required to access this resource.'
                }), 401
    
    return wrapper


def role_required(*allowed_roles):
    """
    Decorator to protect routes requiring specific user roles
    Must be used after @jwt_required decorator
    
    This decorator:
    - Checks user role from JWT token claims
    - Verifies role is in the allowed roles list
    - Returns 403 error for authorization failures
    
    Args:
        allowed_roles: Variable number of role strings ('student', 'faculty')
        
    Usage:
        @app.route('/faculty-only')
        @jwt_required
        @role_required('faculty')
        def faculty_route():
            return jsonify(message='Faculty access granted')
        
        @app.route('/all-users')
        @jwt_required
        @role_required('student', 'faculty')
        def all_users_route():
            return jsonify(message='All authenticated users can access')
    
    Returns:
        403: Insufficient permissions or authorization failed
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Get user role from JWT claims
                user_role = get_current_user_role()
                
                if not user_role:
                    return jsonify({
                        'error': 'Authorization failed',
                        'message': 'User role not found in token.'
                    }), 403
                
                # Check if user role is in allowed roles
                if user_role not in allowed_roles:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'message': f'Access denied. This resource requires one of the following roles: {", ".join(allowed_roles)}'
                    }), 403
                
                # Call the protected route
                return fn(*args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    'error': 'Authorization failed',
                    'message': str(e)
                }), 403
        
        return wrapper
    return decorator


def student_required(fn):
    """
    Convenience decorator for student-only routes
    Equivalent to @role_required('student')
    
    Usage:
        @app.route('/student-dashboard')
        @jwt_required
        @student_required
        def student_dashboard():
            return jsonify(message='Student dashboard')
    """
    @wraps(fn)
    @role_required('student')
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def faculty_required(fn):
    """
    Convenience decorator for faculty-only routes
    Equivalent to @role_required('faculty')
    
    Usage:
        @app.route('/faculty-dashboard')
        @jwt_required
        @faculty_required
        def faculty_dashboard():
            return jsonify(message='Faculty dashboard')
    """
    @wraps(fn)
    @role_required('faculty')
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def handle_jwt_errors(app):
    """
    Register JWT error handlers with Flask app
    Provides consistent error responses for JWT-related errors
    
    Args:
        app: Flask application instance
        
    Usage:
        from flask import Flask
        from flask_jwt_extended import JWTManager
        from backend.middleware import handle_jwt_errors
        
        app = Flask(__name__)
        jwt = JWTManager(app)
        handle_jwt_errors(app)
    """
    from flask_jwt_extended import JWTManager
    
    jwt = JWTManager(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired token errors"""
        return jsonify({
            'error': 'Token expired',
            'message': 'Your session has expired. Please login again.'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid token errors"""
        return jsonify({
            'error': 'Invalid token',
            'message': 'The authentication token is invalid.'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing token errors"""
        return jsonify({
            'error': 'Authorization required',
            'message': 'Authentication token is missing.'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Handle revoked token errors"""
        return jsonify({
            'error': 'Token revoked',
            'message': 'The authentication token has been revoked.'
        }), 401
    
    return jwt
