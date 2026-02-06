"""Create and manage reservations."""

import json
from pathlib import Path

RESERVATIONS_PATH = Path(__file__).parent / "data" / "reservations.json"


def load_reservations():
    """Load all reservations from JSON."""
    with open(RESERVATIONS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_reservations(reservations):
    """Save reservations to JSON."""
    with open(RESERVATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(reservations, f, indent=2)


def _generate_confirmation_id():
    """Generate unique confirmation ID e.g. R1023."""
    reservations = load_reservations()
    max_num = 1000
    for r in reservations:
        cid = r.get("id", "")
        if isinstance(cid, str) and cid.startswith("R"):
            try:
                n = int(cid[1:])
                max_num = max(max_num, n)
            except ValueError:
                pass
    return f"R{max_num + 1}"


def create_reservation(name, party_size, date, time_slot, phone=None):
    """Add a new reservation and return it with confirmation ID."""
    reservations = load_reservations()
    confirmation_id = _generate_confirmation_id()
    new_res = {
        "id": confirmation_id,
        "name": name,
        "party": party_size,
        "date": date,
        "time": time_slot
    }
    if phone:
        new_res["phone"] = phone
    reservations.append(new_res)
    save_reservations(reservations)
    return new_res


def get_by_id(confirmation_id):
    """Get reservation by confirmation ID. Returns None if not found."""
    reservations = load_reservations()
    for r in reservations:
        if r.get("id", "").upper() == confirmation_id.upper().strip():
            return r
    return None


def get_all_reservations():
    """Return all reservations (for history)."""
    return load_reservations()


def get_reservations_by_name(name):
    """Return reservations for a given name."""
    reservations = load_reservations()
    return [r for r in reservations if r.get("name", "").lower() == name.lower().strip()]


def cancel_by_id(confirmation_id):
    """Cancel reservation by confirmation ID. Returns True if found and cancelled."""
    reservations = load_reservations()
    original_len = len(reservations)
    reservations = [r for r in reservations if r.get("id", "").upper() != confirmation_id.upper().strip()]
    if len(reservations) < original_len:
        save_reservations(reservations)
        return True
    return False


def cancel_reservation(name, date):
    """Cancel reservation by name and date. Returns True if found and cancelled."""
    reservations = load_reservations()
    original_len = len(reservations)
    reservations = [r for r in reservations if not (r.get("name") == name and r.get("date") == date)]
    if len(reservations) < original_len:
        save_reservations(reservations)
        return True
    return False


def update_reservation(confirmation_id, **updates):
    """
    Update reservation by ID. Pass date=, time=, party=, name= as needed.
    Returns updated reservation or None if not found.
    """
    reservations = load_reservations()
    for r in reservations:
        if r.get("id", "").upper() == confirmation_id.upper().strip():
            if "date" in updates:
                r["date"] = updates["date"]
            if "time" in updates:
                r["time"] = updates["time"]
            if "party" in updates:
                r["party"] = updates["party"]
            if "name" in updates:
                r["name"] = updates["name"]
            save_reservations(reservations)
            return r
    return None


def get_reservations_for_slot(date, time_slot):
    """Count existing reservations for a given date/time (for capacity logic)."""
    reservations = load_reservations()
    return sum(
        1 for r in reservations
        if r.get("date") == date and r.get("time") == time_slot
    )


def get_booking_stats():
    """
    Analytics: total reservations, most booked time, most booked date,
    most common party size, popular dish (from profiles).
    """
    reservations = load_reservations()
    total = len(reservations)

    if not reservations:
        return {
            "total": 0,
            "most_booked_time": "N/A",
            "most_booked_date": "N/A",
            "most_common_party": "N/A",
            "popular_dish": "N/A"
        }

    time_counts = {}
    date_counts = {}
    party_counts = {}
    for r in reservations:
        t = r.get("time", "")
        time_counts[t] = time_counts.get(t, 0) + 1
        d = r.get("date", "")
        date_counts[d] = date_counts.get(d, 0) + 1
        p = r.get("party", 1)
        party_counts[p] = party_counts.get(p, 0) + 1

    most_time = max(time_counts, key=time_counts.get) if time_counts else "N/A"
    most_date = max(date_counts, key=date_counts.get) if date_counts else "N/A"
    most_party = max(party_counts, key=party_counts.get) if party_counts else "N/A"

    # Popular dish from profiles
    try:
        from profiles import load_profiles
        profiles = load_profiles()
        dish_counts = {}
        for p in profiles.values():
            fd = p.get("favorite_dish", "").strip()
            if fd:
                dish_counts[fd] = dish_counts.get(fd, 0) + 1
        popular_dish = max(dish_counts, key=dish_counts.get) if dish_counts else "No favorites set yet"
    except Exception:
        popular_dish = "N/A"

    return {
        "total": total,
        "most_booked_time": most_time,
        "most_booked_date": most_date,
        "most_common_party": most_party,
        "popular_dish": popular_dish
    }
