"""
Global Configuration for Application

This module is the single source of truth for configuration. Every value
can be overridden with an environment variable of the same name.
"""
import os
import logging

# Redis connection string, e.g. redis://[user]:[password]@host:port/db
DATABASE_URI = os.getenv("DATABASE_URI", "redis://:@localhost:6379/0")
LOGGING_LEVEL = logging.INFO
