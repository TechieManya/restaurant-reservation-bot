"""Load and display compressed menu data."""

import json
from pathlib import Path

MENU_PATH = Path(__file__).parent / "data" / "menu.json"

# s = spice: 0=mild, 1=medium, 2=hot
SPICE_LABELS = {0: "mild", 1: "medium", 2: "hot"}


def load_menu():
    """Load menu from compressed JSON. Keys: n=name, c=category, p=price, v=vegetarian, s=spice."""
    with open(MENU_PATH, encoding="utf-8") as f:
        return json.load(f)


def display_menu():
    """Print menu in readable format."""
    data = load_menu()
    items = data.get("items", [])
    
    if not items:
        return "No menu items available."
    
    lines = ["\n--- Our Menu ---"]
    current_category = None
    
    for item in items:
        cat = item.get("c", "Other")
        if cat != current_category:
            current_category = cat
            lines.append(f"\n  {cat}:")
        
        name = item.get("n", "Unknown")
        price = item.get("p", 0)
        veg = " (V)" if item.get("v") else ""
        spice = item.get("s", 0)
        spice_str = f" [{SPICE_LABELS.get(spice, 'mild')}]" if spice > 0 else ""
        lines.append(f"    • {name} - ${price:.2f}{veg}{spice_str}")
    
    lines.append("")
    return "\n".join(lines)


def recommend_dishes(veg_pref, spicy_pref):
    """
    Recommend dishes based on veg preference and spicy level.
    veg_pref: "veg" or "nonveg" or "any"
    spicy_pref: "mild", "medium", "hot", or "any"
    Returns formatted string with suggestions.
    """
    data = load_menu()
    items = data.get("items", [])
    
    # Map user input to filter values
    want_veg = veg_pref.lower() in ["veg", "vegetarian", "v", "yes"]
    want_nonveg = veg_pref.lower() in ["nonveg", "non-veg", "nonveg", "meat", "n"]
    
    spicy_map = {"mild": 0, "medium": 1, "hot": 2, "any": -1}
    max_spice = spicy_map.get(spicy_pref.lower(), -1)
    
    matches = []
    for item in items:
        is_veg = item.get("v", False)
        spice = item.get("s", 0)
        
        # Filter by veg
        if want_veg and not is_veg:
            continue
        if want_nonveg and is_veg:
            continue
        
        # Filter by spice (user wants at most X, or any)
        if max_spice >= 0 and spice > max_spice:
            continue
        
        matches.append(item)
    
    if not matches:
        return "No dishes match your preferences. Try 'any' for veg or spice!"
    
    lines = ["\n--- Recommendations for you ---"]
    for item in matches[:5]:  # Top 5
        name = item.get("n", "Unknown")
        price = item.get("p", 0)
        veg = " (V)" if item.get("v") else ""
        spice_str = SPICE_LABELS.get(item.get("s", 0), "mild")
        lines.append(f"  • {name} - ${price:.2f}{veg} [{spice_str}]")
    lines.append("")
    return "\n".join(lines)
