# app/extensions.py
import os
from flask import Flask, session as flask_session
from dotenv import load_dotenv
import logging
import json
from datetime import timedelta

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Redis, but handle it gracefully if not installed
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("⚠️ Redis module not installed. Using filesystem session.")

# Initialize Redis connection
kv = None
if REDIS_AVAILABLE:
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        kv = redis.from_url(redis_url, decode_responses=True)
        # Test connection
        kv.ping()
        logger.info("✅ Connected to Redis")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection error: {e}")
        kv = None

# Use Flask's built-in session (no Flask-Session)
session_store = None

def init_extensions(app: Flask):
    """Initialize all extensions with the app"""
    # Use Flask's built-in session
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_COOKIE_NAME'] = 'poly_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    logger.info("✅ Using Flask built-in session")
    
    return kv, None