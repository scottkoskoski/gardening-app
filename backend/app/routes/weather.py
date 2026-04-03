import logging
import requests
from flask import Blueprint, request, jsonify

weather_bp = Blueprint("weather", __name__)
logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Timeout for external API calls (seconds)
EXTERNAL_API_TIMEOUT = 10


@weather_bp.route("/get_weather", methods=["GET"])
def get_weather():
    """Fetches weather data for a given Zip code."""
    zip_code = request.args.get("zip", "").strip()

    if not zip_code:
        return jsonify({"error": "Zip code is required."}), 400

    # Validate zip code format (basic check)
    if not zip_code.isalnum() or len(zip_code) > 10:
        return jsonify({"error": "Invalid zip code format."}), 400

    try:
        # Convert Zip code to latitude & longitude using Open-Meteo's geocoding API
        geo_response = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}",
            timeout=EXTERNAL_API_TIMEOUT,
        )

        if geo_response.status_code != 200 or "results" not in geo_response.json():
            logger.warning("Failed to geocode zip=%s status=%s", zip_code, geo_response.status_code)
            return jsonify({"error": "Failed to fetch location data."}), 502

        geo_data = geo_response.json()["results"][0]
        latitude = geo_data["latitude"]
        longitude = geo_data["longitude"]

        # Fetch weather data using lat/lon
        weather_response = requests.get(
            f"{OPEN_METEO_URL}?latitude={latitude}&longitude={longitude}&current=temperature_2m,precipitation,weathercode",
            timeout=EXTERNAL_API_TIMEOUT,
        )

        if weather_response.status_code == 200:
            return jsonify(weather_response.json())
        else:
            logger.warning("Weather API returned status=%s for zip=%s", weather_response.status_code, zip_code)
            return jsonify({"error": "Failed to fetch weather data."}), 502

    except requests.Timeout:
        logger.error("External weather API timed out for zip=%s", zip_code)
        return jsonify({"error": "Weather service timed out. Please try again."}), 504
    except requests.RequestException as e:
        logger.error("Weather API request failed for zip=%s: %s", zip_code, e)
        return jsonify({"error": "Failed to connect to weather service."}), 502
    except (KeyError, IndexError) as e:
        logger.warning("Unexpected response format from weather API for zip=%s: %s", zip_code, e)
        return jsonify({"error": "Failed to fetch location data."}), 502
