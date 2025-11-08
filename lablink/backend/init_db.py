"""
Database initialization script for LabLink System
This script initializes the database using Flask-Migrate
"""
import os
from flask import Flask
from flask_migrate import Migrate, init as migrate_init, migrate as migrate_migrate, upgrade as migrate_upgrade
from models import db

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL', 'postgresql://lablink:lablink@localhost:5432/lablink')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    return app

def init_database():
    """Initialize database with Flask-Migrate"""
    app = create_app()
    migrate = Migrate(app, db)
    
    with app.app_context():
        print("Initializing database...")
        
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Create indexes (already handled by SQLAlchemy)
        print("✓ Database indexes created successfully")
        
        print("\nDatabase initialization complete!")
        print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

def setup_migrations():
    """Set up Flask-Migrate for database migrations"""
    app = create_app()
    migrate = Migrate(app, db)
    
    with app.app_context():
        print("Setting up database migrations...")
        
        # Check if migrations folder exists
        if not os.path.exists('migrations'):
            print("Initializing migrations folder...")
            migrate_init()
            print("✓ Migrations folder created")
        
        print("\nMigrations setup complete!")
        print("To create a new migration, run: flask db migrate -m 'description'")
        print("To apply migrations, run: flask db upgrade")

def drop_all_tables():
    """Drop all tables (use with caution!)"""
    app = create_app()
    
    with app.app_context():
        print("WARNING: This will drop all tables!")
        confirm = input("Type 'yes' to confirm: ")
        
        if confirm.lower() == 'yes':
            db.drop_all()
            print("✓ All tables dropped")
        else:
            print("Operation cancelled")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init':
            init_database()
        elif command == 'setup-migrations':
            setup_migrations()
        elif command == 'drop':
            drop_all_tables()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: init, setup-migrations, drop")
    else:
        print("Usage: python init_db.py [command]")
        print("Commands:")
        print("  init             - Initialize database and create tables")
        print("  setup-migrations - Set up Flask-Migrate for migrations")
        print("  drop             - Drop all tables (requires confirmation)")
