from flask import Blueprint, request, jsonify
from ..models.database import db
from ..models.plant import Plant

plants_bp = Blueprint("plants", __name__)

@plants_bp.route("/get_plants", methods=["GET"])
def get_plants():
    """Fetches plant recommendations based on filters from the database."""
    hardiness_zone = request.args.get("zone") # User's hardiness zone
    greenhouse = request.args.get("greenhouse", "false").lower() == "true" # Convert to boolean
    container_gardening = request.args.get("containers", "false").lower() == "true" # Convert to boolean
    
    # Starting with all plants
    query = Plant.query
    
    # Apply filters
    if hardiness_zone:
        query = query.filter(
            Plant.hardiness_min <= int(hardiness_zone),
            Plant.hardiness_max >= int(hardiness_zone),
        )
    if greenhouse:
        query = query.filter(Plant.requires_greenhouse == True)
    
    if container_gardening:
        query = query.filter(Plant.suitable_for_containers == True)
    
    # Fetch filtered plants
    plants = query.all()
    
    # Format data for JSON response
    plants_data = [
        {
            "id": plant.id,
            "name": plant.name,
            "description": plant.description if plant.description is not None else "No description available.",
            "hardinessMin": plant.hardiness_min if plant.hardiness_min is not None else "N/A",
            "hardinessMax": plant.hardiness_max if plant.hardiness_max is not None else "N/A",
            "requiresGreenhouse": plant.requires_greenhouse if plant.requires_greenhouse is not None else False,
            "suitableForContainers": plant.suitable_for_containers if plant.suitable_for_containers is not None else False,
            "growingSeason": plant.growing_season if plant.growing_season is not None else "N/A",
            "waterNeeds": plant.water_needs if plant.water_needs is not None else "N/A",
            "sunlight": plant.sunlight if plant.sunlight is not None else "N/A",
            "spaceRequired": plant.space_required if plant.space_required is not None else "N/A",
        }
        for plant in plants
    ]
    return jsonify({"plants": plants_data})