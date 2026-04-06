"""
Global error handlers for the Flask application.

Registers handlers for common HTTP errors and unhandled exceptions
to ensure consistent JSON error responses.
"""

import logging
from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers on the Flask app instance."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized", "message": "Authentication is required."}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "Forbidden", "message": "You do not have permission to access this resource."}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "message": "The requested resource was not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed", "message": "The HTTP method is not allowed for this endpoint."}), 405

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({"error": "Conflict", "message": str(error)}), 409

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({"error": "Unprocessable entity", "message": str(error)}), 422

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
        }), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error("Internal server error: %s", error, exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
        }), 500

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        logger.warning("Validation error: %s", error.messages)
        return jsonify({"error": "Validation error", "details": error.messages}), 422

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        from .models.database import db
        db.session.rollback()
        logger.warning("Database integrity error: %s", error)
        return jsonify({
            "error": "Database integrity error",
            "message": "A database constraint was violated. The operation could not be completed.",
        }), 409

    @app.errorhandler(OperationalError)
    def handle_operational_error(error):
        from .models.database import db
        db.session.rollback()
        logger.error("Database operational error: %s", error, exc_info=True)
        return jsonify({
            "error": "Database error",
            "message": "A database error occurred. Please try again later.",
        }), 503
