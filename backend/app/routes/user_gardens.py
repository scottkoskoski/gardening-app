from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from ..models.database import db
from ..models.user_garden import UserGarden, UserGardenSchema
from ..models.garden_type import GardenType, GardenTypeEnum
from ..models.profile import UserProfile

user_gardens_bp = Blueprint("user_gardens", __name__)

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
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    
@user_gardens_bp.route("", methods=["GET"])
@jwt_required()
def get_user_gardens():
    """Retrieves all gardens associated with the authenticated user."""
    user_id = get_jwt_identity()
    gardens = UserGarden.query.filter_by(user_id=user_id).all()
    
    # Using schema to serialize the gardens
    result = gardens_schema.dump(gardens)
    
    # Processing comma-separated plants back into lists
    garden_list = []
    for garden in result:
        garden_dict = {
            "id": garden["id"],
            "gardenName": garden["garden_name"],
            "gardenType": garden.get("garden_type_name", None),
            "isCommunityGarden": garden["is_community_garden"],
            "isRooftopGarden": garden["is_rooftop_garden"],
            "gardenSize": garden["garden_size"],
            "gardenDimensions": garden["garden_dimensions"],
            "soilType": garden["soil_type"],
            "waterSource": garden["water_source"],
            "pestProtection": garden["pest_protection"],
            "plantHardinessZone": garden["plant_hardiness_zone"],
            "preferredPlants": garden["preferred_plants"].split(",") if garden.get("preferred_plants") else [],
            "currentPlants": garden["current_plants"].split(",") if garden.get("current_plants") else []
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
    
    # Using schema to serialize the garden
    result = garden_schema.dump(garden)
    
    # Converting to camelCase for frontend and handling plant lists
    garden_data = {
        "id": result["id"],
        "gardenName": result["garden_name"],
        "gardenType": result.get("garden_type_name", None),
        "isCommunityGarden": result["is_community_garden"],
        "isRooftopGarden": result["is_rooftop_garden"],
        "gardenSize": result["garden_size"],
        "gardenDimensions": result["garden_dimensions"],
        "soilType": result["soil_type"],
        "waterSource": result["water_source"],
        "pestProtection": result["pest_protection"],
        "plantHardinessZone": result["plant_hardiness_zone"],
        "preferredPlants": result["preferred_plants"].split(",") if result.get("preferred_plants") else [],
        "currentPlants": result["current_plants"].split(",") if result.get("current_plants") else []
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
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

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
        return jsonify({"error": f"Failed to delete garden: {str(e)}"}), 500
