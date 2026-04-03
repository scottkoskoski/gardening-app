"""
Fetches plant images from Wikipedia/Wikimedia Commons and updates the database.

Uses the Wikipedia API to find the main image for each plant by its name.
Images from Wikimedia are permanently hosted and freely licensed.

Usage:
    cd backend
    PYTHONPATH=. venv/bin/python app/scripts/fetch_plant_images.py
    PYTHONPATH=. venv/bin/python app/scripts/fetch_plant_images.py --limit 100
"""

import re
import time
import urllib.parse

import requests

from app import create_app
from app.models.database import db
from app.models.plant import Plant

app = create_app()

WIKI_API = "https://en.wikipedia.org/w/api.php"
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "GardeningApp/1.0 (plant image lookup; educational project)"
})


def search_wikipedia_image(query):
    """Search Wikipedia for a plant page and extract its main image URL."""
    # Step 1: Search for the page
    params = {
        "action": "query",
        "format": "json",
        "titles": query,
        "redirects": 1,
        "prop": "pageimages",
        "piprop": "original",
        "pilicense": "any",
    }
    resp = SESSION.get(WIKI_API, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if page_id == "-1":
            continue
        original = page.get("original", {})
        source = original.get("source")
        if source and is_valid_image(source):
            return source

    # Step 2: If direct title didn't work, try a search
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": f"{query} plant",
        "srlimit": 3,
    }
    resp = SESSION.get(WIKI_API, params=search_params, timeout=15)
    resp.raise_for_status()
    results = resp.json().get("query", {}).get("search", [])

    for result in results:
        title = result.get("title", "")
        # Fetch image for this page
        params["titles"] = title
        resp = SESSION.get(WIKI_API, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if page_id == "-1":
                continue
            original = page.get("original", {})
            source = original.get("source")
            if source and is_valid_image(source):
                return source

    return None


def is_valid_image(url):
    """Check if the URL points to an actual plant image (not an icon/logo)."""
    url_lower = url.lower()
    # Must be an image file
    if not any(url_lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
        # Also check for URLs with parameters
        path = urllib.parse.urlparse(url_lower).path
        if not any(path.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            return False
    # Skip common non-plant images
    skip_patterns = ["icon", "logo", "flag", "map", "diagram", "chart", "symbol"]
    return not any(pat in url_lower for pat in skip_patterns)


def fetch_images(limit=None, skip_existing=True):
    """Fetch Wikipedia images for plants missing image URLs."""
    with app.app_context():
        query = Plant.query
        if skip_existing:
            query = query.filter(
                db.or_(Plant.image_url.is_(None), Plant.image_url == "")
            )

        plants = query.all()
        if limit:
            plants = plants[:limit]

        total = len(plants)
        found = 0
        not_found = 0
        errors = 0

        print(f"Fetching images for {total} plants...")

        for i, plant in enumerate(plants):
            # Try scientific name first (more specific), then common name
            image_url = None
            names_to_try = []
            if plant.scientific_name:
                names_to_try.append(plant.scientific_name)
            names_to_try.append(plant.name)

            for name in names_to_try:
                try:
                    image_url = search_wikipedia_image(name)
                    if image_url:
                        break
                except requests.exceptions.RequestException as e:
                    print(f"  Error searching for {name}: {e}")
                    errors += 1
                    time.sleep(2)
                    continue

            if image_url:
                plant.image_url = image_url
                found += 1
                if (i + 1) % 10 == 0 or i == 0:
                    print(f"  [{i+1}/{total}] {plant.name}: found image")
            else:
                not_found += 1
                if (i + 1) % 50 == 0:
                    print(f"  [{i+1}/{total}] {plant.name}: no image found")

            # Commit every 50 plants
            if (i + 1) % 50 == 0:
                db.session.commit()
                print(f"  Committed batch. Progress: {found} found, {not_found} not found, {errors} errors")

            # Be respectful of Wikipedia's API
            time.sleep(0.2)

        db.session.commit()

        print(f"\n---- Image Fetch Summary ----")
        print(f"Plants processed: {total}")
        print(f"Images found: {found}")
        print(f"Not found: {not_found}")
        print(f"Errors: {errors}")
        total_with_images = Plant.query.filter(
            Plant.image_url.isnot(None), Plant.image_url != ""
        ).count()
        print(f"Total plants with images: {total_with_images}/{Plant.query.count()}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch plant images from Wikipedia")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max number of plants to process")
    parser.add_argument("--all", action="store_true",
                        help="Re-fetch images for all plants, even those with existing URLs")
    args = parser.parse_args()

    fetch_images(limit=args.limit, skip_existing=not args.all)
    print("Done.")
