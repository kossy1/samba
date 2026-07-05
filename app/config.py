# app/config.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Session - Use Flask's built-in session
    SESSION_COOKIE_NAME = 'poly_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # Application
    APP_NAME = os.environ.get('APP_NAME', 'Polytechnic Ibadan Interaction System')
    INSTITUTION_NAME = os.environ.get('INSTITUTION_NAME', 'The Polytechnic, Ibadan')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    KV_REST_API_URL = os.environ.get('KV_REST_API_URL')
    KV_REST_API_TOKEN = os.environ.get('KV_REST_API_TOKEN')
    
    # File uploads
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', 'pdf,doc,docx,jpg,jpeg,png').split(',')
    
    # Security
    PASSWORD_HASH_SALT = os.environ.get('PASSWORD_HASH_SALT', 'poly-salt')
    BCRYPT_ROUNDS = int(os.environ.get('BCRYPT_ROUNDS', 12))
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5000').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
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