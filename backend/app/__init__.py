from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .models.database import db, create_database
from .models.plant import Plant
from .routes.hardiness import hardiness_bp
from .routes.weather import weather_bp
from .routes.plants import plants_bp
from .routes.users import users_bp

def create_app():
    app = Flask(__name__)
    
    # Database Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gardening.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    
    # Initialize Migrate
    migrate = Migrate(app, db)
    
    # Create the database if it doesn't exist
    with app.app_context():
        create_database(app)
    
    # Register Blueprints
    app.register_blueprint(hardiness_bp, url_prefix="/api/hardiness")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")
    app.register_blueprint(plants_bp, url_prefix="/api/plants")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    
    @app.route("/")
    def home():
        return {"message": "Welcome to my Gardening App Backend!"}
    
    return app