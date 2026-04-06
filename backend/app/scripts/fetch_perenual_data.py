"""
Fetches plant data from the Perenual API and populates the database.

Usage:
    cd backend
    source venv/bin/activate
    python app/scripts/fetch_perenual_data.py

Requires PERENUAL_API_KEY in the environment or backend/.env file.
Free tier: 300 requests/day, ~3000 species available.
Each page returns 30 species, so fetching all pages uses ~100 requests.
"""

import os
import re
import sys
import time

import requests
from dotenv import load_dotenv

# Load .env from the backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from app import create_app
from app.models.database import db
from app.models.plant import Plant, PlantSchema

app = create_app()

PERENUAL_API_URL = "https://perenual.com/api"

plant_schema = PlantSchema()

# Mapping from Perenual sunlight values to our schema's allowed values
SUNLIGHT_MAP = {
    "full sun": "Full Sun",
    "full_sun": "Full Sun",
    "part shade": "Partial Shade",
    "part sun": "Partial Sun",
    "part shade/part sun": "Partial Sun",
    "part sun/part shade": "Partial Sun",
    "filtered shade": "Partial Shade",
    "full shade": "Full Shade",
    "deep shade": "Full Shade",
    "sheltered": "Partial Shade",
}

# Mapping from Perenual watering values to our schema's allowed values
WATERING_MAP = {
    "frequent": "High",
    "average": "Medium",
    "minimum": "Low",
    "none": "Low",
}

# Mapping from Perenual cycle values to our growing_season
CYCLE_MAP = {
    "annual": "Summer",
    "biennial": "Spring",
    "perennial": None,
    "biannual": "Spring",
}


def normalize_sunlight(sunlight_list):
    """Convert Perenual sunlight list to our single enum value."""
    if not sunlight_list:
        return None
    # Perenual returns a list like ["full sun"] or ["part shade", "full sun"]
    # Take the first value
    val = sunlight_list[0].lower().strip() if isinstance(sunlight_list, list) else str(sunlight_list).lower().strip()
    return SUNLIGHT_MAP.get(val)


def normalize_watering(watering):
    """Convert Perenual watering string to our enum value."""
    if not watering:
        return None
    return WATERING_MAP.get(watering.lower().strip())


def estimate_space(dimensions):
    """Estimate space_required from Perenual dimensions."""
    if not dimensions or not isinstance(dimensions, dict):
        return None
    # dimensions has min_value, max_value, type (e.g. "feet", "cm")
    max_val = dimensions.get("max_value")
    if max_val is None:
        return None
    try:
        max_val = float(max_val)
    except (ValueError, TypeError):
        return None
    unit = dimensions.get("type", "").lower()
    # Convert to feet if needed
    if "cm" in unit:
        max_val = max_val / 30.48
    if max_val <= 2:
        return "Small"
    elif max_val <= 6:
        return "Medium"
    else:
        return "Large"


def get_image_url(default_image):
    """Extract the best available image URL from Perenual response."""
    if not default_image or not isinstance(default_image, dict):
        return None
    # Prefer regular_url, then medium_url, then small_url, then original_url
    for key in ["regular_url", "medium_url", "small_url", "original_url"]:
        url = default_image.get(key)
        if url and isinstance(url, str) and url.startswith("http"):
            return url
    return None


def sanitize_name(name):
    """Sanitize plant name to match schema's allowed characters."""
    if not name:
        return None
    sanitized = re.sub(r"[^a-zA-Z0-9 '\-]", "", name)
    return sanitized[:100] if sanitized else None


def parse_hardiness(hardiness):
    """Parse Perenual hardiness object to min/max zone strings."""
    if not hardiness or not isinstance(hardiness, dict):
        return None, None
    h_min = hardiness.get("min")
    h_max = hardiness.get("max")
    # Perenual returns e.g. "7" or "7a"
    return (str(h_min) if h_min else None, str(h_max) if h_max else None)


