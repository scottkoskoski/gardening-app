from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.database import db
from ..models.user_garden import UserGarden
from ..models.user_garden_plant import UserGardenPlant, GrowthStage
from ..models.plant import Plant

garden_map_bp = Blueprint("garden_map", __name__)

# Companion planting data: plant_name -> {good_companions: [...], bad_companions: [...], tips: str}
COMPANION_DATA = {
    "Tomato": {
        "good": ["Basil", "Carrot", "Parsley", "Marigold", "Lettuce", "Onion"],
        "bad": ["Cabbage", "Fennel", "Potato", "Corn"],
        "tips": "Tomatoes love basil as a companion - it may improve flavor and repel pests."
    },
    "Basil": {
        "good": ["Tomato", "Pepper", "Oregano", "Lettuce"],
        "bad": ["Sage", "Rue"],
        "tips": "Plant near tomatoes and peppers. Basil can repel aphids and mosquitoes."
    },
    "Carrot": {
        "good": ["Tomato", "Lettuce", "Onion", "Pea", "Radish", "Rosemary"],
        "bad": ["Dill", "Celery"],
        "tips": "Carrots grow well with onions - onions repel carrot fly."
    },
    "Lettuce": {
        "good": ["Carrot", "Radish", "Strawberry", "Onion", "Garlic", "Beet"],
        "bad": ["Celery", "Parsley"],
        "tips": "Lettuce benefits from taller plants nearby that provide partial shade."
    },
    "Pepper": {
        "good": ["Basil", "Tomato", "Carrot", "Onion", "Spinach"],
        "bad": ["Fennel", "Bean"],
        "tips": "Peppers and basil are great companions. Basil may improve pepper flavor."
    },
    "Cucumber": {
        "good": ["Bean", "Pea", "Radish", "Sunflower", "Lettuce", "Corn"],
        "bad": ["Potato", "Melon", "Sage"],
        "tips": "Train cucumbers to grow up trellises near corn for natural support."
    },
    "Bean": {
        "good": ["Corn", "Cucumber", "Potato", "Carrot", "Pea", "Squash"],
        "bad": ["Onion", "Garlic", "Pepper", "Fennel"],
        "tips": "Beans fix nitrogen in the soil, benefiting neighboring plants."
    },
    "Corn": {
        "good": ["Bean", "Squash", "Cucumber", "Pea", "Melon"],
        "bad": ["Tomato", "Celery"],
        "tips": "The classic 'Three Sisters' planting: corn, beans, and squash support each other."
    },
    "Potato": {
        "good": ["Bean", "Corn", "Cabbage", "Pea", "Marigold"],
        "bad": ["Tomato", "Cucumber", "Squash", "Sunflower"],
        "tips": "Keep potatoes away from tomatoes - they share diseases."
    },
    "Squash": {
        "good": ["Corn", "Bean", "Radish", "Marigold", "Pea"],
        "bad": ["Potato"],
        "tips": "Large squash leaves shade the ground, suppressing weeds for neighbors."
    },
    "Onion": {
        "good": ["Carrot", "Lettuce", "Tomato", "Pepper", "Beet", "Strawberry"],
        "bad": ["Bean", "Pea"],
        "tips": "Onions repel many pests and pair well with most garden vegetables."
    },
    "Garlic": {
        "good": ["Tomato", "Pepper", "Lettuce", "Beet", "Strawberry", "Rose"],
        "bad": ["Bean", "Pea"],
        "tips": "Garlic is a natural pest deterrent. Plant around roses and vegetables."
    },
    "Pea": {
        "good": ["Carrot", "Corn", "Cucumber", "Bean", "Radish", "Turnip"],
        "bad": ["Onion", "Garlic"],
        "tips": "Peas fix nitrogen in the soil. Follow peas with nitrogen-loving crops."
    },
    "Radish": {
        "good": ["Carrot", "Lettuce", "Pea", "Cucumber", "Spinach"],
        "bad": ["Hyssop"],
        "tips": "Fast-growing radishes mark rows for slow-germinating carrots."
    },
    "Spinach": {
        "good": ["Strawberry", "Pea", "Bean", "Radish", "Pepper"],
        "bad": [],
        "tips": "Spinach grows well in the shade of taller plants during hot months."
    },
}


def _get_companion_info(plant_name, all_placed_names):
    """Get companion planting recommendations for a plant given its garden neighbors."""
    data = COMPANION_DATA.get(plant_name, None)
    good_neighbors = []
    bad_neighbors = []
    tips = []

    if data:
        tips.append(data["tips"])
        for neighbor in all_placed_names:
            if neighbor == plant_name:
                continue
            if neighbor in data["good"]:
                good_neighbors.append(neighbor)
            if neighbor in data["bad"]:
                bad_neighbors.append(neighbor)

    return {
        "good_companions": good_neighbors,
        "bad_companions": bad_neighbors,
        "tips": tips
    }


