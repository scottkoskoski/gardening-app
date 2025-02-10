from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Defining the database filename
DB_NAME = "gardening.db"

# Initializing SQLAlchemy
db = SQLAlchemy()

def create_database(app: Flask):
    """Creates the database file if it doesn't exist."""
    if not os.path.exists(f"instance/{DB_NAME}"):
        with app.app_context():
            db.create_all()
        print("Database created.")