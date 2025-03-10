from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.database import db
from ..models.user_garden import UserGarden
from ..models.plant import Plant
from ..models.user_garden_plant import UserGardenPlant, GrowthStage

user_garden_plants_bp = Blueprint("user_garden_plants", __name__)

@user_garden_plants_bp.route("", methods=["POST"])
@jwt_required()
def add_plant_to_garden():
    """Adds a plant to a user's garden."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ["garden_id", "plant_id"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    garden = UserGarden.query.filter_by(id=data["garden_id"], user_id=user_id).first()
    if not garden:
        return jsonify({"error": "Garden not found"}), 404
    
    plant = Plant.query.get(data["plant_id"])
    if not plant:
        return jsonify({"error": "Plant not found"}), 404
    
    new_garden_plant = UserGardenPlant(
        garden_id=garden.id,
        plant_id=plant.id,
        expected_harvest_date=datetime.strptime(data.get("expected_harvest_date"), "%Y-%m-%d").date() if data.get("expected_harvest_date") else None,
        growth_stage=GrowthStage[data.get("growth_stage", "SEEDLING").upper()]
    )
    
    db.session.add(new_garden_plant)
    db.session.commit()
    
    return jsonify({"message": "Plant added successfully", "garden_plant_id": new_garden_plant.id}), 201

@user_garden_plants_bp.route("/<int:garden_id>", methods=["GET"])
@jwt_required()
def get_garden_plants(garden_id):
    """Retrieves all plants in a user's garden."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    
    if not garden:
        return jsonify({"error": "Garden not found"}), 404
    
    plants = [
        {
            "id": gp.id,
            "plant_id": gp.plant_id,
            "plant_name": gp.plant.name,
            "growth_stage": gp.growth_stage.value,
            "expected_harvest_date": gp.expected_harvest_date
        }
        for gp in garden.garden_plants
    ]
    
    return jsonify(plants), 200

@user_garden_plants_bp.route("/<int:garden_plant_id>", methods=["DELETE"])
@jwt_required()
def remove_garden_plant(garden_plant_id):
    """Removes a plant from a user's garden."""
    user_id = int(get_jwt_identity())
    garden_plant = UserGardenPlant.query.get(garden_plant_id)
    
    if not garden_plant:
        return jsonify({"error": "Plant not found"}), 404
    
    if not garden_plant.garden:
        return jsonify({"error": "Garden not found"}), 404
    
    if garden_plant.garden.user_id != user_id:
        return jsonify({"error": f"Unauthorized - expected user {garden_plant.garden.user_id}, but got {user_id}"}), 403
    
    db.session.delete(garden_plant)
    db.session.commit()
    
    return jsonify({"message": "Plant removed successfully"}), 200