"""
Vercel serverless function wrapper for Flask app
"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set environment variable to indicate we're running on Vercel
os.environ['VERCEL'] = '1'

# Import the Flask app
from app import app

# Export the app for Vercel (WSGI application)
# Vercel will automatically detect the 'app' variable

