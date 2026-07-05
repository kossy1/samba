# app/utils/security_simple.py
import hashlib
import secrets
import os
import re
from datetime import datetime, timedelta
import jwt
from flask import current_app

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with salt
    Returns: salt$hash
    """
    salt = secrets.token_hex(16)
    # Use PBKDF2 for better security
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return f"{salt}${password_hash}"

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash
    Expected format: salt$hash
    """
    if not hashed:
        print("No hash provided")
        return False
    
    if '$' not in hashed:
        print(f"Invalid hash format: {hashed[:50]}...")
        return False
    
    try:
        salt, stored_hash = hashed.split('$', 1)
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        # Debug output
        print(f"Salt: {salt[:10]}...")
        print(f"Stored hash: {stored_hash[:20]}...")
        print(f"Computed hash: {computed_hash[:20]}...")
        
        return computed_hash == stored_hash
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def generate_jwt_token(user_id: str, role: str) -> str:
    """Generate JWT token for API authentication"""
    secret = os.getenv('SECRET_KEY', 'dev-secret-key')
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, secret, algorithm='HS256')

def verify_jwt_token(token: str):
    """Verify JWT token"""
    secret = os.getenv('SECRET_KEY', 'dev-secret-key')
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None