# app/routes/admin.py
from flask import Blueprint, render_template, session
from app.utils.decorators import admin_required

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html', 
                          user_name=session.get('user_name', 'Admin'))