from flask import Blueprint, request, jsonify
from ..models.database import db
from ..models.user import User

users_bp = Blueprint("users", __name__)

@users_bp.route("/register", methods=["POST"])
def register_user():
    """Registers a new user."""
    data = request.json
    
    # Validate required fields
    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Please provide username, email, and password."}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "User already exists with this email."}), 409
    
    # Create new user with hashed password
    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"]) # Hash password before storing
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully.", "user_id": new_user.id}), 201

@users_bp.route("/get_user", methods=["GET"])
def get_user():
    """Gets user details by email (excluding password hash)."""
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email is required."}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })