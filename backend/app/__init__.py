import os
import logging
import time
from flask import Flask, jsonify, request, g
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from .models.database import db, create_database
from .models.plant import Plant
from .models.journal_entry import JournalEntry
from .models.harvest import Harvest
from .config import config_by_name
from .logging_config import setup_logging
from .errors import register_error_handlers

# Load environment variables
load_dotenv()

# Initialize limiter at module level so blueprints can import it
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
)

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    app = Flask(__name__)

    # Determine configuration
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    # Preserve Google OAuth Client ID from env
    app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")

    # Setup structured logging
    setup_logging(app)

    # Initialize JWTManager
    jwt = JWTManager(app)

    # Enable CORS with configurable origins
    CORS(
        app,
        supports_credentials=True,
        origins=app.config.get("CORS_ORIGINS", ["http://localhost:5173"]),
    )

    # Initialize rate limiter
    limiter.init_app(app)

    # Initialize database extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register global error handlers
    register_error_handlers(app)

    # Security headers middleware
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        # Content-Security-Policy - restrictive default
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        # Strict-Transport-Security for HTTPS environments
        if not app.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # Request logging middleware
    @app.before_request
    def log_request_start():
        g.request_start_time = time.time()

    @app.after_request
    def log_request_end(response):
        if hasattr(g, "request_start_time"):
            duration_ms = (time.time() - g.request_start_time) * 1000
            logger.info(
                "method=%s path=%s status=%s duration_ms=%.1f",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
            )
        return response

    # Register Blueprints
    from .routes.hardiness import hardiness_bp
    from .routes.weather import weather_bp
    from .routes.plants import plants_bp
    from .routes.users import users_bp
    from .routes.user_gardens import user_gardens_bp
    from .routes.user_garden_plants import user_garden_plants_bp
    from .routes.garden_types import garden_types_bp
    from .routes.garden_map import garden_map_bp
    from .routes.frost_dates import frost_dates_bp
    from .routes.journal import journal_bp
    from .routes.planting_calendar import planting_calendar_bp
    from .routes.recommendations import recommendations_bp
    from .routes.tasks import tasks_bp
    from .routes.weather_alerts import weather_alerts_bp
    from .routes.harvests import harvests_bp
    from .routes.soil import soil_bp
    from .routes.seasonal_tips import seasonal_tips_bp

    app.register_blueprint(hardiness_bp, url_prefix="/api/hardiness")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")
    app.register_blueprint(plants_bp, url_prefix="/api/plants")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    # Apply stricter rate limits to auth endpoints
    limiter.limit("10/minute")(app.view_functions.get("users.login", lambda: None))
    limiter.limit("10/minute")(app.view_functions.get("users.google_login", lambda: None))
    limiter.limit("5/minute")(app.view_functions.get("users.register_user", lambda: None))
    app.register_blueprint(user_gardens_bp, url_prefix="/api/user_gardens")
    app.register_blueprint(user_garden_plants_bp, url_prefix="/api/user_garden_plants")
    app.register_blueprint(garden_types_bp, url_prefix="/api")
    app.register_blueprint(garden_map_bp, url_prefix="/api/user_gardens")
    app.register_blueprint(frost_dates_bp, url_prefix="/api/frost_dates")
    app.register_blueprint(journal_bp, url_prefix="/api/journal")
    app.register_blueprint(planting_calendar_bp, url_prefix="/api/planting_calendar")
    app.register_blueprint(recommendations_bp, url_prefix="/api/recommendations")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(weather_alerts_bp, url_prefix="/api/weather_alerts")
    app.register_blueprint(harvests_bp, url_prefix="/api/harvests")
    app.register_blueprint(soil_bp, url_prefix="/api/soil")
    app.register_blueprint(seasonal_tips_bp, url_prefix="/api/tips/seasonal")

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    @limiter.exempt
    def health_check():
        health = {"status": "healthy", "checks": {}}
        status_code = 200

        # Database connectivity check
        try:
            db.session.execute(db.text("SELECT 1"))
            health["checks"]["database"] = "ok"
        except Exception as e:
            health["checks"]["database"] = f"error: {str(e)}"
            health["status"] = "unhealthy"
            status_code = 503
            logger.error("Health check - database error: %s", e)

        return jsonify(health), status_code

    @app.route("/")
    def home():
        return {"message": "Welcome to my Gardening App Backend!"}

    logger.info("Application created with %s configuration", config_name)
    return app
