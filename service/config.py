"""
Global Configuration for Application
"""
import os

# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "redis://localhost:6379")

# Secret for session management
SECRET_KEY = os.getenv("SECRET_KEY", "s3cr3t-key-shhhh")
