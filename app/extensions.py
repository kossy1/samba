# app/extensions.py
import os
import redis
from flask_session import Session
from flask import Flask
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

class RedisClient:
    """Redis client wrapper supporting both local Redis and Vercel KV"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            # Check if we're using Vercel KV
            kv_url = os.getenv('KV_REST_API_URL')
            kv_token = os.getenv('KV_REST_API_TOKEN')
            
            if kv_url and kv_token:
                # For Vercel KV (Upstash), use the Redis URL with token
                parsed = urlparse(kv_url)
                if parsed.scheme == 'redis':
                    # Reconstruct URL with token as password
                    redis_url = f"redis://:{kv_token}@{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/') if parsed.path else '0'}"
                    cls._instance = redis.from_url(redis_url, decode_responses=True)
                    print("✅ Connected to Vercel KV (Production)")
                else:
                    # Fallback to direct connection
                    cls._instance = redis.Redis(
                        host=parsed.hostname,
                        port=parsed.port,
                        password=kv_token,
                        decode_responses=True
                    )
                    print("✅ Connected to Vercel KV (Production - Direct)")
            else:
                # Use local Redis
                redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
                cls._instance = redis.from_url(redis_url, decode_responses=True)
                print(f"✅ Connected to local Redis at {redis_url} (Development)")
        
        return cls._instance
    
    @classmethod
    def get_client(cls):
        """Get the Redis instance"""
        return cls._instance

# Initialize Redis client - FIXED: Use get_client() instead of get()
kv = RedisClient.get_client()

# Initialize Flask-Session
session_store = Session()

def init_extensions(app: Flask):
    """Initialize all extensions with the app"""
    # Configure session to use Redis
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = kv
    
    # Session configuration
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = os.getenv('SESSION_KEY_PREFIX', 'poly_session:')
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize session
    session_store.init_app(app)
    
    return kv, session_store