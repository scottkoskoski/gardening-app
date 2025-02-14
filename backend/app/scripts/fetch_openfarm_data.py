import requests
from app import create_app
from app.models.database import db
from app.models.plant import Plant

app = create_app()

OPENFARM_API_URL = "https://openfarm.cc/api/v1/crops"

# List of plant names to search in API 
PLANT_NAMES = [
    # Vegetables
    "Tomato", "Carrot", "Lettuce", "Cucumber", "Bell Pepper", "Zucchini", "Spinach",
    "Kale", "Broccoli", "Cauliflower", "Cabbage", "Radish", "Turnip", "Beet", "Celery",
    "Brussels Sprouts", "Sweet Corn", "Pumpkin", "Squash", "Butternut Squash", "Acorn Squash",
    "Spaghetti Squash", "Green Beans", "Peas", "Eggplant", "Okra", "Swiss Chard",
    "Collard Greens", "Leek", "Scallions", "Onion", "Garlic", "Shallot", "Fennel", "Artichoke",
    "Asparagus", "Rutabaga", "Parsnip", "Bok Choy", "Mustard Greens",

    # Fruits
    "Strawberry", "Raspberry", "Blueberry", "Blackberry", "Gooseberry", "Elderberry",
    "Grape", "Apple", "Pear", "Peach", "Plum", "Cherry", "Fig", "Pomegranate", "Pawpaw",
    "Kiwi", "Mulberry", "Persimmon", "Quince", "Apricot", "Nectarine", "Melon", "Cantaloupe",
    "Watermelon", "Honeydew", "Banana", "Lemon", "Lime", "Orange", "Grapefruit", "Avocado",
    "Olive",

    # Herbs
    "Basil", "Cilantro", "Parsley", "Dill", "Thyme", "Oregano", "Rosemary", "Sage",
    "Mint", "Chives", "Tarragon", "Lavender", "Chamomile", "Lemongrass", "Fennel",
    "Marjoram", "Bay Laurel", "Stevia",

    # Flowers (Common in Home Gardens)
    "Sunflower", "Marigold", "Zinnia", "Petunia", "Daisy", "Cosmos", "Snapdragon",
    "Pansy", "Begonia", "Impatiens", "Salvia", "Alyssum", "Viola", "Columbine",
    "Lupine", "Hollyhock", "Echinacea", "Lavender", "Rudbeckia", "Coreopsis",
    "Phlox", "Delphinium", "Foxglove", "Lantana", "Verbena", "Dianthus",
    "Sweet Pea", "Nasturtium", "Morning Glory", "Chrysanthemum", "Dahlia",
    "Peony", "Hydrangea", "Lilac", "Rose", "Tulip", "Daffodil", "Crocus",
    "Hyacinth", "Iris", "Hosta", "Daylily", "Astilbe", "Hibiscus",

    # Bonus - Less Common Edible Crops
    "Rhubarb", "Horseradish", "Sunchoke", "Jicama", "Tamarillo", "Loquat",
    "Dragon Fruit", "Passionfruit", "Curry Leaf", "Fenugreek", "Epazote",
    "Wasabi", "Cardoon", "Chayote", "Sea Buckthorn", "Pineberry", "Tomatillo"
]


def fetch_openfarm_data():
    """Fetches plant data from OpenFarm API and updates the database."""
    with app.app_context():
        for plant_name in PLANT_NAMES:
            print(f"Fetching data for {plant_name}...")

            response = requests.get(f"{OPENFARM_API_URL}/?filter={plant_name}")

            if response.status_code != 200:
                print(f"Failed to fetch data for {plant_name}. Status: {response.status_code}")
                continue

            data = response.json()
            crops = data.get("data", [])

            if not crops:
                print(f"No data found for {plant_name}.")
                continue

            for crop in crops:
                attributes = crop.get("attributes", {})

                # Extract relevant attributes
                name = attributes.get("name")
                scientific_name = attributes.get("scientific_name")
                sunlight = attributes.get("sun_requirements")
                sowing_method = attributes.get("sowing_method")
                spread = attributes.get("spread")
                row_spacing = attributes.get("row_spacing")
                height = attributes.get("height")
                description = attributes.get("description")
                image_url = attributes.get("main_image_path")

                # Check if plant already exists in database
                existing_plant = Plant.query.filter_by(name=name).first()
                if existing_plant:
                    print(f"Skipping {name}. Plant already exists in database.")
                    continue

                # Create new plant entry
                new_plant = Plant(
                    name=name,
                    scientific_name=scientific_name,
                    sunlight=sunlight,
                    sowing_method=sowing_method,
                    spread=spread,
                    row_spacing=row_spacing,
                    height=height,
                    description=description,
                    image_url=image_url
                )

                db.session.add(new_plant)
                print(f"Added {name} to the database.")

        # Commit changes after processing all plants
        db.session.commit()
        print("Finished fetching OpenFarm plant data.")

if __name__ == "__main__":
    fetch_openfarm_data()
    print("Data fetch completed.")
