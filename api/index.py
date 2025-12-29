"""
Vercel serverless function entry point for Flask application.
"""

from .main import create_app

# Create and export the Flask app
app = create_app()
