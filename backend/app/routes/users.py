import jwt
import datetime
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from sqlalchemy import or_
from ..models.database import db
from ..models.user import User

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
    
    # Get SECRET_KEY from Flask app configuration
    secret_key = current_app.config["SECRET_KEY"]
    
    token = jwt.encode(
        {
            "user_id": user.id,
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
    
    # Validate required fields
    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Please provide username, email, and password."}), 400
    
    # Check if user already exists
    existing_user = User.query.filter(or_(User.username==data["username"], User.email == data["email"])).first()
    if existing_user:
        if existing_user.username == data["username"]:
            return jsonify({"error": "User already exists with this username."}), 409
        if existing_user.email == data["email"]:
            return jsonify({"error": "User already exists with this email."}), 409
    
    # Create new user with hashed password
    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"]) # Hash password before storing
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully.", "user_id": new_user.id}), 201

@users_bp.route("/get_user", methods=["GET"])
def get_user():
    """Gets user details for the authenticated user."""
    
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization token required."}), 401
    
    token = auth_header.split(" ")[1] # Extract token after "Bearer"
    
    try:
        secret_key = current_app.config["SECRET_KEY"]
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = decoded_token["user_id"]
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found."}), 404
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired. Please log in again."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token. Please log in again."}), 401