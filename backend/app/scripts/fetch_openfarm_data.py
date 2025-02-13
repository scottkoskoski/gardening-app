import requests
import string
from app import create_app
from app.models.database import db
from app.models.plant import Plant

app = create_app()

OPENFARM_API_URL = "https://openfarm.cc/api/v1/crops"

def fetch_openfarm_data():
    """Fetches plant data from the OpenFarm API and updates the database."""
    
    with app.app_context():
        for letter in string.ascii_lowercase: # Loop through the alphabet
            print(f"Fetching plants starting with letter '{letter}'...")
            response = requests.get(f"{OPENFARM_API_URL}?filter={letter}")
            
            if response.status_code != 200:
                print(f"Failed to fetch data for filter {letter}. Status: {response.status_code}")
                continue # Skips to the next letter
            
            data = response.json()
            crops = data.get("data", [])
            
            if not crops:
                print(f"No crops found for filter {letter}.")
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
                new_plant = Plant(name=name,
                                  scientific_name=scientific_name,
                                  sunlight=sunlight,
                                  sowing_method=sowing_method,
                                  spread=spread,
                                  row_spacing=row_spacing,
                                  height=height,
                                  description=description,
                                  image_url=image_url)

                db.session.add(new_plant)
                print(f"Added {name} to the database.")
            
            # Commit changes after each letter's batch
            db.session.commit()
            print(f"Finished fetching plants starting with letter '{letter}'.")

if __name__ == "__main__":
    fetch_openfarm_data()
    print("Data fetch completed.")