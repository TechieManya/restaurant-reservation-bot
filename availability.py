"""Load and query availability schedule."""

import json
import re
from pathlib import Path
from datetime import datetime, date

AVAILABILITY_PATH = Path(__file__).parent / "data" / "availability.json"

# Default slots when date not in availability.json - use for any date
DEFAULT_SLOTS = {"18:00": 10, "19:00": 10, "20:00": 10, "21:00": 10}


def load_availability():
    """Load availability schedule. Format: {date: {time: capacity}}."""
    with open(AVAILABILITY_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_date_slots(date_str):
    """Get time slots for a date. Uses availability.json if present, else default slots."""
    data = load_availability()
    return data.get(date_str, DEFAULT_SLOTS.copy())


def get_available_slots(date_str, party_size):
    """
    Return list of time slots available for given date and party size.
    Accepts any valid YYYY-MM-DD date - uses default slots if not in data.
    """
    date_data = get_date_slots(date_str)
    
    slots = []
    for time_slot, capacity in date_data.items():
        if capacity >= party_size:
            slots.append(time_slot)
    
    return sorted(slots)


def is_date_valid(date_str):
    """Check if string is a valid YYYY-MM-DD date. Accepts any date."""
    if not date_str or len(date_str) != 10:
        return False
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_available_dates():
    """Return list of dates from availability data (for display)."""
    data = load_availability()
    return sorted(data.keys())


def get_slots_for_date(date_str):
    """
    Return all available time slots for a date (any capacity).
    For 'slots' command - shows booking options.
    Accepts 'today' for current date.
    """
    if date_str.lower().strip() == "today":
        date_str = date.today().strftime("%Y-%m-%d")
    return get_available_slots(date_str, party_size=1)


def get_today_str():
    """Return today's date as YYYY-MM-DD."""
    return date.today().strftime("%Y-%m-%d")
