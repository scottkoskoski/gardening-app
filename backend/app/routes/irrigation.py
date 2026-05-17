"""Irrigation frequency recommendations.

Calculates per-plant watering schedules based on plant water needs, growth
stage, container vs in-ground placement, and optional current weather
conditions (temperature, precipitation). Recommendations are computed on
the fly from existing data - no new tables required.
"""

import logging
from datetime import date, timedelta, timezone

import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models.plant import Plant
from ..models.profile import UserProfile
from ..models.user_garden import UserGarden
from ..models.user_garden_plant import GrowthStage, UserGardenPlant

irrigation_bp = Blueprint("irrigation", __name__)
logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
EXTERNAL_API_TIMEOUT = 10

# Base watering frequency in days, keyed by plant water_needs value.
BASE_FREQUENCY_DAYS = {
    "Low": 7,
    "Medium": 3,
    "High": 2,
}
DEFAULT_FREQUENCY_DAYS = 4

# Water amount guidance, keyed by plant water_needs value.
AMOUNT_GUIDANCE = {
    "Low": "About 0.5 inch of water; let soil dry between waterings.",
    "Medium": "About 1 inch of water; soil should stay evenly moist.",
    "High": "1 to 1.5 inches of water; keep soil consistently moist.",
}
DEFAULT_AMOUNT_GUIDANCE = "Water deeply until soil is moist to a depth of 6 inches."

# Container-style garden types get a "container" frequency boost.
CONTAINER_GARDEN_KEYWORDS = ("container", "balcony", "rooftop", "indoor", "patio")

# Weather thresholds.
HEAVY_RAIN_MM = 10.0
HOT_C = 30.0
COOL_C = 10.0


def _fetch_current_weather(zip_code):
    """Fetch current weather for a zip code. Returns None on any failure."""
    if not zip_code or not zip_code.isalnum() or len(zip_code) > 10:
        return None
    try:
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}",
            timeout=EXTERNAL_API_TIMEOUT,
        )
        if geo.status_code != 200:
            return None
        results = geo.json().get("results") or []
        if not results:
            return None
        lat = results[0]["latitude"]
        lon = results[0]["longitude"]

        weather = requests.get(
            f"{OPEN_METEO_URL}?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,precipitation",
            timeout=EXTERNAL_API_TIMEOUT,
        )
        if weather.status_code != 200:
            return None
        current = weather.json().get("current") or {}
        return {
            "temperature": current.get("temperature_2m"),
            "precipitation": current.get("precipitation"),
        }
    except (requests.RequestException, KeyError, IndexError, ValueError) as e:
        logger.warning("Irrigation weather lookup failed for zip=%s: %s", zip_code, e)
        return None


def _is_container_garden(garden):
    """Detect a container-style garden from its type or flags."""
    if getattr(garden, "is_rooftop_garden", False):
        return True
    garden_type = getattr(garden, "garden_type", None)
    if garden_type is None:
        return False
    name = (getattr(garden_type, "name", "") or "").lower()
    return any(keyword in name for keyword in CONTAINER_GARDEN_KEYWORDS)


