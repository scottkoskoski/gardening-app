import jwt
import logging
import re
import requests
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from sqlalchemy import or_
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from ..models.database import db
from ..models.user import User, UserSchema
from ..models.profile import UserProfile

users_bp = Blueprint("users", __name__)
logger = logging.getLogger(__name__)

# Input validation constants
MAX_USERNAME_LENGTH = 100
MAX_EMAIL_LENGTH = 120
MAX_PASSWORD_LENGTH = 256
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def admin_required():
    """
    Custom decorator that checks if the current user has admin privileges.
    This combines JWT verification with admin role checking.

    Usage:
        @users_bp.route("/admin_only", methods=["GET"])
        @admin_required()
        def admin_only_route():
            # This function will only execute if the user is an admin
            return jsonify({"messge": "Welcome, admin!"})
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required() # First ensures the user is authenticated
        def decorator(*args, **kwargs):
            # Getting the authenticated user ID from the JWT
            user_id = get_jwt_identity()

            # Finding the user in the database
            user = User.query.get(user_id)

            # Checking if the user exists and has admin privileges
            if not user or not user.is_admin:
                return jsonify({"error": "Admin privileges required"}), 403

            # If the user is an admin, proceed with the original function
            return fn(*args, **kwargs)
        return decorator
    return wrapper


@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    # Input length validation
    if len(username) > MAX_USERNAME_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        return jsonify({"error": "Invalid username or password."}), 401

    user = User.query.filter_by(username=username).first()

    if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
        logger.info("Failed login attempt for username=%s", username)
        return jsonify({"error": "Invalid username or password."}), 401

    # Recording the login timestamp
    user.record_login()

    secret_key = current_app.config["SECRET_KEY"]

    token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        },
        secret_key,
        algorithm="HS256",
    )

    logger.info("Successful login for user_id=%s", user.id)
    return jsonify({"message": "Login successful!", "token": token}), 200


@users_bp.route("/google-login", methods=["POST"])
def google_login():
    """Authenticate a user via Google OAuth credential."""
    data = request.get_json()
    credential = data.get("credential")

    if not credential:
        return jsonify({"error": "Google credential is required."}), 400

    google_client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    if not google_client_id:
        return jsonify({"error": "Google OAuth is not configured on the server."}), 500

    try:
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            google_client_id
        )

        google_id = idinfo["sub"]
        email = idinfo.get("email")
        name = idinfo.get("name", "")

        if not email:
            return jsonify({"error": "Google account must have an email address."}), 400

        # Check if user exists by google_id first, then by email
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                # Link existing account to Google
                user.google_id = google_id
                if user.auth_provider == "local":
                    user.auth_provider = "local"  # Keep local if they had a password
            else:
                # Create a new user from Google info
                # Generate a unique username from the email prefix
                base_username = email.split("@")[0]
                username = base_username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User(
                    username=username,
                    email=email,
                    google_id=google_id,
                    auth_provider="google"
                )
                db.session.add(user)

        # Record login
        user.record_login()
        db.session.commit()

        # Generate JWT
        secret_key = current_app.config["SECRET_KEY"]
        token = jwt.encode(
            {
                "sub": str(user.id),
                "exp": datetime.now(timezone.utc) + timedelta(hours=24)
            },
            secret_key,
            algorithm="HS256",
        )

        logger.info("Successful Google login for user_id=%s", user.id)
        return jsonify({"message": "Login successful!", "token": token}), 200

    except ValueError as e:
        return jsonify({"error": "Invalid Google credential."}), 401
    except Exception as e:
        logger.error("Google login error: %s", e, exc_info=True)
        return jsonify({"error": "An error occurred during Google authentication."}), 500


@users_bp.route("/register", methods=["POST"])
def register_user():
    """Registers a new user."""
    data = request.json

    if not data:
        return jsonify({"error": "Request body is required."}), 400

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"error": "Please provide username, email, and password."}), 400

    # Input length validation
    if len(username) > MAX_USERNAME_LENGTH:
        return jsonify({"error": "Username must be 100 characters or less."}), 400
    if len(email) > MAX_EMAIL_LENGTH:
        return jsonify({"error": "Email must be 120 characters or less."}), 400
    if len(password) > MAX_PASSWORD_LENGTH:
        return jsonify({"error": "Password is too long."}), 400

    # Email format validation
    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Please provide a valid email address."}), 400

    existing_user = User.query.filter(
        or_(User.username == username, User.email == email)
    ).first()

    if existing_user:
        if existing_user.username == username:
            return jsonify({"error": "User already exists with this username."}), 409
        if existing_user.email == email:
            return jsonify({"error": "User already exists with this email."}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)  # Hash password before storing

    db.session.add(new_user)
    db.session.commit()

    logger.info("New user registered: user_id=%s username=%s", new_user.id, new_user.username)
    return jsonify({"message": "User registered successfully.", "user_id": new_user.id}), 201


@users_bp.route("/get_user", methods=["GET"])
@jwt_required()
def get_user():
    """Gets user details for the authenticated user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found."}), 404

    # Using UserSchema to properly serialize the user data
    user_schema = UserSchema()
    serialized_user = user_schema.dump(user)

    return jsonify(serialized_user), 200


