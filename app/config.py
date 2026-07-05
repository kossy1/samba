import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Application
    APP_NAME = os.environ.get('APP_NAME', 'Polytechnic Ibadan Interaction System')
    INSTITUTION_NAME = os.environ.get('INSTITUTION_NAME', 'The Polytechnic, Ibadan')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    KV_REST_API_URL = os.environ.get('KV_REST_API_URL')
    KV_REST_API_TOKEN = os.environ.get('KV_REST_API_TOKEN')
    
    # Session
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = os.environ.get('SESSION_KEY_PREFIX', 'poly_session:')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_REDIS = None  # Will be set after Redis initialization
    
    # File uploads
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', 'pdf,doc,docx,jpg,jpeg,png').split(',')
    
    # Security
    PASSWORD_HASH_SALT = os.environ.get('PASSWORD_HASH_SALT', 'poly-salt')
    BCRYPT_ROUNDS = int(os.environ.get('BCRYPT_ROUNDS', 12))
    WTF_CSRF_ENABLED = os.environ.get('CSRF_ENABLED', 'True').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', 3600))
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5000').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Cache
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_KEY_PREFIX = os.environ.get('CACHE_KEY_PREFIX', 'poly_cache:')
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Feature flags
    ENABLE_REGISTRATION = os.environ.get('ENABLE_REGISTRATION', 'True').lower() == 'true'
    ENABLE_DISCUSSIONS = os.environ.get('ENABLE_DISCUSSIONS', 'True').lower() == 'true'
    ENABLE_ANNOUNCEMENTS = os.environ.get('ENABLE_ANNOUNCEMENTS', 'True').lower() == 'true'
    ENABLE_ASSIGNMENTS = os.environ.get('ENABLE_ASSIGNMENTS', 'True').lower() == 'true'
    ENABLE_FILE_UPLOADS = os.environ.get('ENABLE_FILE_UPLOADS', 'True').lower() == 'true'
    
    # Deployment
    IS_VERCEL = os.environ.get('VERCEL', 'False').lower() == 'true'
    VERCEL_URL = os.environ.get('VERCEL_URL')
    DEPLOYMENT_ENVIRONMENT = os.environ.get('DEPLOYMENT_ENVIRONMENT', 'development')

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    SESSION_COOKIE_SECURE = False
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    SESSION_COOKIE_SECURE = True
    TEMPLATES_AUTO_RELOAD = False
    PREFERRED_URL_SCHEME = 'https'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, DevelopmentConfig)