def _compute_recommendation(plant, garden_plant, garden, weather):
    """Compute an irrigation recommendation for one user-garden-plant row."""
    water_needs = plant.water_needs or "Medium"
    base_days = BASE_FREQUENCY_DAYS.get(water_needs, DEFAULT_FREQUENCY_DAYS)
    frequency = base_days
    reasoning = [f"{water_needs} water needs: water roughly every {base_days} days."]

    # Growth stage: seedlings need more frequent, shallow waterings.
    stage = garden_plant.growth_stage
    if stage == GrowthStage.SEEDLING:
        frequency = max(1, frequency - 1)
        reasoning.append("Seedlings need more frequent watering to keep roots moist.")
    elif stage == GrowthStage.FRUITING:
        reasoning.append("Fruiting plants benefit from consistent moisture for good fruit set.")

    # Container plants dry out faster.
    in_container = _is_container_garden(garden) or bool(plant.suitable_for_containers and garden.garden_type and "container" in (garden.garden_type.name or "").lower())
    if in_container:
        frequency = max(1, frequency - 1)
        reasoning.append("Container plants dry out faster than in-ground plantings.")

    # Weather adjustments.
    skip_today = False
    if weather:
        temp = weather.get("temperature")
        precip = weather.get("precipitation")
        if precip is not None and precip >= HEAVY_RAIN_MM:
            skip_today = True
            reasoning.append(
                f"Heavy rain today ({precip:.1f} mm) - skip watering and check drainage."
            )
        elif temp is not None and temp >= HOT_C:
            frequency = max(1, frequency - 1)
            reasoning.append(
                f"Hot weather ({temp:.0f}°C) - water more frequently to prevent stress."
            )
        elif temp is not None and temp <= COOL_C:
            frequency += 2
            reasoning.append(
                f"Cool weather ({temp:.0f}°C) - plants need less water in cooler temps."
            )

    # Compute next watering date based on planted_at + multiples of frequency.
    today = date.today()
    planted_at = garden_plant.planted_at
    if planted_at is None:
        next_watering = today
    else:
        if hasattr(planted_at, "date"):
            planted_date = planted_at.date() if planted_at.tzinfo is None or planted_at.tzinfo == timezone.utc else planted_at.astimezone(timezone.utc).date()
        else:
            planted_date = planted_at
        days_since = (today - planted_date).days
        if days_since < 0:
            next_watering = today
        else:
            cycles_passed = days_since // frequency
            next_watering = planted_date + timedelta(days=(cycles_passed + 1) * frequency)

    if skip_today:
        next_watering = max(next_watering, today + timedelta(days=2))

    days_until = (next_watering - today).days
    if skip_today:
        urgency = "skip"
    elif days_until <= 0:
        urgency = "today"
    elif days_until <= 2:
        urgency = "soon"
    else:
        urgency = "later"

    return {
        "garden_plant_id": garden_plant.id,
        "plant_id": plant.id,
        "plant_name": plant.name,
        "garden_id": garden.id,
        "garden_name": garden.garden_name,
        "growth_stage": stage.value if stage else None,
        "water_needs": water_needs,
        "frequency_days": frequency,
        "next_watering": next_watering.isoformat(),
        "days_until": days_until,
        "skip_today": skip_today,
        "urgency": urgency,
        "amount_guidance": AMOUNT_GUIDANCE.get(water_needs, DEFAULT_AMOUNT_GUIDANCE),
        "reasoning": reasoning,
    }


@irrigation_bp.route("", methods=["GET"])
@jwt_required()
def get_irrigation_schedule():
    """Return per-plant irrigation recommendations for the authenticated user.

    Query params:
        zip (optional): override the zip code used to look up current weather.
                        Defaults to the user's profile zip.
    """
    user_id = get_jwt_identity()

    profile = UserProfile.query.filter_by(user_id=user_id).first()
    zip_override = (request.args.get("zip") or "").strip()
    zip_code = zip_override or (profile.zip_code if profile else None)

    weather = _fetch_current_weather(zip_code) if zip_code else None

    gardens = UserGarden.query.filter_by(user_id=user_id).all()

    recommendations = []
    for garden in gardens:
        garden_plants = UserGardenPlant.query.filter_by(garden_id=garden.id).all()
        for gp in garden_plants:
            plant = Plant.query.get(gp.plant_id)
            if not plant:
                continue
            recommendations.append(_compute_recommendation(plant, gp, garden, weather))

    # Most urgent first, then by next watering date.
    urgency_order = {"today": 0, "soon": 1, "later": 2, "skip": 3}
    recommendations.sort(
        key=lambda r: (urgency_order.get(r["urgency"], 4), r["next_watering"])
    )

    summary = {
        "total": len(recommendations),
        "today": sum(1 for r in recommendations if r["urgency"] == "today"),
        "soon": sum(1 for r in recommendations if r["urgency"] == "soon"),
        "later": sum(1 for r in recommendations if r["urgency"] == "later"),
        "skip": sum(1 for r in recommendations if r["urgency"] == "skip"),
    }

    return jsonify({
        "schedule": recommendations,
        "summary": summary,
        "weather": weather,
        "zip_code": zip_code,
    }), 200