@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Fetch the authenticated user's profile."""
    try:
        user_id = get_jwt_identity()
        logger.debug("Fetching profile for user_id=%s", user_id)

        profile = UserProfile.query.filter_by(user_id=user_id).first()

        if not profile:
            return jsonify({
                "zip_code": "",
                "plant_hardiness_zone": "",
                "city": "",
                "state": "",
                "has_irrigation": False,
                "sunlight_hours": None,
                "soil_ph": None
            }), 200

        return jsonify({
            "zip_code": profile.zip_code,
            "plant_hardiness_zone": profile.plant_hardiness_zone,
            "city": profile.city,
            "state": profile.state,
            "has_irrigation": profile.has_irrigation,
            "sunlight_hours": profile.sunlight_hours,
            "soil_ph": profile.soil_ph
        }), 200
    except Exception as e:
        logger.error("Error in get_profile for user_id=%s: %s", get_jwt_identity(), e, exc_info=True)
        return jsonify({"error": "An unexpected error occurred fetching profile"}), 500


@users_bp.route("/profile", methods=["POST"])
@jwt_required()
def update_profile():
    """Create or update the authenticated user's profile."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        logger.debug("Profile update request for user_id=%s", user_id)

        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload."}), 422

        # Convert frontend keys to match backend expectations
        formatted_data = {
            "zip_code": data.get("zip_code", ""),
            "city": data.get("city", ""),
            "state": data.get("state", ""),
            "has_irrigation": data.get("has_irrigation", False),
            "sunlight_hours": data.get("sunlight_hours"),
            "soil_ph": data.get("soil_ph")
        }

        # Validate zip code format if provided
        zip_code = formatted_data["zip_code"]
        if zip_code and not re.match(r"^\d{5}(-\d{4})?$", zip_code):
            return jsonify({"error": "Invalid zip code format. Use 12345 or 12345-6789."}), 400

        # Validate soil_ph range if provided
        soil_ph = formatted_data["soil_ph"]
        if soil_ph is not None:
            try:
                soil_ph = float(soil_ph)
                if not (0 <= soil_ph <= 14):
                    return jsonify({"error": "Soil pH must be between 0 and 14."}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Soil pH must be a number."}), 400

        # Validate sunlight_hours range if provided
        sunlight_hours = formatted_data["sunlight_hours"]
        if sunlight_hours is not None:
            try:
                sunlight_hours = float(sunlight_hours)
                if not (0 <= sunlight_hours <= 24):
                    return jsonify({"error": "Sunlight hours must be between 0 and 24."}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Sunlight hours must be a number."}), 400

        profile = UserProfile.query.filter_by(user_id=user_id).first()

        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)

        # Update fields
        profile.zip_code = formatted_data["zip_code"]
        profile.city = formatted_data["city"]
        profile.state = formatted_data["state"]
        profile.has_irrigation = formatted_data["has_irrigation"]
        profile.sunlight_hours = formatted_data["sunlight_hours"]
        profile.soil_ph = formatted_data["soil_ph"]

        # Fetch hardiness zone if zip code is provided and changed
        new_zip = formatted_data["zip_code"]
        if new_zip and new_zip != profile.zip_code:
            try:
                base_url = current_app.config.get("BASE_URL", "http://127.0.0.1:5000")
                hardiness_url = f"{base_url}/api/hardiness/get_hardiness_zone?zip={new_zip}"
                response = requests.get(hardiness_url, timeout=10)

                if response.status_code == 200:
                    hardiness_data = response.json()
                    profile.plant_hardiness_zone = hardiness_data.get("zone", profile.plant_hardiness_zone)
            except Exception as e:
                logger.warning("Failed to fetch hardiness zone for zip=%s: %s", new_zip, e)

        db.session.commit()
        logger.info("Profile updated for user_id=%s", user_id)
        return jsonify(
            {
                "message": "Profile updated successfully.",
                "plant_hardiness_zone": profile.plant_hardiness_zone,
            }
        )
    except Exception as e:
        db.session.rollback()
        logger.error("Error in update_profile for user_id=%s: %s", get_jwt_identity(), e, exc_info=True)
        return jsonify({"error": "An unexpected error occurred updating profile"}), 500



@users_bp.route("/inactive_users", methods=["GET"])
@admin_required()
def get_inactive_users():
    """Gets users who haven't logged in for over 30 days."""

    # Calculating the date 30 days ago
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    # Finding users who haven't logged in for 30 days
    inactive_users = User.query.filter(
        or_(User.last_login_at < thirty_days_ago, User.last_login_at == None)
    ).all()

    # Serializing the users with schema
    users_schema = UserSchema(many=True)
    result = users_schema.dump(inactive_users)

    return jsonify(result), 200
