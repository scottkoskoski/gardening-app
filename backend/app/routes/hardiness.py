import requests
from flask import Blueprint, request, jsonify

# Create a Blueprint for the plant hardiness API
hardiness_bp = Blueprint("hardiness", __name__)

# USDA API URL
USDA_API_URL = "https://phzmapi.org/"

@hardiness_bp.route("/get_hardiness_zone", methods=["GET"])
def get_hardiness_zone():
    """Fetches the USDA Hardiness Zone based on Zip code."""
    zip_code = request.args.get("zip") # Get Zip code from query parameters
    
    if not zip_code:
        return jsonify({"error": "Zip code is required."}), 400 # Return error if Zip code is not provided
    
    # Call the USDA API
    response = requests.get(f"{USDA_API_URL}/{zip_code}.json")
    
    if response.status_code == 200:
        return jsonify(response.json()), 200 # Return the response from the USDA API as JSON
    else:
        return jsonify({"error": "Failed to fetch hardiness zone.",
                        "status_code": response.status_code,
                        "details": response.text}), response.status_code