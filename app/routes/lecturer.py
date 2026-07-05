# app/routes/lecturer.py
from flask import Blueprint, render_template, session
from app.utils.decorators import lecturer_required

bp = Blueprint('lecturer', __name__)

@bp.route('/dashboard')
@lecturer_required
def dashboard():
    """Lecturer dashboard"""
    return render_template('lecturer/dashboard.html',
                          user_name=session.get('user_name', 'Lecturer'))