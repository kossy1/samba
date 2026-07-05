# app/routes/student.py
from flask import Blueprint, render_template, session
from app.utils.decorators import student_required

bp = Blueprint('student', __name__)

@bp.route('/dashboard')
@student_required
def dashboard():
    """Student dashboard"""
    return render_template('student/dashboard.html',
                          user_name=session.get('user_name', 'Student'))