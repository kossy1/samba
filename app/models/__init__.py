# app/__init__.py
from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Import extensions
from app.extensions import kv, session_store, init_extensions
from app.config import Config, get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_class=None):
    """
    Application factory pattern
    Creates and configures the Flask application
    """
    if config_class is None:
        config_class = get_config()
    
    # Create Flask app instance
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app.config.from_object(config_class)
    logger.info(f"Loading configuration for: {app.config.get('ENV', 'development')}")
    
    # Set secret key - ensure it's a string
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize extensions (session, redis, etc.)
    init_extensions(app)
    logger.info("Extensions initialized successfully")
    
    # Import and register blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.lecturer import bp as lecturer_bp
    from app.routes.student import bp as student_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(lecturer_bp, url_prefix='/lecturer')
    app.register_blueprint(student_bp, url_prefix='/student')
    logger.info("Blueprints registered successfully")
    
    # Home route - redirect to login
    @app.route('/')
    def home():
        """Redirect root URL to login page"""
        return redirect(url_for('auth.login'))
    
    # Auto-create admin user if it doesn't exist
    with app.app_context():
        try:
            from app.services.user_service import UserService
            user_service = UserService()
            
            # Check if admin exists
            admin = user_service.get_user('admin')
            if not admin:
                # Admin password - change this in production
                admin_password = os.getenv('SEED_ADMIN_PASSWORD', 'Admin@Poly2024!')
                admin_email = os.getenv('SEED_ADMIN_EMAIL', 'admin@polyibadan.edu.ng')
                
                # Create admin user data
                admin_data = {
                    'user_id': 'admin',
                    'email': admin_email,
                    'password': admin_password,
                    'role': 'admin',
                    'first_name': os.getenv('SEED_ADMIN_FIRST_NAME', 'System'),
                    'last_name': os.getenv('SEED_ADMIN_LAST_NAME', 'Administrator'),
                    'is_active': True
                }
                
                # Create the admin user
                result = user_service.create_user(admin_data)
                if result:
                    logger.info(f"✅ Admin user auto-created! (Password: {admin_password})")
                    print(f"✅ Admin user auto-created! (Password: {admin_password})")
                else:
                    logger.warning("⚠️ Failed to auto-create admin user")
            else:
                logger.info("✅ Admin user already exists")
                
        except Exception as e:
            logger.error(f"⚠️ Could not auto-create admin: {e}")
            print(f"⚠️ Could not auto-create admin: {e}")
    
    # Error handlers
    register_error_handlers(app)
    
    # Context processors
    register_context_processors(app)
    
    # Teardown context to handle session cleanup
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Clean up session on teardown"""
        # Flask-Session handles this automatically
        pass
    
    logger.info("✅ Application created successfully")
    return app

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 - Page Not Found"""
        from flask import render_template, request, jsonify
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 - Forbidden"""
        from flask import render_template, request, jsonify
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 - Internal Server Error"""
        from flask import render_template, request, jsonify
        app.logger.error(f"Server error: {error}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 - Unauthorized"""
        from flask import render_template, request, jsonify
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Unauthorized'}), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all other exceptions"""
        app.logger.error(f"Unhandled exception: {error}")
        import traceback
        traceback.print_exc()
        from flask import render_template, request, jsonify
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500

def register_context_processors(app):
    """Register context processors for templates"""
    
    @app.context_processor
    def inject_user():
        """Inject user session data into templates"""
        from flask import session
        return {
            'current_user_id': session.get('user_id'),
            'current_user_role': session.get('user_role'),
            'current_user_name': session.get('user_name'),
            'current_user_email': session.get('user_email'),
            'is_authenticated': 'user_id' in session,
            'app_name': app.config.get('APP_NAME', 'Polytechnic Ibadan Interaction System'),
            'institution_name': app.config.get('INSTITUTION_NAME', 'The Polytechnic, Ibadan'),
            'app_version': app.config.get('APP_VERSION', '1.0.0')
        }
    
    @app.context_processor
    def inject_utility_functions():
        """Inject utility functions into templates"""
        from flask import session
        
        def has_role(role):
            """Check if current user has a specific role"""
            return session.get('user_role') == role
        
        def is_admin():
            """Check if current user is admin"""
            return session.get('user_role') == 'admin'
        
        def is_lecturer():
            """Check if current user is lecturer"""
            return session.get('user_role') == 'lecturer'
        
        def is_student():
            """Check if current user is student"""
            return session.get('user_role') == 'student'
        
        return {
            'has_role': has_role,
            'is_admin': is_admin,
            'is_lecturer': is_lecturer,
            'is_student': is_student
        }