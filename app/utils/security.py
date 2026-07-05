# app/utils/security.py
import bcrypt
import os
import re
from datetime import datetime, timedelta
import jwt
from functools import wraps
from flask import request, jsonify, session, redirect, url_for, flash

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt(rounds=int(os.getenv('BCRYPT_ROUNDS', 12)))
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
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