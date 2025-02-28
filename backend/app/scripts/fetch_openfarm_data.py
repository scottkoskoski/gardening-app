import requests
import re
from app import create_app
from app.models.database import db
from app.models.plant import Plant, PlantSchema

app = create_app()

OPENFARM_API_URL = "https://openfarm.cc/api/v1/crops"

# Creating an instance of PlantSchema for validation
plant_schema = PlantSchema()

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
        # Tracking statistics
        total_fetched = 0
        total_added = 0
        total_skipped_existing = 0
        total_skipped_validation = 0
        total_errors = 0
        
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
            
            total_fetched += len(crops)

            for crop in crops:
                attributes = crop.get("attributes", {})

                # Extract relevant attributes
                name = attributes.get("name")
                if not name:
                    print(f"Skipping unnamed crop for {plant_name}")
                    total_skipped_validation += 1
                    continue
                
                # Sanitizing name to match characters allowed by schema
                sanitized_name = re.sub(r"[^a-zA-Z0-9 '\-]", "", name)
                if sanitized_name != name:
                    print(f"Sanitized name from '{name}' to '{sanitized_name}'")
                    name = sanitized_name
                
                # Check if plant already exists in database
                existing_plant = Plant.query.filter_by(name=name).first()
                if existing_plant:
                    print(f"Skipping {name}. Plant already exists in database.")
                    total_skipped_existing += 1
                    continue
                
                # Preparing plant data
                plant_data = {
                    "name": name,
                    "scientific_name": attributes.get("scientific_name"),
                    "sunlight": attributes.get("sun_requirements"),
                    "sowing_method": attributes.get("sowing_method"),
                    "description": attributes.get("description")
                }
                
                # Handling numeric values
                try:
                    if attributes.get("spread") is not None:
                        plant_data["spread"] = float(attributes.get("spread"))
                    if attributes.get("row_spacing") is not None:
                        plant_data["row_spacing"] = float(attributes.get("row_spacing"))
                    if attributes.get("height") is not None:
                        plant_data["height"] = float(attributes.get("height"))
                except (ValueError, TypeError):
                    print(f"Warning: Numeric conversion issue for {name}")
                
                # Handling image URL to make sure it's not too long
                image_url = attributes.get("main_image_path")
                if image_url and len(image_url) <= 255:
                    plant_data["image_url"] = image_url
                elif image_url:
                    print(f"Warning: Image URL for {name} exceeds 255 characters, truncating")
                    plant_data["image_url"] = image_url[:255]
                
                # Ensuring required boolean fields are present with defaults
                plant_data["requires_greenhouse"] = False
                plant_data["suitable_for_containers"] = False
                
                # Validating growing_season, water_needs, and space_required to match allowed values
                if "growing_season" in plant_data and plant_data["growing_season"] not in ["Spring", "Summer", "Fall", "Winter", None]:
                    print(f"Warning: Invalid growing_season for {name}, setting to null")
                    plant_data["growing_season"] = None
                
                if "water_needs" in plant_data and plant_data["water_needs"] not in ["Low", "Medium", "High", None]:
                    print(f"Warning: Invalid water_needs for {name}, setting to null")
                    plant_data["water_needs"] = None

                if "space_required" in plant_data and plant_data["space_required"] not in ["Small", "Medium", "Large", None]:
                    print(f"Warning: Invalid space_required for {name}, setting to null")
                    plant_data["space_required"] = None
                    
                # Ensure sunlight values match schema's allowed options
                if plant_data.get("sunlight") not in ["Full Sun", "Partial Sun", "Partial Shade", "Full Shade", None]:
                    print(f"Warning: Invalid sunlight value for {name}, setting to null")
                    plant_data["sunlight"] = None               
                
                # Validating data using schema
                errors = plant_schema.validate(plant_data)
                if errors:
                    print(f"Validation failed for {name}: {errors}")
                    total_skipped_validation += 1
                    continue
                
                try:
                    new_plant = Plant(**plant_data)
                    db.session.add(new_plant)
                    print(f"Added {name} to the database.")
                    total_added += 1
                except Exception as e:
                    print(f"Error processing {plant_name}: {str(e)}")
                    total_errors += 1
                    continue
                
        # Committing after processing all plants
        try:
            db.session.commit()
            print("\n---- Import Summary ----")
            print(f"Total plants fetched: {total_fetched}")
            print(f"Total plants added: {total_added}")
            print(f"Total plants skipped (already exist): {total_skipped_existing}")
            print(f"Total plants skipped (validation failed): {total_skipped_validation}")
            print(f"Total errors encountered: {total_errors}")
            print("Finished fetching OpenFarm plant data.")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing changes to database: {str(e)}")
            print("All changes have been rolled back.")
                    
if __name__ == "__main__":
    fetch_openfarm_data()
    print("Data fetch completed.")
