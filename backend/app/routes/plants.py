from flask import Blueprint, request, jsonify

plants_bp = Blueprint("plants", __name__)

# Sample mock data (Replace with real API calls later)
sample_plants = [
    {
        "id": 1,
        "name": "Tomato",
        "hardiness_min": "3",
        "hardiness_max": "10",
        "requires_greenhouse": False,
        "suitable_for_containers": True,
        "growing_season": "Spring, Summer",
        "water_needs": "Medium",
        "sunlight": "Full sun",
        "space_required": "Medium",
    },
    {
        "id": 2,
        "name": "Lettuce",
        "hardiness_min": "2",
        "hardiness_max": "11",
        "requires_greenhouse": False,
        "suitable_for_containers": True,
        "growing_season": "Spring, Fall",
        "water_needs": "Medium",
        "sunlight": "Partial shade",
        "space_required": "Small",
    },
    {
        "id": 3,
        "name": "Pepper",
        "hardiness_min": "4",
        "hardiness_max": "10",
        "requires_greenhouse": False,
        "suitable_for_containers": True,
        "growing_season": "Summer",
        "water_needs": "High",
        "sunlight": "Full sun",
        "space_required": "Medium",
    },
]

@plants_bp.route("/get_plants", methods=["GET"])
def get_plants():
    """Fetches plan recommendations based on filters."""
    hardiness_zone = request.args.get("zone") # User's hardiness zone
    greenhouse = request.args.get("greenhouse", "false").lower() == "true" # Convert to boolean
    container_gardening = request.args.get("containers", "false").lower() == "true" # Convert to boolean
    
    # Filter data based on user input
    filtered_plants = [
        plant for plant in sample_plants
        if (not hardiness_zone or (plant["hardiness_min"] <= hardiness_zone <= plant["hardiness_max"]))
        and (not greenhouse or plant["requires_greenhouse"])
        and (not container_gardening or plant["suitable_for_containers"])
    ]
    
    return jsonify({"plants": filtered_plants})