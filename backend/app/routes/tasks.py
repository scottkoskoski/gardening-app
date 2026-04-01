from datetime import datetime, date, timedelta, timezone
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models.database import db
from ..models.user_garden import UserGarden
from ..models.user_garden_plant import UserGardenPlant, GrowthStage
from ..models.plant import Plant
from ..models.profile import UserProfile
from .frost_dates import FROST_DATA, parse_zone_number

tasks_bp = Blueprint("tasks", __name__)

TODAY = date(2026, 4, 1)


def _due_label(target_date):
    """Return 'today', 'this_week', or 'upcoming' relative to TODAY."""
    if target_date is None:
        return "today"
    delta = (target_date - TODAY).days
    if delta <= 0:
        return "today"
    if delta <= 7:
        return "this_week"
    return "upcoming"


def _watering_tasks(garden, garden_plant, plant):
    """Generate watering tasks based on plant water needs."""
    tasks = []
    water = (plant.water_needs or "").capitalize()
    if water == "High":
        tasks.append({
            "id": f"water-{plant.name.lower().replace(' ', '-')}-{garden_plant.id}",
            "type": "watering",
            "priority": "high",
            "title": f"Water your {plant.name}",
            "description": f"{plant.name} has high water needs. Check soil moisture daily.",
            "garden_name": garden.garden_name,
            "garden_id": garden.id,
            "plant_name": plant.name,
            "due": "today",
        })
    elif water == "Medium":
        tasks.append({
            "id": f"water-{plant.name.lower().replace(' ', '-')}-{garden_plant.id}",
            "type": "watering",
            "priority": "medium",
            "title": f"Water your {plant.name}",
            "description": f"{plant.name} has medium water needs. Water every 2-3 days.",
            "garden_name": garden.garden_name,
            "garden_id": garden.id,
            "plant_name": plant.name,
            "due": "this_week",
        })
    elif water == "Low":
        tasks.append({
            "id": f"water-{plant.name.lower().replace(' ', '-')}-{garden_plant.id}",
            "type": "watering",
            "priority": "low",
            "title": f"Water your {plant.name}",
            "description": f"{plant.name} has low water needs. Water once a week.",
            "garden_name": garden.garden_name,
            "garden_id": garden.id,
            "plant_name": plant.name,
            "due": "this_week",
        })
    return tasks


def _growth_stage_tasks(garden, garden_plant, plant):
    """Generate growth stage transition suggestions."""
    tasks = []
    if not garden_plant.planted_at:
        return tasks

    planted = garden_plant.planted_at
    if planted.tzinfo:
        days_since = (datetime.now(timezone.utc) - planted).days
    else:
        days_since = (datetime.utcnow() - planted).days

    stage = garden_plant.growth_stage
    suggestion = None

    if stage == GrowthStage.SEEDLING and days_since > 21:
        suggestion = ("Vegetative", "has been a seedling for over 21 days. Consider updating its growth stage to Vegetative.")
    elif stage == GrowthStage.VEGETATIVE and days_since > 30:
        suggestion = ("Flowering", "has been in the vegetative stage for over 30 days. It may be ready to transition to Flowering.")
    elif stage == GrowthStage.FLOWERING and days_since > 20:
        suggestion = ("Fruiting", "has been flowering for over 20 days. Check if it is transitioning to Fruiting.")

    if suggestion:
        tasks.append({
            "id": f"growth-{plant.name.lower().replace(' ', '-')}-{garden_plant.id}",
            "type": "growth_stage",
            "priority": "medium",
            "title": f"Update {plant.name} to {suggestion[0]}",
            "description": f"{plant.name} {suggestion[1]}",
            "garden_name": garden.garden_name,
            "garden_id": garden.id,
            "plant_name": plant.name,
            "due": "today",
        })
    return tasks


def _harvest_tasks(garden, garden_plant, plant):
    """Generate harvest reminders when expected harvest date is near or past."""
    tasks = []
    if not garden_plant.expected_harvest_date:
        return tasks

    harvest_date = garden_plant.expected_harvest_date
    if hasattr(harvest_date, "date"):
        harvest_date = harvest_date.date()

    days_until = (harvest_date - TODAY).days

    if days_until <= 7:
        if days_until <= 0:
            desc = f"{plant.name} is ready to harvest! The expected harvest date has passed."
            due = "today"
        else:
            desc = f"{plant.name} is expected to be ready for harvest in {days_until} day{'s' if days_until != 1 else ''}."
            due = "this_week"

        tasks.append({
            "id": f"harvest-{plant.name.lower().replace(' ', '-')}-{garden_plant.id}",
            "type": "harvest",
            "priority": "high",
            "title": f"Harvest your {plant.name}",
            "description": desc,
            "garden_name": garden.garden_name,
            "garden_id": garden.id,
            "plant_name": plant.name,
            "due": due,
        })
    return tasks


