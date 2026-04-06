"""
Fix plant images by fetching working URLs from Wikipedia REST API
and Perenual API as fallback.
"""
import sys
import os
import time
import urllib.request
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app, db
from app.models.plant import Plant

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
PERENUAL_API = "https://perenual.com/api/v2/species-list"
PERENUAL_KEY = os.getenv("PERENUAL_API_KEY", "")

# Manual overrides for plants that won't match Wikipedia well
WIKI_TITLE_MAP = {
    "Cherry Tomato": "Cherry_tomato",
    "Bell Pepper": "Bell_pepper",
    "Jalapeno Pepper": "Jalapeño",
    "Sugar Snap Pea": "Snap_pea",
    "Swiss Chard": "Chard",
    "Brussels Sprouts": "Brussels_sprout",
    "Green Bean": "Green_bean",
    "Sweet Potato": "Sweet_potato",
    "Hot Pepper": "Capsicum_chinense",
    "Romaine Lettuce": "Romaine_lettuce",
    "Collard Greens": "Collard_greens",
    "Green Onion": "Scallion",
    "Bok Choy": "Bok_choy",
    "Winter Squash": "Winter_squash",
    "Celery Root": "Celeriac",
    "Butternut Squash": "Butternut_squash",
    "Black-Eyed Susan": "Rudbeckia_hirta",
    "Morning Glory": "Ipomoea_purpurea",
    "Sweet Pea": "Sweet_pea",
    "Cover Crop Mix": "Cover_crop",
    "Ground Cherry": "Physalis_pruinosa",
    "Passion Fruit": "Passionfruit",
    "Bay Laurel": "Laurus_nobilis",
    "Lemon Balm": "Lemon_balm",
    "Snap Pea": "Snap_pea",
    "Microgreens": "Microgreen",
}

def fetch_wiki_image(plant_name, scientific_name):
    """Try Wikipedia REST API to get a working thumbnail URL."""
    titles_to_try = []

    # Use manual mapping first
    if plant_name in WIKI_TITLE_MAP:
        titles_to_try.append(WIKI_TITLE_MAP[plant_name])

    # Try common name
    titles_to_try.append(plant_name.replace(" ", "_"))

    # Try scientific name (genus species)
    if scientific_name:
        titles_to_try.append(scientific_name.split(" ")[0])  # Just genus
        titles_to_try.append(scientific_name.replace(" ", "_"))

    for title in titles_to_try:
        try:
            url = f"{WIKI_API}{title}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "GardeningApp/1.0 (educational project)"
            })
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode())

            # Get the thumbnail or original image
            if "thumbnail" in data and "source" in data["thumbnail"]:
                img_url = data["thumbnail"]["source"]
                # Get a larger version by modifying the width
                img_url = img_url.replace("/50px-", "/600px-").replace("/60px-", "/600px-").replace("/80px-", "/600px-").replace("/100px-", "/600px-").replace("/120px-", "/600px-").replace("/160px-", "/600px-").replace("/200px-", "/600px-").replace("/220px-", "/600px-").replace("/240px-", "/600px-").replace("/280px-", "/600px-").replace("/300px-", "/600px-").replace("/320px-", "/600px-")
                # Also try replacing smaller widths generically
                import re
                img_url = re.sub(r'/\d+px-', '/600px-', img_url)
                return img_url

            if "originalimage" in data and "source" in data["originalimage"]:
                return data["originalimage"]["source"]

        except Exception as e:
            continue

    return None


def fetch_perenual_image(plant_name):
    """Try Perenual API as fallback."""
    if not PERENUAL_KEY:
        return None
    try:
        url = f"{PERENUAL_API}?key={PERENUAL_KEY}&q={urllib.parse.quote(plant_name)}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "GardeningApp/1.0"
        })
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())

        if data.get("data") and len(data["data"]) > 0:
            plant_data = data["data"][0]
            img = plant_data.get("default_image", {})
            if img and img.get("regular_url"):
                return img["regular_url"]
            if img and img.get("medium_url"):
                return img["medium_url"]
            if img and img.get("original_url"):
                return img["original_url"]
    except Exception as e:
        pass
    return None


def verify_url(url):
    """Verify a URL is accessible."""
    try:
        req = urllib.request.Request(url, method='HEAD', headers={
            "User-Agent": "GardeningApp/1.0 (educational project)"
        })
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status == 200
    except:
        # Try GET if HEAD fails
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "GardeningApp/1.0 (educational project)"
            })
            resp = urllib.request.urlopen(req, timeout=5)
            # Read a small amount to verify
            resp.read(1024)
            return True
        except:
            return False


def main():
    import urllib.parse

    app = create_app()
    with app.app_context():
        plants = Plant.query.order_by(Plant.id).all()
        total = len(plants)
        updated = 0
        failed = []

        print(f"Updating images for {total} plants...")

        for i, plant in enumerate(plants):
            print(f"[{i+1}/{total}] {plant.name}...", end=" ", flush=True)

            # Try Wikipedia first
            img_url = fetch_wiki_image(plant.name, plant.scientific_name)

            if img_url and verify_url(img_url):
                plant.image_url = img_url
                updated += 1
                print(f"OK (Wikipedia)")
            else:
                # Try Perenual as fallback
                img_url = fetch_perenual_image(plant.name)
                if img_url and verify_url(img_url):
                    plant.image_url = img_url
                    updated += 1
                    print(f"OK (Perenual)")
                else:
                    failed.append(plant.name)
                    print(f"FAILED")

            # Rate limiting
            time.sleep(0.3)

        db.session.commit()
        print(f"\nDone! Updated {updated}/{total} plants.")
        if failed:
            print(f"Failed to find images for: {', '.join(failed)}")


if __name__ == "__main__":
    main()
