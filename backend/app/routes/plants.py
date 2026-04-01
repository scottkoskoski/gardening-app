from flask import Blueprint, request, jsonify
from ..models.database import db
from ..models.plant import Plant, PlantSchema
from .garden_map import COMPANION_DATA

plants_bp = Blueprint("plants", __name__)

# Creating instance of PlantSchema
plant_schema = PlantSchema()
plants_schema = PlantSchema(many=True) # For serializing multiple plants

@plants_bp.route("/get_plants", methods=["GET"])
def get_plants():
    """Fetches plant recommendations based on filters from the database."""
    hardiness_zone = request.args.get("zone") # User's hardiness zone
    greenhouse = request.args.get("greenhouse", "false").lower() == "true" # Convert to boolean
    container_gardening = request.args.get("containers", "false").lower() == "true" # Convert to boolean

    # New filter params
    search = request.args.get("search", "").strip()
    sunlight = request.args.get("sunlight", "").strip()
    water_needs = request.args.get("water_needs", "").strip()
    growing_season = request.args.get("growing_season", "").strip()
    space_required = request.args.get("space_required", "").strip()
    sowing_method = request.args.get("sowing_method", "").strip()

    # Starting with all plants
    query = Plant.query

    # Apply filters
    if hardiness_zone:
        query = query.filter(
            Plant.hardiness_min <= hardiness_zone,
            Plant.hardiness_max >= hardiness_zone,
        )

    if greenhouse:
        query = query.filter(Plant.requires_greenhouse == True)

    if container_gardening:
        query = query.filter(Plant.suitable_for_containers == True)

    if search:
        query = query.filter(Plant.name.ilike(f"%{search}%"))

    if sunlight:
        query = query.filter(Plant.sunlight == sunlight)

    if water_needs:
        query = query.filter(Plant.water_needs == water_needs)

    if growing_season:
        query = query.filter(Plant.growing_season == growing_season)

    if space_required:
        query = query.filter(Plant.space_required == space_required)

    if sowing_method:
        query = query.filter(Plant.sowing_method == sowing_method)

    # Fetch filtered plants
    plants = query.all()

    result = plants_schema.dump(plants)

    # Format data for JSON response
    plants_data = []
    for plant in result:
        plants_data.append({
            "id": plant.get("id"),
            "name": plant.get("name"),
            "description": plant.get("description", "No description available."),
            "hardinessMin": plant.get("hardiness_min", "N/A"),
            "hardinessMax": plant.get("hardiness_max", "N/A"),
            "requiresGreenhouse": plant.get("requires_greenhouse", False),
            "suitableForContainers": plant.get("suitable_for_containers", False),
            "growingSeason": plant.get("growing_season", "N/A"),
            "waterNeeds": plant.get("water_needs", "N/A"),
            "sunlight": plant.get("sunlight", "N/A"),
            "spaceRequired": plant.get("space_required", "N/A"),
            "imageUrl": plant.get("image_url", None),
        })

    return jsonify({"plants": plants_data})

@plants_bp.route("/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    """Retrieves a specific plant by ID."""
    plant = Plant.query.get_or_404(plant_id)
    
    # Using schema to serialize a single plant
    result = plant_schema.dump(plant)
    
    plant_name = result.get("name", "")
    companion_info = COMPANION_DATA.get(plant_name, {})
    companions = {
        "good": companion_info.get("good", []),
        "bad": companion_info.get("bad", []),
        "tips": companion_info.get("tips", "")
    }

    plant_data = {
            "id": result.get("id"),
            "name": result.get("name"),
            "scientificName": result.get("scientific_name", None),
            "description": result.get("description", "No description available."),
            "hardinessMin": result.get("hardiness_min", "N/A"),
            "hardinessMax": result.get("hardiness_max", "N/A"),
            "bestTemperatureMin": result.get("best_temperature_min", None),
            "bestTemperatureMax": result.get("best_temperature_max", None),
            "requiresGreenhouse": result.get("requires_greenhouse", False),
            "suitableForContainers": result.get("suitable_for_containers", False),
            "growingSeason": result.get("growing_season", "N/A"),
            "waterNeeds": result.get("water_needs", "N/A"),
            "sunlight": result.get("sunlight", "N/A"),
            "spaceRequired": result.get("space_required", "N/A"),
            "sowingMethod": result.get("sowing_method", "N/A"),
            "spread": result.get("spread", None),
            "rowSpacing": result.get("row_spacing", None),
            "height": result.get("height", None),
            "imageUrl": result.get("image_url", "N/A"),
            "companions": companions
    }

    return jsonify(plant_data)

@plants_bp.route("", methods=["POST"])
def add_plant():
    """Adds a new plant to the database with schema validation."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    
    # Validating using schema
    errors = plant_schema.validate(json_data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 422
    
    try:
        plant_data = plant_schema.load(json_data)
        new_plant = Plant(**plant_data)
        
        db.session.add(new_plant)
        db.session.commit()
        return jsonify({"message": "Plant added successfully", "id":new_plant.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add plant", "details": str(e)}), 500