# app/utils/error_handlers.py
from flask import render_template, jsonify, request

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found(error):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def server_error(error):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Unauthorized'}), 401
        return render_template('errors/401.html'), 401