from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.database import db
from ..models.profile import UserProfile
from ..models.user_garden import UserGarden
from ..models.user_garden_plant import UserGardenPlant
from ..models.plant import Plant

weather_alerts_bp = Blueprint("weather_alerts", __name__)

# Weather code descriptions for human-readable output
WEATHER_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}

# Weather codes that indicate freezing conditions
FREEZING_CODES = {71, 73, 75}

# Weather codes that indicate cloudy/overcast conditions
CLOUDY_CODES = {3, 45, 48}

# Weather codes that indicate storms
STORM_CODES = {95}


def _get_user_plants(user_id):
    """Fetch all plants across all of a user's gardens."""
    gardens = UserGarden.query.filter_by(user_id=user_id).all()
    if not gardens:
        return []

    garden_ids = [g.id for g in gardens]
    garden_plants = (
        UserGardenPlant.query
        .filter(UserGardenPlant.garden_id.in_(garden_ids))
        .all()
    )

    plants = []
    seen_plant_ids = set()
    for gp in garden_plants:
        if gp.plant_id not in seen_plant_ids:
            seen_plant_ids.add(gp.plant_id)
            plant = Plant.query.get(gp.plant_id)
            if plant:
                plants.append(plant)
    return plants


def _generate_alerts(temperature, precipitation, weathercode, plants):
    """Generate weather-aware gardening alerts based on conditions and plants."""
    alerts = []
    alert_counter = 0

    plant_names = [p.name for p in plants]
    high_water_plants = [p.name for p in plants if p.water_needs == "High"]
    full_sun_plants = [p.name for p in plants if p.sunlight == "Full Sun"]

    # Frost Alert (critical): temperature < 2 C or freezing weather codes
    if temperature < 2 or weathercode in FREEZING_CODES:
        tender_plants = plant_names if plant_names else ["your plants"]
        alert_counter += 1
        alerts.append({
            "id": f"frost-{alert_counter}",
            "type": "frost",
            "severity": "critical",
            "title": "Frost Warning Tonight",
            "message": f"Temperature dropping to {temperature}\u00b0C. Protect {', '.join(tender_plants[:5])}.",
            "affected_plants": tender_plants[:10],
            "action": "Cover plants or bring containers indoors",
        })

    # Storm/Wind Alert (warning): weathercode indicates storms (95+)
    if weathercode in STORM_CODES or weathercode >= 95:
        alert_counter += 1
        alerts.append({
            "id": f"storm-{alert_counter}",
            "type": "storm",
            "severity": "warning",
            "title": "Storm Warning",
            "message": "Storm warning. Secure tall plants and garden structures.",
            "affected_plants": plant_names[:10],
            "action": "Stake tall plants and secure garden structures",
        })

    # Heavy Rain Alert (warning): precipitation > 10mm
    if precipitation > 10:
        drainage_plants = plant_names if plant_names else ["your plants"]
        alert_counter += 1
        alerts.append({
            "id": f"rain-{alert_counter}",
            "type": "heavy_rain",
            "severity": "warning",
            "title": "Heavy Rain Expected",
            "message": f"Heavy rain expected ({precipitation}mm). Skip watering today. Check drainage for {', '.join(drainage_plants[:5])}.",
            "affected_plants": drainage_plants[:10],
            "action": "Skip watering and check drainage around plants",
        })

    # Heat Alert (warning): temperature > 35 C
    if temperature > 35:
        affected = high_water_plants if high_water_plants else plant_names[:5]
        alert_counter += 1
        alerts.append({
            "id": f"heat-{alert_counter}",
            "type": "heat",
            "severity": "warning",
            "title": "High Heat Advisory",
            "message": f"High heat advisory ({temperature}\u00b0C). Water {', '.join(affected) if affected else 'your plants'} more frequently. Consider shade cloth.",
            "affected_plants": affected[:10],
            "action": "Increase watering frequency and provide shade",
        })

    # Drought/Dry Alert (info): no precipitation and plants with High water needs
    if precipitation == 0 and high_water_plants:
        alert_counter += 1
        alerts.append({
            "id": f"dry-{alert_counter}",
            "type": "dry",
            "severity": "info",
            "title": "No Rain Today",
            "message": f"No rain today. Remember to water your {', '.join(high_water_plants[:5])}.",
            "affected_plants": high_water_plants[:10],
            "action": "Water high-need plants manually",
        })

    # Overcast/Low Light (info): cloudy weather codes
    if weathercode in CLOUDY_CODES and full_sun_plants:
        alert_counter += 1
        alerts.append({
            "id": f"cloudy-{alert_counter}",
            "type": "cloudy",
            "severity": "info",
            "title": "Cloudy Conditions",
            "message": f"Cloudy conditions. Your {', '.join(full_sun_plants[:5])} may need extra attention.",
            "affected_plants": full_sun_plants[:10],
            "action": "Monitor full-sun plants for signs of light deficiency",
        })

    # Good Growing Weather (positive): 15-30 C, no extreme weather
    is_extreme = (
        temperature < 2
        or temperature > 35
        or precipitation > 10
        or weathercode in FREEZING_CODES
        or weathercode in STORM_CODES
        or weathercode >= 95
    )
    if not is_extreme and 15 <= temperature <= 30:
        alert_counter += 1
        alerts.append({
            "id": f"good-{alert_counter}",
            "type": "good_weather",
            "severity": "positive",
            "title": "Great Growing Conditions",
            "message": "Great growing conditions! Perfect day for garden maintenance.",
            "affected_plants": [],
            "action": "Enjoy gardening today",
        })

    return alerts


@weather_alerts_bp.route("", methods=["GET"])
@jwt_required()
def get_weather_alerts():
    """Generate weather-aware gardening alerts for the authenticated user."""
    user_id = get_jwt_identity()

    # Get optional query params for weather overrides, with defaults
    temperature = request.args.get("temperature", type=float)
    precipitation = request.args.get("precipitation", type=float)
    weathercode = request.args.get("weathercode", type=int)

    # Use defaults if not provided
    if temperature is None:
        temperature = 18.0
    if precipitation is None:
        precipitation = 0.0
    if weathercode is None:
        weathercode = 2

    # Fetch user's plants
    plants = _get_user_plants(user_id)

    # Generate alerts
    alerts = _generate_alerts(temperature, precipitation, weathercode, plants)

    # Build weather description
    description = WEATHER_DESCRIPTIONS.get(weathercode, "Unknown conditions")

    return jsonify({
        "alerts": alerts,
        "current_conditions": {
            "temperature": temperature,
            "precipitation": precipitation,
            "description": description,
        },
    }), 200
