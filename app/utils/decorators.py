# app/utils/decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session:
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if session['user_role'] not in allowed_roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator for admin-only routes"""
    return role_required(['admin'])(f)

def lecturer_required(f):
    """Decorator for lecturer-only routes"""
    return role_required(['lecturer'])(f)

def student_required(f):
    """Decorator for student-only routes"""
    return role_required(['student'])(f)

def token_required(f):
    """Decorator for API token authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            from app.utils.security import verify_jwt_token
            payload = verify_jwt_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add user info to request context
            request.user_id = payload.get('user_id')
            request.user_role = payload.get('role')
            
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def register_decorators(app):
    """Register custom Jinja2 filters and decorators"""
    app.jinja_env.globals.update(
        is_authenticated=lambda: 'user_id' in session,
        current_user_role=lambda: session.get('user_role'),
        current_user_name=lambda: session.get('user_name')
    )