def fetch_species_page(api_key, page=1, indoor=None):
    """Fetch a single page of species from the Perenual API."""
    params = {"key": api_key, "page": page}
    if indoor is not None:
        params["indoor"] = 1 if indoor else 0
    resp = requests.get(f"{PERENUAL_API_URL}/species-list", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def process_species(species):
    """Convert a Perenual species entry to our Plant model fields."""
    name = sanitize_name(species.get("common_name"))
    if not name:
        return None

    sunlight_raw = species.get("sunlight")
    watering_raw = species.get("watering")
    cycle = species.get("cycle", "")

    # Parse hardiness
    hardiness = species.get("hardiness") or {}
    h_min, h_max = parse_hardiness(hardiness)

    # Parse dimensions for height estimate
    dimensions = species.get("dimensions") or {}
    height_max = None
    if dimensions.get("max_value") is not None:
        try:
            height_max = float(dimensions["max_value"])
            if "cm" in str(dimensions.get("type", "")).lower():
                height_max = height_max / 2.54  # convert to inches
            elif "feet" in str(dimensions.get("type", "")).lower():
                height_max = height_max * 12  # convert to inches
        except (ValueError, TypeError):
            height_max = None

    plant_data = {
        "name": name,
        "scientific_name": (species.get("scientific_name") or [None])[0] if isinstance(species.get("scientific_name"), list) else species.get("scientific_name"),
        "description": species.get("description") if isinstance(species.get("description"), str) else None,
        "sunlight": normalize_sunlight(sunlight_raw),
        "water_needs": normalize_watering(watering_raw),
        "hardiness_min": h_min,
        "hardiness_max": h_max,
        "growing_season": CYCLE_MAP.get(cycle.lower().strip()) if cycle else None,
        "space_required": estimate_space(dimensions),
        "height": height_max,
        "image_url": get_image_url(species.get("default_image")),
        "requires_greenhouse": species.get("indoor", False) if isinstance(species.get("indoor"), bool) else False,
        "suitable_for_containers": species.get("indoor", False) if isinstance(species.get("indoor"), bool) else False,
    }

    # Truncate scientific_name if too long
    if plant_data["scientific_name"] and len(plant_data["scientific_name"]) > 200:
        plant_data["scientific_name"] = plant_data["scientific_name"][:200]

    # Validate
    errors = plant_schema.validate(plant_data)
    if errors:
        return None

    return plant_data


def fetch_perenual_data(max_pages=None):
    """Fetch plant data from Perenual API and populate the database."""
    api_key = os.environ.get("PERENUAL_API_KEY")
    if not api_key:
        print("ERROR: PERENUAL_API_KEY not set. Add it to backend/.env or set it in your environment.")
        print("Sign up for a free key at https://perenual.com/")
        sys.exit(1)

    with app.app_context():
        # Check how many plants already exist
        existing_count = Plant.query.count()
        print(f"Database currently has {existing_count} plants.")

        total_added = 0
        total_skipped_existing = 0
        total_skipped_validation = 0
        total_pages_fetched = 0

        page = 1
        last_page = None

        while True:
            if max_pages and page > max_pages:
                print(f"Reached max_pages limit ({max_pages}).")
                break

            print(f"\nFetching page {page}{f'/{last_page}' if last_page else ''}...")

            try:
                data = fetch_species_page(api_key, page=page)
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    print("Rate limited. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                print(f"HTTP error fetching page {page}: {e}")
                break
            except requests.exceptions.RequestException as e:
                print(f"Request error fetching page {page}: {e}")
                break

            total_pages_fetched += 1
            last_page = data.get("last_page", page)
            species_list = data.get("data", [])

            if not species_list:
                print("No more species data. Stopping.")
                break

            for species in species_list:
                plant_data = process_species(species)
                if plant_data is None:
                    total_skipped_validation += 1
                    continue

                # Check for duplicates by name
                existing = Plant.query.filter_by(name=plant_data["name"]).first()
                if existing:
                    total_skipped_existing += 1
                    continue

                try:
                    new_plant = Plant(**plant_data)
                    db.session.add(new_plant)
                    total_added += 1
                except Exception as e:
                    print(f"Error adding {plant_data['name']}: {e}")
                    continue

            # Commit each page to avoid losing progress
            try:
                db.session.commit()
                print(f"Page {page}: added {len(species_list)} candidates, "
                      f"running total: {total_added} added, "
                      f"{total_skipped_existing} duplicates, "
                      f"{total_skipped_validation} skipped.")
            except Exception as e:
                db.session.rollback()
                print(f"Error committing page {page}: {e}")

            if page >= last_page:
                print("Reached last page.")
                break

            page += 1
            # Be respectful of rate limits (300/day = ~1 every 5 seconds to be safe)
            time.sleep(1)

        print("\n---- Import Summary ----")
        print(f"Pages fetched: {total_pages_fetched}")
        print(f"Plants added: {total_added}")
        print(f"Plants skipped (duplicate): {total_skipped_existing}")
        print(f"Plants skipped (validation): {total_skipped_validation}")
        print(f"Total plants in database: {Plant.query.count()}")


def clear_dead_image_plants():
    """Remove plants that have dead OpenFarm image URLs."""
    with app.app_context():
        dead_openfarm = Plant.query.filter(
            db.or_(
                Plant.image_url.like("/assets/%"),
                Plant.image_url.like("%openfarm.cc%"),
                Plant.image_url.like("%openfarm-project%"),
            )
        ).all()
        count = len(dead_openfarm)
        if count:
            for plant in dead_openfarm:
                # Clear the dead URL rather than deleting the plant (preserves user garden references)
                plant.image_url = None
            db.session.commit()
            print(f"Cleared {count} dead OpenFarm image URLs.")
        else:
            print("No dead OpenFarm image URLs found.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch plant data from Perenual API")
    parser.add_argument("--max-pages", type=int, default=None,
                        help="Max number of pages to fetch (30 species/page). Omit for all pages.")
    parser.add_argument("--clear-dead-images", action="store_true",
                        help="Clear dead OpenFarm image URLs from existing plants.")
    args = parser.parse_args()

    if args.clear_dead_images:
        clear_dead_image_plants()

    fetch_perenual_data(max_pages=args.max_pages)
    print("Done.")
