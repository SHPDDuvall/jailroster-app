"""
Flask application entry point with SQLAlchemy database support.
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import timedelta
from .models.roster import db
from .routes.auth import auth_bp
from .routes.roster_db import roster_bp

def create_app():
    """Create and configure the Flask application."""
    
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    app.config['SESSION_COOKIE_SECURE'] = True  # Always use secure cookies in production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Lax for same-domain requests
    app.config['SESSION_COOKIE_NAME'] = 'jail_roster_session'  # Custom session cookie name
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    # Handle Render's postgres:// URL scheme (should be postgresql://)
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Serverless-friendly database connection settings
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,  # Recycle connections after 5 minutes
        'pool_size': 5,  # Smaller pool for serverless
        'max_overflow': 2,
        'connect_args': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 second query timeout
        }
    }
    
    # Initialize database
    db.init_app(app)
    
    # Enable CORS with specific origins
    CORS(app, 
         supports_credentials=True,
         origins=['https://jailroster.shakerpd.com', 'https://jailroster-deploy.vercel.app'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(roster_bp, url_prefix='/api/roster')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Serve the React frontend
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'message': 'Jail Roster API is running'}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Determine the port (Render sets PORT environment variable)
    port = int(os.getenv('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
