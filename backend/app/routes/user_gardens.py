from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from ..models.database import db
from ..models.user_garden import UserGarden
from ..models.garden_type import GardenType
from ..models.profile import UserProfile

user_gardens_bp = Blueprint("user_gardens", __name__)

@user_gardens_bp.route("/user_gardens", methods=["POST"])
@jwt_required()
def add_garden():
    """Add a new garden for the authenticated user."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ["garden_name", "garden_type"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Look up garden type ID based on the name
    garden_type = GardenType.query.filter_by(name=data["garden_type"]).first()
    if not garden_type:
        return jsonify({"error":"Invalid garden type"}), 400
    
    # Fetch user's plant hardiness zone
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    plant_hardiness_zone = user_profile.plant_hardiness_zone if user_profile else None
    
    new_garden = UserGarden(
        user_id=user_id,
        garden_name=data["garden_name"],
        garden_type_id=garden_type.id,
        is_community_garden=data.get("is_community_garden", False),
        is_rooftop_garden=data.get("is_rooftop_garden", False),
        garden_size=data.get("garden_size"),
        garden_dimensions=data.get("garden_dimensions"),
        soil_type=data.get("soil_type"),
        water_source=data.get("water_source"),
        pest_protection=data.get("pest_protection", False),
        plant_hardiness_zone=plant_hardiness_zone,
        preferred_plants=data.get("preferred_plants"),
        current_plants=data.get("current_plants"),
    )
    
    try:
        db.session.add(new_garden)
        db.session.commit()
        return jsonify({"message": "Garden added successfully", "garden_id": new_garden.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to add garden"}), 500

@user_gardens_bp.route("/user_gardens", methods=["GET"])
@jwt_required()
def get_user_gardens():
    """Retrieves all gardens associated with the authenticated user."""
    user_id = get_jwt_identity()
    gardens = UserGarden.query.filter_by(user_id=user_id).all()
    
    garden_list = [
        {
            "id": g.id,
            "garden_name": g.garden_name,
            "garden_type": g.garden_type.name,
            "is_community_garden": g.is_community_garden,
            "is_rooftop_garden": g.is_rooftop_garden,
            "garden_size": g.garden_size,
            "garden_dimensions": g.garden_dimensions,
            "soil_type": g.soil_type,
            "water_source": g.water_source,
            "pest_protection": g.pest_protection,
            "plant_hardiness_zone": g.plant_hardiness_zone,
            "preferred_plants": g.preferred_plants,
            "current_plants": g.current_plants
        }
        for g in gardens
    ]
    
    return jsonify(garden_list), 200

@user_gardens_bp.route("/user_gardens/<int:garden_id>", methods=["GET"])
@jwt_required()
def get_garden_by_id(garden_id):
    """Retrieves a specific garden by its ID."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    
    if not garden:
        return jsonify({"error": "Garden not found"}), 404
    
    return jsonify(
        {
            "id": garden.id,
            "garden_name": garden.garden_name,
            "garden_type": garden.garden_type.name,
            "is_community_garden": garden.is_community_garden,
            "is_rooftop_garden": garden.is_rooftop_garden,
            "garden_size": garden.garden_size,
            "garden_dimensions": garden.garden_dimensions,
            "soil_type": garden.soil_type,
            "water_source": garden.water_source,
            "pest_protection": garden.pest_protection,
            "plant_hardiness_zone": garden.plant_hardiness_zone,
            "preferred_plants": garden.preferred_plants,
            "current_plants": garden.current_plants,
        }
    ), 200

@user_gardens_bp.route("/user_gardens/<int:garden_id>", methods=["PUT"])
@jwt_required()
def update_garden(garden_id):
    """Updates a garden for the authenticated user."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    
    if not garden:
        return jsonify({"error": "Garden not found"}), 404
    
    data = request.get_json()
    
    if "garden_type" in data:
        # If the user is updating garden type, find the corresponding ID
        garden_type = GardenType.query.filter_by(name=data["garden_type"]).first()
        if not garden_type:
            return jsonify({"error": "Invalid garden type"}), 400
        garden.garden_type_id = garden_type.id
    
    garden.garden_name = data.get("garden_name", garden.garden_name)
    garden.is_community_garden = data.get("is_community_garden", garden.is_community_garden)
    garden.is_rooftop_garden = data.get("is_rooftop_garden", garden.is_rooftop_garden)
    garden.garden_size = data.get("garden_size", garden.garden_size)
    garden.garden_dimensions = data.get("garden_dimensions", garden.garden_dimensions)
    garden.soil_type = data.get("soil_type", garden.soil_type)
    garden.water_source = data.get("water_source", garden.water_source)
    garden.pest_protection = data.get("pest_protection", garden.pest_protection)
    garden.garden_dimensions = data.get("garden_dimensions", garden.garden_dimensions)
    garden.preferred_plants = data.get("preferred_plants", garden.preferred_plants)
    garden.current_plants = data.get("current_plants", garden.current_plants)
    
    db.session.commit()
    
    return jsonify({"message": "Garden updated successfully"}), 200

@user_gardens_bp.route("/user_gardens/<int:garden_id>", methods=["DELETE"])
@jwt_required()
def delete_garden(garden_id):
    """Deletes a garden for the authenticated user."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    
    if not garden:
        return jsonify({"error": "Garden not found"}), 404
    
    db.session.delete(garden)
    db.session.commit()
    
    return jsonify({"message": "Garden deleted successfully"}), 200