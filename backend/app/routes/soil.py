import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.database import db
from ..models.profile import UserProfile
from ..models.user_garden import UserGarden
from ..models.user_garden_plant import UserGardenPlant

soil_bp = Blueprint("soil", __name__)
logger = logging.getLogger(__name__)

PLANT_PH_PREFERENCES = {
    "Artichoke": {"min": 6.5, "max": 7.5, "ideal": 6.8},
    "Arugula": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Asparagus": {"min": 6.5, "max": 7.5, "ideal": 7.0},
    "Avocado": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Basil": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Bay Laurel": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Bean": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Beet": {"min": 6.0, "max": 7.5, "ideal": 6.8},
    "Bell Pepper": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Blackberry": {"min": 5.5, "max": 6.5, "ideal": 6.0},
    "Blueberry": {"min": 4.5, "max": 5.5, "ideal": 5.0},
    "Bok Choy": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Borage": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Broccoli": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Brussels Sprouts": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Butternut Squash": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Cabbage": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Calendula": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Cantaloupe": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Carrot": {"min": 6.0, "max": 6.8, "ideal": 6.3},
    "Cauliflower": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Celery": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Celery Root": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Chamomile": {"min": 5.6, "max": 7.5, "ideal": 6.5},
    "Cherry Tomato": {"min": 6.0, "max": 6.8, "ideal": 6.5},
    "Chives": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Cilantro": {"min": 6.2, "max": 6.8, "ideal": 6.5},
    "Collard Greens": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Corn": {"min": 5.8, "max": 7.0, "ideal": 6.5},
    "Cucumber": {"min": 5.5, "max": 7.0, "ideal": 6.0},
    "Dill": {"min": 5.5, "max": 6.5, "ideal": 6.0},
    "Eggplant": {"min": 5.5, "max": 6.8, "ideal": 6.0},
    "Endive": {"min": 5.8, "max": 7.0, "ideal": 6.5},
    "Fennel": {"min": 5.5, "max": 7.0, "ideal": 6.5},
    "Fig": {"min": 6.0, "max": 6.5, "ideal": 6.2},
    "Garlic": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Ginger": {"min": 5.5, "max": 6.5, "ideal": 6.0},
    "Grape": {"min": 5.5, "max": 6.5, "ideal": 6.0},
    "Green Bean": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Green Onion": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Ground Cherry": {"min": 6.0, "max": 6.8, "ideal": 6.5},
    "Horseradish": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Hot Pepper": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Jalapeno Pepper": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Kale": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Kohlrabi": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Lavender": {"min": 6.5, "max": 7.5, "ideal": 7.0},
    "Leek": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Lemon": {"min": 5.5, "max": 6.5, "ideal": 6.0},
    "Lemon Balm": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Lemongrass": {"min": 5.5, "max": 7.0, "ideal": 6.5},
    "Lettuce": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Lovage": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Marjoram": {"min": 6.5, "max": 7.5, "ideal": 7.0},
    "Microgreens": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Mint": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Nasturtium": {"min": 6.0, "max": 8.0, "ideal": 7.0},
    "Okra": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Onion": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Oregano": {"min": 6.0, "max": 8.0, "ideal": 7.0},
    "Parsley": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Parsnip": {"min": 5.5, "max": 7.0, "ideal": 6.5},
    "Passion Fruit": {"min": 5.5, "max": 6.5, "ideal": 6.0},
    "Pea": {"min": 6.0, "max": 7.5, "ideal": 6.8},
    "Pepper": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Peppermint": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Potato": {"min": 4.8, "max": 6.5, "ideal": 5.5},
    "Pumpkin": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Radicchio": {"min": 6.0, "max": 6.8, "ideal": 6.5},
    "Radish": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Raspberry": {"min": 5.5, "max": 6.5, "ideal": 6.0},
    "Rhubarb": {"min": 5.5, "max": 7.0, "ideal": 6.5},
    "Romaine Lettuce": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Romanesco": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Rosemary": {"min": 6.0, "max": 7.5, "ideal": 7.0},
    "Sage": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Sorrel": {"min": 5.5, "max": 6.8, "ideal": 6.0},
    "Spinach": {"min": 6.0, "max": 7.5, "ideal": 6.8},
    "Stevia": {"min": 6.5, "max": 7.5, "ideal": 7.0},
    "Strawberry": {"min": 5.5, "max": 6.8, "ideal": 6.0},
    "Sugar Snap Pea": {"min": 6.0, "max": 7.5, "ideal": 6.8},
    "Sunchoke": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Sunflower": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Sweet Pea": {"min": 6.0, "max": 7.5, "ideal": 6.8},
    "Sweet Potato": {"min": 5.5, "max": 6.5, "ideal": 6.0},
    "Swiss Chard": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Tarragon": {"min": 6.0, "max": 7.5, "ideal": 6.5},
    "Thyme": {"min": 6.0, "max": 8.0, "ideal": 7.0},
    "Tomatillo": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Tomato": {"min": 6.0, "max": 6.8, "ideal": 6.5},
    "Turmeric": {"min": 5.5, "max": 6.5, "ideal": 6.0},
    "Turnip": {"min": 5.5, "max": 7.0, "ideal": 6.5},
    "Watercress": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Watermelon": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Winter Squash": {"min": 6.0, "max": 7.0, "ideal": 6.5},
    "Zucchini": {"min": 6.0, "max": 7.0, "ideal": 6.5},
}