@garden_map_bp.route("/<int:garden_id>/map", methods=["GET"])
@jwt_required()
def get_garden_map(garden_id):
    """Get garden map data including grid dimensions and all placed plants."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()

    if not garden:
        return jsonify({"error": "Garden not found"}), 404

    placements = []
    for gp in garden.garden_plants:
        placement = {
            "id": gp.id,
            "plant_id": gp.plant_id,
            "plant_name": gp.plant.name,
            "growth_stage": gp.growth_stage.value,
            "row": gp.row,
            "col": gp.col,
            "image_url": gp.plant.image_url,
            "expected_harvest_date": gp.expected_harvest_date.isoformat() if gp.expected_harvest_date else None,
        }
        placements.append(placement)

    return jsonify({
        "garden_id": garden.id,
        "garden_name": garden.garden_name,
        "grid_rows": garden.grid_rows or 8,
        "grid_cols": garden.grid_cols or 10,
        "placements": placements,
    }), 200


@garden_map_bp.route("/<int:garden_id>/map/resize", methods=["PUT"])
@jwt_required()
def resize_garden_grid(garden_id):
    """Update garden grid dimensions."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()

    if not garden:
        return jsonify({"error": "Garden not found"}), 404

    data = request.get_json()
    grid_rows = data.get("grid_rows")
    grid_cols = data.get("grid_cols")

    if not grid_rows or not grid_cols:
        return jsonify({"error": "grid_rows and grid_cols are required"}), 400

    if not (1 <= grid_rows <= 50 and 1 <= grid_cols <= 50):
        return jsonify({"error": "Grid dimensions must be between 1 and 50"}), 400

    garden.grid_rows = grid_rows
    garden.grid_cols = grid_cols

    # Remove any plants that fall outside the new grid
    for gp in garden.garden_plants:
        if gp.row is not None and gp.col is not None:
            if gp.row >= grid_rows or gp.col >= grid_cols:
                gp.row = None
                gp.col = None

    db.session.commit()
    return jsonify({"message": "Grid resized successfully"}), 200


@garden_map_bp.route("/<int:garden_id>/map/place", methods=["POST"])
@jwt_required()
def place_plant_on_map(garden_id):
    """Place a new plant on the garden map at a specific grid position."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()

    if not garden:
        return jsonify({"error": "Garden not found"}), 404

    data = request.get_json()
    plant_id = data.get("plant_id")
    row = data.get("row")
    col = data.get("col")

    if plant_id is None or row is None or col is None:
        return jsonify({"error": "plant_id, row, and col are required"}), 400

    grid_rows = garden.grid_rows or 8
    grid_cols = garden.grid_cols or 10

    if row < 0 or row >= grid_rows or col < 0 or col >= grid_cols:
        return jsonify({"error": "Position is outside the garden grid"}), 400

    plant = Plant.query.get(plant_id)
    if not plant:
        return jsonify({"error": "Plant not found"}), 404

    # Check if cell is already occupied
    existing = UserGardenPlant.query.filter_by(
        garden_id=garden_id, row=row, col=col
    ).first()
    if existing:
        return jsonify({"error": "This cell is already occupied"}), 409

    new_garden_plant = UserGardenPlant(
        garden_id=garden.id,
        plant_id=plant.id,
        growth_stage=GrowthStage[data.get("growth_stage", "SEEDLING").upper()],
        row=row,
        col=col
    )

    db.session.add(new_garden_plant)
    db.session.commit()

    return jsonify({
        "message": "Plant placed successfully",
        "garden_plant_id": new_garden_plant.id,
        "plant_name": plant.name,
        "image_url": plant.image_url,
    }), 201


@garden_map_bp.route("/<int:garden_id>/map/<int:garden_plant_id>", methods=["DELETE"])
@jwt_required()
def remove_plant_from_map(garden_id, garden_plant_id):
    """Remove a plant from the garden map."""
    user_id = int(get_jwt_identity())
    garden_plant = UserGardenPlant.query.get(garden_plant_id)

    if not garden_plant:
        return jsonify({"error": "Plant not found"}), 404

    if garden_plant.garden_id != garden_id:
        return jsonify({"error": "Plant does not belong to this garden"}), 400

    if garden_plant.garden.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(garden_plant)
    db.session.commit()

    return jsonify({"message": "Plant removed from map"}), 200


@garden_map_bp.route("/<int:garden_id>/map/<int:garden_plant_id>/info", methods=["GET"])
@jwt_required()
def get_placed_plant_info(garden_id, garden_plant_id):
    """Get detailed info and recommendations for a plant placed on the map."""
    user_id = int(get_jwt_identity())
    garden_plant = UserGardenPlant.query.get(garden_plant_id)

    if not garden_plant:
        return jsonify({"error": "Plant not found"}), 404

    if garden_plant.garden.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    plant = garden_plant.plant
    garden = garden_plant.garden

    # Get all plant names in this garden for companion analysis
    all_plant_names = [gp.plant.name for gp in garden.garden_plants if gp.id != garden_plant_id]

    companions = _get_companion_info(plant.name, all_plant_names)

    # Build spacing recommendation
    spacing_tips = []
    if plant.spread:
        spacing_tips.append(f"Spread: {plant.spread} cm")
    if plant.row_spacing:
        spacing_tips.append(f"Row spacing: {plant.row_spacing} cm")
    if plant.height:
        spacing_tips.append(f"Height: {plant.height} cm")

    return jsonify({
        "plant": {
            "id": plant.id,
            "name": plant.name,
            "scientific_name": plant.scientific_name,
            "description": plant.description,
            "image_url": plant.image_url,
            "sunlight": plant.sunlight,
            "water_needs": plant.water_needs,
            "growing_season": plant.growing_season,
            "space_required": plant.space_required,
            "sowing_method": plant.sowing_method,
            "spread": plant.spread,
            "row_spacing": plant.row_spacing,
            "height": plant.height,
            "hardiness_min": plant.hardiness_min,
            "hardiness_max": plant.hardiness_max,
        },
        "placement": {
            "id": garden_plant.id,
            "row": garden_plant.row,
            "col": garden_plant.col,
            "growth_stage": garden_plant.growth_stage.value,
            "planted_at": garden_plant.planted_at.isoformat() if garden_plant.planted_at else None,
            "expected_harvest_date": garden_plant.expected_harvest_date.isoformat() if garden_plant.expected_harvest_date else None,
        },
        "companions": companions,
        "spacing": spacing_tips,
    }), 200
