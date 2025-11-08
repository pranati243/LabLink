"""
Configuration management for LabLink System
Provides development and production configurations with environment variable support
"""
import os
from datetime import timedelta


class Config:
    """Base configuration with common settings"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/lablink'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
        'pool_pre_ping': True,
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20'))
    }
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_HOURS', '1')))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_DAYS', '30')))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_CSRF_PROTECT = False  # Disable CSRF for API usage
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    
    # Application settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False


class DevelopmentConfig(Config):
    """Development configuration with debug mode enabled"""
    
    DEBUG = True
    TESTING = False
    
    # More verbose logging in development
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    
    # Relaxed CORS in development
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Pretty print JSON in development
    JSONIFY_PRETTYPRINT_REGULAR = True


class ProductionConfig(Config):
    """Production configuration with security hardening"""
    
    DEBUG = False
    TESTING = False
    
    # Stricter logging in production
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    
    # Require specific CORS origins in production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    
    # Additional security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    def __init__(self):
        """Validate production configuration on initialization"""
        super().__init__()
        
        # Ensure secure keys are set in production
        if self.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError('SECRET_KEY must be set in production environment')
        
        if self.JWT_SECRET_KEY == 'dev-jwt-secret-change-in-production':
            raise ValueError('JWT_SECRET_KEY must be set in production environment')


class TestingConfig(Config):
    """Testing configuration for running tests"""
    
    DEBUG = True
    TESTING = True
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'sqlite:///:memory:'
    )
    
    # SQLite doesn't support connection pooling options
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Shorter token expiration for tests
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=10)


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration object based on environment
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable
    
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config.get(config_name, DevelopmentConfig)
