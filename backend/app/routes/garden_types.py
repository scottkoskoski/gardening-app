from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ..models.garden_type import GardenType, GardenTypeSchema

garden_types_bp = Blueprint("garden_types", __name__)

# Schema instances
garden_type_schema = GardenTypeSchema()
garden_types_schema = GardenTypeSchema(many=True)


@garden_types_bp.route("/garden_types", methods=["GET"])
def get_garden_types():
    """Retrieves all available gardedn types."""
    try:
        garden_types = GardenType.query.all()
        
        # Using schema to serialize the garden types
        result = garden_types_schema.dump(garden_types)
        
        # Converting to frontend-friendly format
        garden_types_list = []
        for garden_type in result:
            garden_type_dict = {
                "id": garden_type["id"],
                "name": garden_type["name"],
                "description": garden_type.get("description", ""),
                "idealSoilType": garden_type.get("ideal_soil_type", ""),
                "spaceRequirements": garden_type.get("space_requirements", ""),
                "maintenanceLevel": garden_type.get("maintenance_level", "")
            }
            garden_types_list.append(garden_type_dict)
        
        return jsonify(garden_types_list), 200
    
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@garden_types_bp.route("/garden_types/<int:garden_type_id>", methods=["GET"])
def get_garden_type(garden_type_id):
    """Retrieves a specific garden type by its ID."""
    try:
        garden_type = GardenType.query.get(garden_type_id)
        
        if not garden_type:
            return jsonify({"error": "Garden type not found"}), 404
        
        # Using schema to serialize the garden type
        result = garden_type_schema.dump(garden_type)
        
        garden_type_data = {
            "id": result["id"],
            "name": result["name"],
            "description": result.get("description", ""),
            "idealSoilType": result.get("ideal_soil_type", ""),
            "spaceRequirements": result.get("space_requirements", ""),
            "maintenanceLevel": result.get("maintenance_level", "")
        }
        
        return jsonify(garden_type_data), 200
    
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    