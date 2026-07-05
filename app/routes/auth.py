# app/routes/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app
from app.services.user_service import UserService
import logging

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        if not user_id or not password:
            flash('Please enter both user ID and password.', 'error')
            return render_template('auth/login.html')
        
        try:
            # Authenticate user
            user_service = UserService()
            user = user_service.authenticate(user_id, password)
            
            if user:
                session['user_id'] = user.user_id
                session['user_role'] = user.role
                session['user_name'] = user.full_name
                session['user_email'] = user.email
                
                flash(f'Welcome back, {user.full_name}!', 'success')
                
                # Redirect based on role
                if user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user.role == 'lecturer':
                    return redirect(url_for('lecturer.dashboard'))
                else:
                    return redirect(url_for('student.dashboard'))
            else:
                flash('Invalid credentials. Please try again.', 'error')
        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))