DEFAULT_PH = {"min": 6.0, "max": 7.0, "ideal": 6.5}

LIME_AMENDMENTS = [
    {
        "name": "Garden Lime (Calcium Carbonate)",
        "action": "Raises pH",
        "application": "Apply 5 lbs per 100 sq ft to raise pH by ~1 point",
        "when": "Apply in fall for best results, or 2-3 weeks before planting",
    },
    {
        "name": "Dolomitic Lime",
        "action": "Raises pH + adds magnesium",
        "application": "Apply 5 lbs per 100 sq ft; preferred if soil is also low in magnesium",
        "when": "Apply in fall for best results, or 2-3 weeks before planting",
    },
    {
        "name": "Wood Ash",
        "action": "Raises pH mildly + adds potassium",
        "application": "Apply 2 lbs per 100 sq ft for a gentle pH increase",
        "when": "Apply in fall or early spring; avoid contact with seedlings",
    },
]

SULFUR_AMENDMENTS = [
    {
        "name": "Elemental Sulfur",
        "action": "Lowers pH",
        "application": "Apply 1-2 lbs per 100 sq ft to lower pH by ~1 point",
        "when": "Apply in fall; takes several months for soil bacteria to convert",
    },
    {
        "name": "Iron Sulfate (Ferrous Sulfate)",
        "action": "Lowers pH faster than elemental sulfur",
        "application": "Apply 5 lbs per 100 sq ft to lower pH by ~1 point",
        "when": "Can apply any time; works within weeks",
    },
    {
        "name": "Sulfur-Coated Urea",
        "action": "Lowers pH + adds nitrogen",
        "application": "Apply according to nitrogen needs; provides gradual acidification",
        "when": "Apply during growing season for dual benefit",
    },
]

GENERAL_TIPS = [
    "Test your soil pH at the beginning of each growing season",
    "Most vegetables prefer a pH between 6.0-7.0",
    "Soil pH changes are gradual - apply amendments and retest after 4-6 weeks",
    "Organic matter (compost) naturally buffers soil pH toward neutral",
    "Mulching with pine needles or oak leaves can slowly lower pH",
    "Avoid over-liming; it's easier to lower pH than to raise it back",
    "Container gardens allow you to customize soil pH for individual plants",
]


