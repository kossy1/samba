# app.py
from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Run the application
    app.run(
        debug=True,           # Enable debug mode for development
        port=5000,            # Port to run on
        host='0.0.0.0'        # Listen on all interfaces
    )