from flask import Blueprint, request, jsonify
from ..models.database import db
from ..models.plant import Plant, PlantSchema

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
        })
        
    return jsonify({"plants": plants_data})

@plants_bp.route("/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    """Retrieves a specific plant by ID."""
    plant = Plant.query.get_or_404(plant_id)
    
    # Using schema to serialize a single plant
    result = plant_schema.dump(plant)
    
    plant_data = {
            "id": result.get("id"),
            "name": result.get("name"),
            "description": result.get("description", "No description available."),
            "hardinessMin": result.get("hardiness_min", "N/A"),
            "hardinessMax": result.get("hardiness_max", "N/A"),
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
            "imageUrl": result.get("image_url", "N/A")
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