def get_plant_status(soil_ph, pref):
    """Determine plant pH status and recommendation."""
    ideal = pref["ideal"]
    ph_min = pref["min"]
    ph_max = pref["max"]

    if abs(soil_ph - ideal) <= 0.3:
        return "optimal", 0.0, "Soil pH is ideal for this plant"
    elif ph_min <= soil_ph <= ph_max:
        diff = round(abs(soil_ph - ideal), 1)
        return "acceptable", diff, f"Soil pH is within acceptable range but {diff} from ideal ({ideal})"
    elif soil_ph < ph_min:
        diff = round(ph_min - soil_ph, 1)
        return "too_acidic", diff, f"Add garden lime to raise pH by {diff}-{round(diff + 0.5, 1)} points"
    else:
        diff = round(soil_ph - ph_max, 1)
        return "too_alkaline", diff, f"Add elemental sulfur to lower pH by {diff}-{round(diff + 0.5, 1)} points"


@soil_bp.route("/recommendations", methods=["GET"])
@jwt_required()
def get_soil_recommendations():
    """Return soil amendment recommendations based on user's soil pH and planted crops."""
    user_id = get_jwt_identity()
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not profile or profile.soil_ph is None:
        return jsonify({
            "error": "Soil pH not set. Please update your profile with your soil pH value.",
            "soil_ph_missing": True,
        }), 400

    soil_ph = profile.soil_ph

    # Get all user gardens and their plants
    gardens = UserGarden.query.filter_by(user_id=user_id).all()
    garden_ids = [g.id for g in gardens]
    garden_map = {g.id: g.garden_name for g in gardens}

    garden_plants = []
    if garden_ids:
        garden_plants = UserGardenPlant.query.filter(
            UserGardenPlant.garden_id.in_(garden_ids)
        ).all()

    # Analyze each plant
    plants_analysis = []
    acidic_plants = []
    alkaline_plants = []

    for gp in garden_plants:
        plant_name = gp.plant.name
        garden_name = garden_map.get(gp.garden_id, "Unknown")
        pref = PLANT_PH_PREFERENCES.get(plant_name, DEFAULT_PH)
        status, ph_diff, recommendation = get_plant_status(soil_ph, pref)

        plants_analysis.append({
            "plant_name": plant_name,
            "garden_name": garden_name,
            "preferred_ph": pref,
            "status": status,
            "ph_difference": ph_diff,
            "recommendation": recommendation,
        })

        if status == "too_acidic":
            acidic_plants.append(plant_name)
        elif status == "too_alkaline":
            alkaline_plants.append(plant_name)

    # Determine overall status
    statuses = [p["status"] for p in plants_analysis]
    if not statuses:
        overall_status = "no_plants"
    elif all(s == "optimal" for s in statuses):
        overall_status = "optimal"
    elif any(s in ("too_acidic", "too_alkaline") for s in statuses):
        overall_status = "needs_attention"
    else:
        overall_status = "acceptable"

    # Build amendment suggestions
    amendments = []
    if acidic_plants:
        # Deduplicate plant names
        unique_acidic = list(dict.fromkeys(acidic_plants))
        for amend in LIME_AMENDMENTS:
            amendments.append({**amend, "for_plants": unique_acidic})

    if alkaline_plants:
        unique_alkaline = list(dict.fromkeys(alkaline_plants))
        for amend in SULFUR_AMENDMENTS:
            amendments.append({**amend, "for_plants": unique_alkaline})

    return jsonify({
        "soil_ph": soil_ph,
        "overall_status": overall_status,
        "plants": plants_analysis,
        "amendments": amendments,
        "general_tips": GENERAL_TIPS,
    }), 200


@soil_bp.route("/ph-guide", methods=["GET"])
def get_ph_guide():
    """Return the full pH preference guide for all plants."""
    return jsonify({
        "plant_preferences": PLANT_PH_PREFERENCES,
        "default_ph": DEFAULT_PH,
        "amendments": {
            "to_raise_ph": LIME_AMENDMENTS,
            "to_lower_ph": SULFUR_AMENDMENTS,
        },
        "general_tips": GENERAL_TIPS,
    }), 200
