"""
Structured logging configuration for the application.

Provides a consistent logging setup with JSON-style structured output
for production and human-readable output for development.
"""

import logging
import sys
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured log lines suitable for log aggregation."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        return str(log_data)


def setup_logging(app):
    """Configure application logging based on the app config.

    In development: human-readable format to stderr.
    In production: structured format to stderr for log aggregation.
    """
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

    # Remove default Flask handlers to avoid duplicate output
    app.logger.handlers.clear()

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)

    if app.debug:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = StructuredFormatter()

    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)

    # Also configure the root logger for library output
    root = logging.getLogger()
    root.setLevel(log_level)
    if not root.handlers:
        root.addHandler(handler)

    # Quiet noisy libraries
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    app.logger.info("Logging configured at %s level", logging.getLevelName(log_level))
