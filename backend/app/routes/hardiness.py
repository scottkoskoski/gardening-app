import logging
import re
import requests as http_requests
from flask import Blueprint, request, jsonify

# Create a Blueprint for the plant hardiness API
hardiness_bp = Blueprint("hardiness", __name__)
logger = logging.getLogger(__name__)

# USDA API URL
USDA_API_URL = "https://phzmapi.org/"

# Timeout for external API calls (seconds)
EXTERNAL_API_TIMEOUT = 10

# Zip code validation pattern
ZIP_CODE_PATTERN = re.compile(r"^\d{5}(-\d{4})?$")


@hardiness_bp.route("/get_hardiness_zone", methods=["GET"])
def get_hardiness_zone():
    """Fetches the USDA Hardiness Zone based on Zip code."""
    zip_code = request.args.get("zip", "").strip()

    if not zip_code:
        return jsonify({"error": "Zip code is required."}), 400

    if not ZIP_CODE_PATTERN.match(zip_code):
        return jsonify({"error": "Invalid zip code format. Use 12345 or 12345-6789."}), 400

    try:
        # Call the USDA API
        response = http_requests.get(
            f"{USDA_API_URL}/{zip_code}.json",
            timeout=EXTERNAL_API_TIMEOUT,
        )

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            logger.warning(
                "USDA API returned status=%s for zip=%s",
                response.status_code, zip_code
            )
            return jsonify({
                "error": "Failed to fetch hardiness zone.",
                "status_code": response.status_code,
            }), 502

    except http_requests.Timeout:
        logger.error("USDA API timed out for zip=%s", zip_code)
        return jsonify({"error": "Hardiness zone service timed out. Please try again."}), 504
    except http_requests.RequestException as e:
        logger.error("USDA API request failed for zip=%s: %s", zip_code, e)
        return jsonify({"error": "Failed to connect to hardiness zone service."}), 502
