# app/routes/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app
from app.services.user_service import UserService
import logging

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page - supports username, email, matric number"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')  # Can be username, email, or matric number
        password = request.form.get('password')
        
        current_app.logger.info(f"Login attempt for user: {user_id}")
        
        if not user_id or not password:
            flash('Please enter both User ID/Matric Number and Password.', 'error')
            return render_template('auth/login.html')
        
        try:
            user_service = UserService()
            
            # Try to find user by various identifiers
            user = None
            
            # First, check if it's a matric number (student)
            if user_id and user_id.isdigit() or '/' in user_id:
                # Search for student by matric number
                all_users = user_service.get_all_users()
                for u in all_users:
                    if u.get('role') == 'student' and u.get('matric_no') == user_id:
                        # Found student by matric number
                        user = user_service.authenticate(u.get('user_id'), password)
                        break
            
            # If not found by matric, try as regular user_id
            if not user:
                user = user_service.authenticate(user_id, password)
            
            if user:
                current_app.logger.info(f"Login successful for user: {user.user_id}")
                session['user_id'] = user.user_id
                session['user_role'] = user.role
                session['user_name'] = user.full_name
                session['user_email'] = user.email
                
                # Store matric number for students
                if user.role == 'student' and hasattr(user, 'matric_no'):
                    session['matric_no'] = user.matric_no
                
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
                flash('Invalid credentials. Please check your User ID/Matric Number and Password.', 'error')
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