import jwt
import datetime
import requests
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from sqlalchemy import or_
from ..models.database import db
from ..models.user import User
from ..models.profile import UserProfile

users_bp = Blueprint("users", __name__)

@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password."}), 401

    secret_key = current_app.config["SECRET_KEY"]

    token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        },
        secret_key,
        algorithm="HS256",
    )

    return jsonify({"message": "Login successful!", "token": token}), 200


@users_bp.route("/register", methods=["POST"])
def register_user():
    """Registers a new user."""
    data = request.json

    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Please provide username, email, and password."}), 400

    existing_user = User.query.filter(
        or_(User.username == data["username"], User.email == data["email"])
    ).first()

    if existing_user:
        if existing_user.username == data["username"]:
            return jsonify({"error": "User already exists with this username."}), 409
        if existing_user.email == data["email"]:
            return jsonify({"error": "User already exists with this email."}), 409

    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"])  # Hash password before storing

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully.", "user_id": new_user.id}), 201


@users_bp.route("/get_user", methods=["GET"])
@jwt_required()
def get_user():
    """Gets user details for the authenticated user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found."}), 404

    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    ), 200


@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Fetch the authenticated user's profile."""
    user_id = get_jwt_identity()
    print(f"Received GET /users/profile request for user_id: {user_id}")

    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify(
            {
                "first_name": "",
                "last_name": "",
                "zip_code": "",
                "plant_hardiness_zone": "",
            }
        ), 200

    return jsonify(
        {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "zip_code": profile.zip_code,
            "plant_hardiness_zone": profile.plant_hardiness_zone,
        }
    ), 200


@users_bp.route("/profile", methods=["POST"])
@jwt_required()
def update_profile():
    """Create or update the authenticated user's profile."""
    user_id = get_jwt_identity()
    data = request.get_json()

    print("Received profile update request:", data)

    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON payload."}), 422

    # Convert frontend keys to match backend expectations
    formatted_data = {
        "first_name": data.get("first_name") or data.get("firstName", ""),
        "last_name": data.get("last_name") or data.get("lastName", ""),
        "zip_code": data.get("zip_code") or data.get("zipCode", ""),
    }

    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)

    # Update fields
    profile.first_name = formatted_data["first_name"]
    profile.last_name = formatted_data["last_name"]

    # Fetch hardiness zone if zip code is provided and changed
    new_zip = formatted_data["zip_code"]
    if new_zip and new_zip != profile.zip_code:
        try:
            base_url = current_app.config.get("BASE_URL", "http://127.0.0.1:5000")
            hardiness_url = f"{base_url}/api/hardiness/get_hardiness_zone?zip={new_zip}"
            response = requests.get(hardiness_url)

            if response.status_code == 200:
                hardiness_data = response.json()
                profile.plant_hardiness_zone = hardiness_data.get("zone", profile.plant_hardiness_zone)
        except Exception as e:
            print(f"Failed to fetch hardiness zone: {e}")

    profile.zip_code = new_zip

    db.session.commit()
    return jsonify(
        {
            "message": "Profile updated successfully.",
            "plant_hardiness_zone": profile.plant_hardiness_zone,
        }
    )
