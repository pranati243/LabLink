#!/usr/bin/env python3
"""
LabLink System Startup Script
Checks database connection, runs migrations if needed, and starts the Flask server
"""
import os
import sys
from pathlib import Path

# Load environment variables from .env file FIRST before any imports
from dotenv import load_dotenv
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Now import backend modules
from backend.app import create_app
from backend.models import db


def check_database_connection(app):
    """
    Check if database connection is working
    
    Args:
        app: Flask application instance
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with app.app_context():
            # Try to execute a simple query
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("\nPlease ensure:")
        print("  1. Database is accessible")
        print("  2. Database exists (see backend/init_db.py)")
        print("  3. DATABASE_URL environment variable is set correctly")
        return False


def initialize_database(app):
    """
    Initialize database tables if they don't exist
    
    Args:
        app: Flask application instance
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ Database tables initialized")
            return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False


def main():
    """Main startup function"""
    print("=" * 60)
    print("LabLink System - Starting Application")
    print("=" * 60)
    print()
    
    # Get configuration from environment
    config_name = os.getenv('FLASK_ENV', 'development')
    print(f"Environment: {config_name}")
    print()
    
    # Create Flask application
    try:
        app = create_app(config_name)
        print("✓ Flask application created")
    except Exception as e:
        print(f"✗ Failed to create Flask application: {e}")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection(app):
        sys.exit(1)
    
    # Initialize database tables
    if not initialize_database(app):
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Application Ready!")
    print("=" * 60)
    print()
    
    # Get server configuration
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    
    # Start server
    if config_name == 'production':
        print(f"Starting production server on {host}:{port}")
        print("Note: In production, use gunicorn instead of Flask development server")
        print("Example: gunicorn --bind 0.0.0.0:5000 --workers 4 run:app")
        print()
    else:
        print(f"Starting development server on {host}:{port}")
        print(f"Debug mode: {debug}")
        print()
        print(f"Access the application at: http://localhost:{port}")
        print(f"Health check endpoint: http://localhost:{port}/health")
        print(f"API documentation: See API_DOCUMENTATION.md")
        print()
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Server error: {e}")
        sys.exit(1)


# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    main()
