import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from ..models.database import db
from ..models.user_garden import UserGarden, UserGardenSchema
from ..models.garden_type import GardenType, GardenTypeEnum
from ..models.profile import UserProfile

user_gardens_bp = Blueprint("user_gardens", __name__)
logger = logging.getLogger(__name__)

# Schema instances
garden_schema = UserGardenSchema()
gardens_schema = UserGardenSchema(many=True)


@user_gardens_bp.route("", methods=["POST"])
@jwt_required()
def add_garden():
    """Add a new garden for the authenticated user."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    data["user_id"] = user_id
    
    # Validating the data using the schema
    try:
        if "garden_type" in data:
            garden_type = GardenType.query.filter_by(name=data["garden_type"]).first()
            if not garden_type:
                return jsonify({"error": "Invalid garden type"}), 400
            data["garden_type_id"] = garden_type.id
            del data["garden_type"] # Removing string version now that we have the ID
        
        # Fedtching user's plant hardiness zone if not provided
        if "plant_hardiness_zone" not in data or not data["plant_hardiness_zone"]:
            user_profile = UserProfile.query.filter_by(user_id=user_id).first()
            if user_profile and user_profile.plant_hardiness_zone:
                data["plant_hardiness_zone"] = user_profile.plant_hardiness_zone
        
        # Processing plant lists into commar-separated strings
        if "preferred_plants" in data and isinstance(data["preferred_plants"], list):
            data["preferred_plants"] = ",".join(data["preferred_plants"])
        
        if "current_plants" in data and isinstance(data["current_plants"], list):
            data["current_plants"] = ",".join(data["current_plants"])
        
        # Validating with schema
        errors = garden_schema.validate(data)
        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 422
        
        # Loading data into a dict thorugh the schema
        garden_data = garden_schema.load(data)
        
        # Creating new garden object
        new_garden = UserGarden(**garden_data)
        
        db.session.add(new_garden)
        db.session.commit()
        
        return jsonify({
            "message": "Garden added successfully",
            "garden_id": new_garden.id
        }), 201
    
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 422
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to add garden. Possible duplicate or missing required field(s)."}), 500
    except Exception as e:
        db.session.rollback()
        logger.error("Error adding garden for user_id=%s: %s", user_id, e, exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500

@user_gardens_bp.route("", methods=["GET"])
@jwt_required()
def get_user_gardens():
    """Retrieves all gardens associated with the authenticated user."""
    user_id = get_jwt_identity()
    gardens = UserGarden.query.filter_by(user_id=user_id).all()
    
    garden_list = []
    for garden in gardens:
        # Serialize garden plants
        garden_plants = []
        for gp in garden.garden_plants:
            garden_plants.append({
                "id": gp.id,
                "plant_id": gp.plant_id,
                "plant_name": gp.plant.name,
                "growth_stage": gp.growth_stage.value,
                "expected_harvest_date": gp.expected_harvest_date.isoformat() if gp.expected_harvest_date else None,
                "row": gp.row,
                "col": gp.col
            })

        garden_dict = {
            "id": garden.id,
            "garden_name": garden.garden_name,
            "garden_type": garden.garden_type.name.value if garden.garden_type else None,
            "is_community_garden": garden.is_community_garden,
            "is_rooftop_garden": garden.is_rooftop_garden,
            "garden_size": garden.garden_size,
            "garden_dimensions": garden.garden_dimensions,
            "soil_type": garden.soil_type,
            "water_source": garden.water_source,
            "pest_protection": garden.pest_protection,
            "plant_hardiness_zone": garden.plant_hardiness_zone,
            "preferred_plants": garden.preferred_plants.split(",") if garden.preferred_plants else [],
            "current_plants": garden.current_plants.split(",") if garden.current_plants else [],
            "grid_rows": garden.grid_rows or 8,
            "grid_cols": garden.grid_cols or 10,
            "garden_plants": garden_plants
        }
        garden_list.append(garden_dict)

    return jsonify(garden_list), 200
    

@user_gardens_bp.route("/<int:garden_id>", methods=["GET"])
@jwt_required()
def get_garden_by_id(garden_id):
    """Retrieves a specific garden by its ID."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    
    if not garden:
        return jsonify({"error": "Garden not found"}), 404
    
    # Serialize garden plants
    garden_plants = []
    for gp in garden.garden_plants:
        garden_plants.append({
            "id": gp.id,
            "plant_id": gp.plant_id,
            "plant_name": gp.plant.name,
            "growth_stage": gp.growth_stage.value,
            "expected_harvest_date": gp.expected_harvest_date.isoformat() if gp.expected_harvest_date else None
        })

    garden_data = {
        "id": garden.id,
        "garden_name": garden.garden_name,
        "garden_type": garden.garden_type.name.value if garden.garden_type else None,
        "is_community_garden": garden.is_community_garden,
        "is_rooftop_garden": garden.is_rooftop_garden,
        "garden_size": garden.garden_size,
        "garden_dimensions": garden.garden_dimensions,
        "soil_type": garden.soil_type,
        "water_source": garden.water_source,
        "pest_protection": garden.pest_protection,
        "plant_hardiness_zone": garden.plant_hardiness_zone,
        "preferred_plants": garden.preferred_plants.split(",") if garden.preferred_plants else [],
        "current_plants": garden.current_plants.split(",") if garden.current_plants else [],
        "garden_plants": garden_plants
    }

    return jsonify(garden_data), 200
    

@user_gardens_bp.route("/<int:garden_id>", methods=["PUT"])
@jwt_required()
def update_garden(garden_id):
    """Updates a garden for the authenticated user."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    
    if not garden:
        return jsonify({"error": "Garden not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    try:
        # Processing garden_type string to enum/ID if provided
        if "garden_type" in data:
            garden_type = GardenType.query.filter_by(name=data["garden_type"]).first()
            if not garden_type:
                return jsonify({"error": "Invalid garden type"}), 400
            data["garden_type_id"] = garden_type.id
            del data["garden_type"] # Removing the string version
        
        # Processing plant lists into comma-separated strings
        if "preferred_plants" in data and isinstance(data["preferred_plants"], list):
            data["preferred_plants"] = ",".join(data["preferred_plants"])
        
        if "current_plants" in data and isinstance(data["current_plants"], list):
            data["current_plants"] = ",".join(data["current_plants"])
        
        # Adding the user_8id and garden_id to ensure ownership validation
        data["user_id"] = user_id
        data["id"] = garden_id
        
        # Validating the fields that are being updated
        errors = garden_schema.validate(data, partial=True)
        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 422
        
        # Updating the garden object with validated data
        for key, value in data.items():
            if hasattr(garden, key):
                setattr(garden, key, value)
        
        db.session.commit()
        return jsonify({"message": "Garden updated successfully"}), 200
    
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 422
    except Exception as e:
        db.session.rollback()
        logger.error("Error updating garden_id=%s: %s", garden_id, e, exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500

@user_gardens_bp.route("/<int:garden_id>", methods=["DELETE"])
@jwt_required()
def delete_garden(garden_id):
    """Deletes a garden for the authenticated user."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    
    if not garden:
        return jsonify({"error": "Garden not found"}), 404
    
    try:
        db.session.delete(garden)
        db.session.commit()
        return jsonify({"message": "Garden deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error("Error deleting garden_id=%s: %s", garden_id, e, exc_info=True)
        return jsonify({"error": "Failed to delete garden."}), 500
