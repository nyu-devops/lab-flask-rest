"""
Global Configuration for Application
"""
import os
import logging

# Get configuration from environment
DATABASE_URI = os.getenv("DATABASE_URI", "redis://:@localhost:6379/0")
LOGGING_LEVEL = logging.INFO
