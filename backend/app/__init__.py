import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from .models.database import db, create_database
from .models.plant import Plant
from .routes.hardiness import hardiness_bp
from .routes.weather import weather_bp
from .routes.plants import plants_bp
from .routes.users import users_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load SECRET_KEY
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    
    # Database Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__)) # backend/app
    DB_PATH = os.path.join(BASE_DIR, "..","instance", "gardening.db") # backend/instance/gardening.db
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
    
    # Initialize extensions 
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Register Blueprints
    app.register_blueprint(hardiness_bp, url_prefix="/api/hardiness")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")
    app.register_blueprint(plants_bp, url_prefix="/api/plants")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    
    @app.route("/")
    def home():
        return {"message": "Welcome to my Gardening App Backend!"}
    
    return app