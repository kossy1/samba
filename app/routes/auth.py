# app/routes/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app
from app.services.user_service import UserService
import logging

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        current_app.logger.info(f"Login attempt for user: {user_id}")
        
        if not user_id or not password:
            flash('Please enter both user ID and password.', 'error')
            return render_template('auth/login.html')
        
        try:
            # Authenticate user
            user_service = UserService()
            user = user_service.authenticate(user_id, password)
            
            if user:
                current_app.logger.info(f"Login successful for user: {user_id}")
                # Ensure all session values are strings
                session['user_id'] = str(user.user_id)
                session['user_role'] = str(user.role)
                session['user_name'] = str(user.full_name)
                session['user_email'] = str(user.email)
                
                flash(f'Welcome back, {user.full_name}!', 'success')
                
                # Redirect based on role
                if user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user.role == 'lecturer':
                    return redirect(url_for('lecturer.dashboard'))
                else:
                    return redirect(url_for('student.dashboard'))
            else:
                current_app.logger.warning(f"Login failed for user: {user_id}")
                flash('Invalid credentials. Please try again.', 'error')
        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))