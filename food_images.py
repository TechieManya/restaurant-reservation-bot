"""Download and manage real food images."""

import requests
from pathlib import Path
from PIL import Image
import io

IMAGES_DIR = Path(__file__).parent / "data" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def get_food_image_url(dish_name, category):
    """Get food image URL based on dish name and category."""
    # Map categories to Foodish API categories
    category_map = {
        "Pizza": "pizza",
        "Starter": "salad",
        "Main": "pasta",
        "Dessert": "dessert",
    }
    
    # Map specific dishes to Foodish categories
    dish_map = {
        "pizza": "pizza",
        "salad": "salad",
        "pasta": "pasta",
        "burger": "burger",
        "sushi": "sushi",
        "soup": "soup",
        "dessert": "dessert",
        "cake": "dessert",
        "ice cream": "dessert",
        "tiramisu": "dessert",
        "chicken": "burger",
        "salmon": "sushi",
        "wings": "burger",
        "bread": "burger",
    }
    
    # Check dish name first
    dish_lower = dish_name.lower()
    for key, value in dish_map.items():
        if key in dish_lower:
            return f"https://foodish-api.herokuapp.com/images/{value}/{value}{hash(dish_name) % 10 + 1}.jpg"
    
    # Fall back to category
    foodish_cat = category_map.get(category, "pizza")
    return f"https://foodish-api.herokuapp.com/images/{foodish_cat}/{foodish_cat}{hash(dish_name) % 10 + 1}.jpg"


def download_food_image(dish_name, category, size=(200, 200)):
    """Download food image from Foodish API or use Unsplash Source."""
    # Try Foodish first
    try:
        url = get_food_image_url(dish_name, category)
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            img = img.resize(size, Image.Resampling.LANCZOS)
            return img
    except Exception:
        pass
    
    # Fallback to Unsplash Source (no auth needed)
    try:
        # Map to search terms
        search_terms = {
            "Pizza": "pizza",
            "Starter": "salad",
            "Main": "pasta",
            "Dessert": "dessert",
        }
        term = search_terms.get(category, "food")
        # Unsplash Source API - random image by keyword
        url = f"https://source.unsplash.com/200x200/?{term}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            img = img.resize(size, Image.Resampling.LANCZOS)
            return img
    except Exception:
        pass
    
    # Final fallback - return None, will use placeholder
    return None


def get_food_image(dish_name, category, size=(200, 200)):
    """Get food image, downloading if needed or using cached version."""
    # Create cache filename
    cache_name = f"{dish_name.replace(' ', '_').lower()}_{category.lower()}.png"
    cache_path = IMAGES_DIR / cache_name
    
    # Return cached if exists
    if cache_path.exists():
        try:
            img = Image.open(cache_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return img
        except Exception:
            pass
    
    # Download new image
    img = download_food_image(dish_name, category, size)
    if img:
        try:
            img.save(cache_path, "PNG")
        except Exception:
            pass
        return img
    
    return None
