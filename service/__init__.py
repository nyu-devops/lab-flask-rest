"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and database
"""
from flask import Flask

app = Flask(__name__)

# Import the routes after the Flask app is created
from service import routes, error_handlers
