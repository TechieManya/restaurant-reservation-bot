"""Waitlist management for full time slots."""

import json
from pathlib import Path
from datetime import datetime

WAITLIST_PATH = Path(__file__).parent / "data" / "waitlist.json"


def load_waitlist():
    """Load waitlist from JSON."""
    if not WAITLIST_PATH.exists():
        return []
    with open(WAITLIST_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_waitlist(waitlist):
    """Save waitlist to JSON."""
    WAITLIST_PATH.parent.mkdir(exist_ok=True)
    with open(WAITLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(waitlist, f, indent=2)


def add_to_waitlist(name, party_size, date, time_slot, phone=None):
    """Add customer to waitlist. Returns waitlist entry with ID."""
    waitlist = load_waitlist()
    entry_id = f"W{len(waitlist) + 1000}"
    
    entry = {
        "id": entry_id,
        "name": name,
        "party": party_size,
        "date": date,
        "time": time_slot,
        "phone": phone,
        "added_at": datetime.now().isoformat(),
    }
    waitlist.append(entry)
    save_waitlist(waitlist)
    return entry


def get_waitlist_by_date_time(date, time_slot):
    """Get all waitlist entries for a specific date and time."""
    waitlist = load_waitlist()
    return [
        w for w in waitlist
        if w.get("date") == date and w.get("time") == time_slot
    ]


def get_all_waitlist():
    """Get all waitlist entries."""
    return load_waitlist()


def remove_from_waitlist(waitlist_id):
    """Remove entry from waitlist by ID. Returns True if found."""
    waitlist = load_waitlist()
    original_len = len(waitlist)
    waitlist = [w for w in waitlist if w.get("id") != waitlist_id]
    if len(waitlist) < original_len:
        save_waitlist(waitlist)
        return True
    return False


def get_waitlist_by_phone(phone):
    """Get waitlist entries for a phone number."""
    waitlist = load_waitlist()
    return [w for w in waitlist if w.get("phone") == phone]
