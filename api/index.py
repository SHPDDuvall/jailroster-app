"""
Vercel serverless function entry point for Flask application.
"""

from main import create_app

# Create the Flask app
app = create_app()

# Export the app for Vercel
# Vercel expects the WSGI app to be available
handler = app
