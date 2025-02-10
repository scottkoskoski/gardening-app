from flask import Flask
from app.routes.hardiness import hardiness_bp
from app.routes.weather import weather_bp

def create_app():
    app = Flask(__name__)
    
    # Register Blueprints
    app.register_blueprint(hardiness_bp, url_prefix="/api/hardiness")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")
    
    @app.route("/")
    def home():
        return {"message": "Welcome to my Gardening App Backend!"}
    
    return app