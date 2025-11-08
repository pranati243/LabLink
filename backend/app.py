"""
Main Flask application for LabLink System
Entry point for the backend API
"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import flask_jwt_extended
from backend.models import db
from backend.middleware import handle_jwt_errors
from backend.config import get_config
from backend.auth_routes import auth_bp
from backend.component_routes import component_bp
from backend.request_routes import request_bp
from backend.transaction_routes import transaction_bp


def create_app(config_name=None):
    """
    Application factory for creating Flask app instance
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration from config.py
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure CORS
    CORS(
        app,
        origins=app.config['CORS_ORIGINS'],
        allow_headers=app.config['CORS_ALLOW_HEADERS'],
        methods=app.config['CORS_METHODS'],
        supports_credentials=True
    )
    
    # Initialize JWT with error handlers
    handle_jwt_errors(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(component_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(transaction_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = 'connected'
        except Exception:
            db_status = 'disconnected'
        
        return jsonify({
            'status': 'healthy' if db_status == 'connected' else 'degraded',
            'service': 'LabLink API',
            'database': db_status
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information"""
        return jsonify({
            'service': 'LabLink API',
            'version': '1.0.0',
            'environment': app.config.get('ENV', 'development'),
            'endpoints': {
                'auth': '/api/auth',
                'components': '/api/components',
                'requests': '/api/requests',
                'transactions': '/api/transactions',
                'health': '/health'
            }
        }), 200
    
    # Test endpoint with built-in JWT decorator
    @app.route('/test-jwt', methods=['GET'])
    @flask_jwt_extended.jwt_required()
    def test_jwt():
        """Test endpoint to verify JWT is working"""
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        return jsonify({
            'message': 'JWT is working!',
            'user_id': user_id
        }), 200
    
    return app


def register_error_handlers(app):
    """
    Register global error handlers for consistent error responses
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors"""
        if isinstance(error, HTTPException):
            message = error.description
        else:
            message = str(error)
        
        return jsonify({
            'error': 'Bad Request',
            'message': message,
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 Unauthorized errors"""
        if isinstance(error, HTTPException):
            message = error.description
        else:
            message = 'Authentication required'
        
        return jsonify({
            'error': 'Unauthorized',
            'message': message,
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors"""
        if isinstance(error, HTTPException):
            message = error.description
        else:
            message = 'Access forbidden'
        
        return jsonify({
            'error': 'Forbidden',
            'message': message,
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        if isinstance(error, HTTPException):
            message = error.description
        else:
            message = f'Resource not found: {request.path}'
        
        return jsonify({
            'error': 'Not Found',
            'message': message,
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 Method Not Allowed errors"""
        return jsonify({
            'error': 'Method Not Allowed',
            'message': f'The method {request.method} is not allowed for {request.path}',
            'status_code': 405
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        # Rollback any pending database transactions
        db.session.rollback()
        
        # Log the error (in production, this should go to a logging service)
        app.logger.error(f'Internal Server Error: {str(error)}')
        
        # Don't expose internal error details in production
        if app.config.get('DEBUG'):
            message = str(error)
        else:
            message = 'An internal server error occurred. Please try again later.'
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': message,
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors"""
        # Rollback any pending database transactions
        db.session.rollback()
        
        # Log the error
        app.logger.error(f'Unexpected Error: {str(error)}', exc_info=True)
        
        # Return 500 for unexpected errors
        if app.config.get('DEBUG'):
            message = str(error)
        else:
            message = 'An unexpected error occurred. Please try again later.'
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': message,
            'status_code': 500
        }), 500


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', True))