def _seasonal_tasks(zone_str):
    """Generate seasonal tasks based on current month and zone."""
    tasks = []
    current_month = TODAY.month

    # Spring tasks (March-May)
    if 3 <= current_month <= 5:
        tasks.append({
            "id": "seasonal-compost",
            "type": "seasonal",
            "priority": "low",
            "title": "Start composting",
            "description": "Spring is a great time to start or refresh your compost pile for the growing season.",
            "garden_name": None,
            "garden_id": None,
            "plant_name": None,
            "due": "this_week",
        })
        tasks.append({
            "id": "seasonal-prepare-beds",
            "type": "seasonal",
            "priority": "medium",
            "title": "Prepare garden beds",
            "description": "Prepare your garden beds for spring planting. Turn soil and add amendments.",
            "garden_name": None,
            "garden_id": None,
            "plant_name": None,
            "due": "this_week",
        })

    # Frost-related seasonal tasks
    if zone_str:
        zone_num = parse_zone_number(zone_str)
        if zone_num and zone_num < 11:
            lookup = max(3, min(10, zone_num))
            frost_info = FROST_DATA[lookup]
            last_frost_date = date(TODAY.year, frost_info["last_frost"][0], frost_info["last_frost"][1])
            days_to_frost = (last_frost_date - TODAY).days

            if -7 <= days_to_frost <= 21:
                tasks.append({
                    "id": "seasonal-transplant",
                    "type": "seasonal",
                    "priority": "medium",
                    "title": "Prepare to transplant seedlings outdoors",
                    "description": f"Your last frost date is approximately {last_frost_date.strftime('%B %d')}. Start hardening off indoor seedlings.",
                    "garden_name": None,
                    "garden_id": None,
                    "plant_name": None,
                    "due": "this_week" if days_to_frost <= 7 else "upcoming",
                })

    # General pest check
    tasks.append({
        "id": "seasonal-pest-check",
        "type": "seasonal",
        "priority": "low",
        "title": "Check for pests weekly",
        "description": "Inspect your plants for signs of pests or disease. Early detection prevents major damage.",
        "garden_name": None,
        "garden_id": None,
        "plant_name": None,
        "due": "this_week",
    })

    return tasks


def _frost_warning_tasks(zone_str, gardens):
    """Generate frost warning if within 2 weeks of last frost date."""
    tasks = []
    if not zone_str:
        return tasks

    zone_num = parse_zone_number(zone_str)
    if not zone_num or zone_num >= 11:
        return tasks

    lookup = max(3, min(10, zone_num))
    frost_info = FROST_DATA[lookup]
    last_frost_date = date(TODAY.year, frost_info["last_frost"][0], frost_info["last_frost"][1])
    days_to_frost = (last_frost_date - TODAY).days

    if 0 <= days_to_frost <= 14:
        tasks.append({
            "id": "frost-warning",
            "type": "frost_warning",
            "priority": "high",
            "title": "Frost warning — protect tender plants",
            "description": f"Your last frost date is around {last_frost_date.strftime('%B %d')}. Protect tender plants with covers or bring them indoors.",
            "garden_name": None,
            "garden_id": None,
            "plant_name": None,
            "due": "today",
        })

    return tasks


@tasks_bp.route("", methods=["GET"])
@jwt_required()
def get_tasks():
    """Generate smart task reminders for the authenticated user."""
    user_id = get_jwt_identity()
    tasks = []

    # Fetch user profile for zone info
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    zone_str = profile.plant_hardiness_zone if profile else None

    # Fetch user gardens
    gardens = UserGarden.query.filter_by(user_id=user_id).all()

    # Plant-specific tasks
    for garden in gardens:
        garden_zone = garden.plant_hardiness_zone or zone_str
        garden_plants = UserGardenPlant.query.filter_by(garden_id=garden.id).all()

        for gp in garden_plants:
            plant = Plant.query.get(gp.plant_id)
            if not plant:
                continue

            tasks.extend(_watering_tasks(garden, gp, plant))
            tasks.extend(_growth_stage_tasks(garden, gp, plant))
            tasks.extend(_harvest_tasks(garden, gp, plant))

    # Seasonal tasks
    tasks.extend(_seasonal_tasks(zone_str))

    # Frost warnings
    tasks.extend(_frost_warning_tasks(zone_str, gardens))

    # Sort by priority: high first, then medium, then low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tasks.sort(key=lambda t: priority_order.get(t["priority"], 3))

    # Build summary
    summary = {
        "total": len(tasks),
        "high": sum(1 for t in tasks if t["priority"] == "high"),
        "medium": sum(1 for t in tasks if t["priority"] == "medium"),
        "low": sum(1 for t in tasks if t["priority"] == "low"),
    }

    return jsonify({"tasks": tasks, "summary": summary}), 200
