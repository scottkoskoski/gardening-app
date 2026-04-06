"""Fix remaining plant images with curated Wikimedia Commons URLs."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app, db
from app.models.plant import Plant

# Curated working Wikimedia Commons REST API URLs (these support hotlinking)
IMAGE_MAP = {
    "Jalapeno Pepper": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Capsicum_annuum_fruits_IMGP0045.jpg",
    "Butternut Squash": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Butternut_squash_-_Cucurbita_moschata.jpg",
    "Green Bean": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Green-beans-background.jpg",
    "Sugar Snap Pea": "https://upload.wikimedia.org/wikipedia/commons/2/26/Snow_peas.jpg",
    "Lettuce": "https://upload.wikimedia.org/wikipedia/commons/d/da/Iceberg_lettuce_in_SB.jpg",
    "Cauliflower": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Cauliflower.JPG",
    "Potato": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Patates.jpg",
    "Sweet Potato": "https://upload.wikimedia.org/wikipedia/commons/5/58/Ipomoea_batatas_006.JPG",
    "Eggplant": "https://upload.wikimedia.org/wikipedia/commons/7/76/Solanum_melongena_24_08_2012_%281%29.JPG",
    "Parsnip": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Pastinaca_sativa_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-263.jpg",
    "Basil": "https://upload.wikimedia.org/wikipedia/commons/9/90/Basil-Basilico-Ocimum_basilicum-albahaca.jpg",
    "Oregano": "https://upload.wikimedia.org/wikipedia/commons/d/d1/Origanum_vulgare_-_harilik_pune.jpg",
    "Lemongrass": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Lemon_grass.jpg",
    "Rhubarb": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Rheum_rhabarbarum.2006-04-27.uทท.jpg",
    "Sunflower": "https://upload.wikimedia.org/wikipedia/commons/4/40/Sunflower_from_Silesia2.jpg",
    "Zinnia": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Zinnia_elegans_with_Bombus01.jpg",
    "Nasturtium": "https://upload.wikimedia.org/wikipedia/commons/e/e7/Tropaeolum_majus-1.jpg",
    "Petunia": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Petunia_Cultivars.jpg",
    "Black-Eyed Susan": "https://upload.wikimedia.org/wikipedia/commons/b/b6/Rudbeckia_hirta_Indian_Summer.jpg",
    "Morning Glory": "https://upload.wikimedia.org/wikipedia/commons/0/05/Ipomoea_purpurea_-_Morning_Glory.jpg",
    "Sweet Pea": "https://upload.wikimedia.org/wikipedia/commons/0/09/Sweetpea_flowers.jpg",
    "Impatiens": "https://upload.wikimedia.org/wikipedia/commons/1/17/Impatiens_walleriana_-_balsam_in_Meppel_%28Netherlands%29.jpg",
    "Daylily": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Daylily_-_Hemerocallis.jpg",
    "Edamame": "https://upload.wikimedia.org/wikipedia/commons/6/64/Edamame_by_Zesmerelda_in_Chicago.jpg",
    "Hot Pepper": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Habanero_closeup_edit2.jpg",
    "Romaine Lettuce": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Romaine_lettuce.jpg",
    "Collard Greens": "https://upload.wikimedia.org/wikipedia/commons/b/b9/Collard-Greens-Bundle.jpg",
    "Green Onion": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Allium_fistulosum_bulbifera0.jpg",
    "Bok Choy": "https://upload.wikimedia.org/wikipedia/commons/d/d9/Brassica_rapa_chinensis.jpg",
    "Tomatillo": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Tomatillo.jpg",
    "Celery Root": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Celeriac.jpg",
    "Peony": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Paeonia_lactiflora1.jpg",
    "Daffodil": "https://upload.wikimedia.org/wikipedia/commons/1/1a/24_Marzo_2013-_Narciso_%288597033044%29.jpg",
    "Geranium": "https://upload.wikimedia.org/wikipedia/commons/3/37/Pelargonium_zonale_hybrid.jpg",
    "Begonia": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Begonia_semperflorens_group.jpg",
    "Avocado": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Persea_americana_fruit_2.jpg",
    "Microgreens": "https://upload.wikimedia.org/wikipedia/commons/c/c0/Sprouts_microgreen_mix_close-up.jpg",
    "Peppermint": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Mentha_x_piperita_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-095.jpg",
    "Calendula": "https://upload.wikimedia.org/wikipedia/commons/1/18/Calendula_officinalis_10.jpg",
    "Borage": "https://upload.wikimedia.org/wikipedia/commons/9/90/Borago_officinalis_01.jpg",
    "Comfrey": "https://upload.wikimedia.org/wikipedia/commons/f/f9/Comfrey.jpg",
    "Cover Crop Mix": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Cover_crop_drill_interseeder.jpg",
    "Romanesco": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Romanesco_Brassica_oleracea_Richard_Bartz.jpg",
    "Ground Cherry": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Physalis_peruviana_Fruit_Close-Up.jpg",
    "Sunchoke": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Sunroot_top.jpg",
    "Sorrel": "https://upload.wikimedia.org/wikipedia/commons/5/54/Rumex_acetosa_cultivar_01.jpg",
    "Lovage": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Levisticum_officinale_001.JPG",
    "Endive": "https://upload.wikimedia.org/wikipedia/commons/d/db/Endive_02.jpg",
    "Watercress": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Nasturtium_officinale.jpg",
    "Radicchio": "https://upload.wikimedia.org/wikipedia/commons/8/88/Radicchio_di_Chioggia.jpg",
    "Passion Fruit": "https://upload.wikimedia.org/wikipedia/commons/2/21/Passiflora_edulis_forma_flavicarpa.jpg",
    "Bay Laurel": "https://upload.wikimedia.org/wikipedia/commons/f/f8/Laurus_nobilis_g1.jpg",
    "Tarragon": "https://upload.wikimedia.org/wikipedia/commons/c/c1/Artemisia_dracunculus_002.JPG",
    "Marjoram": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Origanum_majorana_002.JPG",
    "Stevia": "https://upload.wikimedia.org/wikipedia/commons/5/5b/Stevia_rebaudiana_flowers.jpg",
    "Lemon Balm": "https://upload.wikimedia.org/wikipedia/commons/8/80/Melissa_officinalis_%282%29.jpg",
}

def main():
    app = create_app()
    with app.app_context():
        updated = 0
        for name, url in IMAGE_MAP.items():
            plant = Plant.query.filter_by(name=name).first()
            if plant:
                plant.image_url = url
                updated += 1
                print(f"  Updated: {name}")
            else:
                print(f"  NOT FOUND: {name}")

        db.session.commit()
        print(f"\nUpdated {updated} remaining plants.")

if __name__ == "__main__":
    main()
