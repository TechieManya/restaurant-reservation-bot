"""User profile system - name, phone, preferences. Persisted in JSON."""

import json
import re
from pathlib import Path

PROFILES_PATH = Path(__file__).parent / "data" / "profiles.json"


def _normalize_phone(phone):
    """Normalize phone for consistent lookup (digits only)."""
    return re.sub(r"\D", "", str(phone)) if phone else ""


def load_profiles():
    """Load all profiles from JSON."""
    if not PROFILES_PATH.exists():
        return {}
    with open(PROFILES_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_profiles(profiles):
    """Save profiles to JSON."""
    with open(PROFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)


def get_by_phone(phone):
    """Get profile by phone. Returns None if not found."""
    key = _normalize_phone(phone)
    if not key:
        return None
    profiles = load_profiles()
    return profiles.get(key)


def save_or_update_profile(phone, name=None, preferences=None, favorite_dish=None):
    """Create or update profile. preferences: {veg, spicy, party_size}."""
    profiles = load_profiles()
    key = _normalize_phone(phone)
    if not key:
        return None
    existing = profiles.get(key, {})
    if name is not None:
        existing["name"] = name
    if "name" not in existing:
        existing["name"] = ""
    if preferences is not None:
        existing["preferences"] = {**existing.get("preferences", {}), **preferences}
    if favorite_dish is not None:
        existing["favorite_dish"] = favorite_dish
    existing["phone"] = phone
    profiles[key] = existing
    save_profiles(profiles)
    return existing


def get_usual_booking_text(profile):
    """Format 'Your usual X-person spicy veg booking?' from profile preferences."""
    prefs = profile.get("preferences", {})
    party = prefs.get("party_size", 2)
    veg = prefs.get("veg", "any")
    spicy = prefs.get("spicy", "any")
    veg_str = "veg" if veg == "veg" else "non-veg" if veg == "nonveg" else "mixed"
    spicy_str = spicy if spicy != "any" else "your preferred spice"
    return f"Your usual {party}-person {spicy_str} {veg_str} booking?"
