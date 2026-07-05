# app/__init__.py
from flask import Flask
from dotenv import load_dotenv
import os

from app.config import Config, get_config
from app.extensions import kv, session_store, init_extensions
from app.routes import auth, admin, lecturer, student
from app.utils.decorators import register_decorators
from app.utils.error_handlers import register_error_handlers
from app.utils.context_processors import register_context_processors

load_dotenv()

def create_app(config_class=None):
    """Application factory pattern"""
    if config_class is None:
        config_class = get_config()
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(lecturer.bp, url_prefix='/lecturer')
    app.register_blueprint(student.bp, url_prefix='/student')
    
    # Register custom decorators
    register_decorators(app)
    
    # Error handlers
    register_error_handlers(app)
    
    # Context processors
    register_context_processors(app)
    
    return app