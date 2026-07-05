# app/utils/context_processors.py
from flask import session

def register_context_processors(app):
    """Register context processors for templates"""
    
    @app.context_processor
    def inject_user():
        return {
            'current_user_id': session.get('user_id'),
            'current_user_role': session.get('user_role'),
            'current_user_name': session.get('user_name'),
            'current_user_email': session.get('user_email'),
            'is_authenticated': 'user_id' in session,
            'app_name': app.config.get('APP_NAME'),
            'institution_name': app.config.get('INSTITUTION_NAME'),
            'app_version': app.config.get('APP_VERSION')
        }
    
    @app.context_processor
    def inject_utility_functions():
        def has_role(role):
            return session.get('user_role') == role
        
        def is_admin():
            return session.get('user_role') == 'admin'
        
        def is_lecturer():
            return session.get('user_role') == 'lecturer'
        
        def is_student():
            return session.get('user_role') == 'student'
        
        return {
            'has_role': has_role,
            'is_admin': is_admin,
            'is_lecturer': is_lecturer,
            'is_student': is_student
        }