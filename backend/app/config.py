"""
Application configuration classes for different environments.

Usage:
    Set FLASK_ENV environment variable to 'development', 'testing', or 'production'.
    The config is selected automatically in create_app().
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY")

    # JWT settings
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLAlchemy engine options (connection pooling for non-SQLite)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # CORS - configurable via env var, comma-separated origins
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:5174"
    ).split(",")

    # Rate limiting
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = "200/hour"
    RATELIMIT_HEADERS_ENABLED = True

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    DEBUG = True
    DB_PATH = os.path.join(BASE_DIR, "..", "instance", "gardening.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")


class TestingConfig(BaseConfig):
    """Testing environment configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "DEBUG"
    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production environment configuration."""

    DEBUG = False
    DB_PATH = os.getenv(
        "DATABASE_PATH",
        os.path.join(BASE_DIR, "..", "instance", "gardening.db"),
    )
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI", f"sqlite:///{DB_PATH}"
    )
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")

    # Stricter rate limits in production
    RATELIMIT_DEFAULT = "100/hour"


# Map environment names to config classes
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
