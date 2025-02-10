import requests
from flask import Blueprint, request, jsonify

weather_bp = Blueprint("weather", __name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

@weather_bp.route("/get_weather", methods=["GET"])
def get_weather():
    """Fetches weather data for a given Zip code."""
    zip_code = request.args.get("zip")
    
    if not zip_code:
        return jsonify({"error": "Zip code is required."}), 400
    
    # Convert Zip code to latitude & longitude using Open-Meteo's geocoding API
    geo_response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}")
    
    if geo_response.status_code != 200 or "results" not in geo_response.json():
        return jsonify({"error": "Failed to fetch location data."}), 500
    
    geo_data = geo_response.json()["results"][0]
    latitude = geo_data["latitude"]
    longitude = geo_data["longitude"]
    
    # Fetch weather data using lat/lon
    weather_response = requests.get(
        f"{OPEN_METEO_URL}?latitude={latitude}&longitude={longitude}&current=temperature_2m,precipitation,weathercode"
    )
    
    if weather_response.status_code == 200:
        return jsonify(weather_response.json())
    else:
        return jsonify({"error": "Failed to fetch weather data."}), weather_response.status_code