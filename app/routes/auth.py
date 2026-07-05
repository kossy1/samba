from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from app.services.user_service import UserService
from app.utils.decorators import login_required
from app.utils.validators import validate_login

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        # Validate input
        if not validate_login(user_id, password):
            flash('Invalid credentials format', 'error')
            return render_template('auth/login.html')
        
        # Authenticate user
        user_service = UserService()
        user = user_service.authenticate(user_id, password)
        
        if user:
            session['user_id'] = user.user_id
            session['user_role'] = user.role
            session['user_name'] = user.full_name
            session['user_email'] = user.email
            
            # Update last login
            user_service.update_last_login(user.user_id)
            
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
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration (for students and lecturers)"""
    if request.method == 'POST':
        # Registration logic
        pass
    return render_template('auth/register.html')