"""Conversation flow and intent handling."""

from menu import display_menu, recommend_dishes
from availability import (
    get_available_slots, is_date_valid, get_slots_for_date,
    get_today_str
)
from reservation import (
    create_reservation, cancel_by_id,
    get_by_id, get_all_reservations, update_reservation,
    get_booking_stats
)
from profiles import get_by_phone, save_or_update_profile, get_usual_booking_text


def detect_intent(text):
    """Detect user intent from input."""
    t = text.lower().strip()
    if not t:
        return None
    if any(w in t for w in ["book", "reserve", "table"]):
        return "book"
    if any(w in t for w in ["menu", "food", "eat"]):
        return "menu"
    if any(w in t for w in ["recommend", "suggest", "recommendation"]):
        return "recommend"
    if any(w in t for w in ["history", "bookings", "reservations"]):
        return "history"
    if any(w in t for w in ["modify", "change", "update"]):
        return "modify"
    if any(w in t for w in ["cancel"]):
        return "cancel"
    if any(w in t for w in ["slots", "availability", "times"]):
        return "slots"
    if any(w in t for w in ["stats", "statistics", "analytics"]):
        return "stats"
    if any(w in t for w in ["help", "?"]):
        return "help"
    if any(w in t for w in ["quit", "exit", "bye"]):
        return "quit"
    return None


def get_help_message():
    """Return help text."""
    return """
--- Commands ---
  book / reserve   - Book a table
  menu             - View our menu
  recommend        - Get dish recommendations (veg + spicy preference)
  history          - View all reservations
  slots            - Show available booking times for a date
  stats            - Booking statistics
  modify           - Change a booking (using confirmation ID)
  cancel           - Cancel a reservation (using confirmation ID)
  help             - Show this message
  quit / exit      - Exit the bot
"""


def handle_book(state):
    """Handle booking flow with user profile (Welcome back)."""
    step = state.get("step", 0)
    
    # Step 0: Ask phone
    if step == 0:
        state["step"] = 1
        return "Phone number? (or 'skip' for guest booking)", state
    
    # Step 1: Process phone - check profile or skip
    if step == 1:
        inp = state.get("last_input", "").strip()
        if inp.lower() == "skip":
            state["phone"] = None
            state["step"] = 2
            return "How many people? (1-10)", state
        state["phone"] = inp
        profile = get_by_phone(inp)
        if profile and profile.get("name"):
            state["profile"] = profile
            state["step"] = 1
            state["book_phase"] = "usual"
            usual = get_usual_booking_text(profile)
            name = profile.get("name", "there")
            return f"Welcome back {name}!\n{usual}\n(yes / no)", state
        state["step"] = 2
        return "How many people? (1-10)", state
    
    # Step 1 with phase "usual" - yes/no for usual booking
    if step == 1 and state.get("book_phase") == "usual":
        inp = state.get("last_input", "").lower().strip()
        if inp == "yes":
            prefs = state.get("profile", {}).get("preferences", {})
            state["party_size"] = prefs.get("party_size", 2)
            state.pop("book_phase", None)
            state["step"] = 3
            return "Which date? (YYYY-MM-DD or 'today')", state
        state.pop("book_phase", None)
        state.pop("profile", None)
        state["step"] = 2
        return "How many people? (1-10)", state
    
    # Step 2: Party size
    if step == 2:
        try:
            n = int(state.get("last_input", "0"))
            if 1 <= n <= 10:
                state["party_size"] = n
                state["step"] = 3
                return "Which date? (YYYY-MM-DD or 'today')", state
        except ValueError:
            pass
        return "Please enter a number between 1 and 10.", state
    
    # Step 3: Date
    if step == 3:
        date_str = state.get("last_input", "").strip()
        if date_str.lower() == "today":
            date_str = get_today_str()
        if is_date_valid(date_str):
            state["date"] = date_str
            state["step"] = 4
            slots = get_available_slots(date_str, state["party_size"])
            if not slots:
                state["step"] = 0
                return "Sorry, no slots available for that date/party size.", state
            return f"Available slots: {', '.join(slots)}. Pick one:", state
        return "Invalid date. Use YYYY-MM-DD (e.g. 2025-02-10) or 'today'", state
    
    # Step 4: Time
    if step == 4:
        time_slot = state.get("last_input", "").strip()
        slots = get_available_slots(state["date"], state["party_size"])
        if time_slot in slots:
            state["time"] = time_slot
            state["step"] = 5
            return "Name for the reservation?", state
        return f"Please pick from: {', '.join(slots)}", state
    
    # Step 5: Name
    if step == 5:
        name = state.get("last_input", "").strip()
        if name:
            state["name"] = name
            if state.get("phone"):
                state["step"] = 6
                return "Favorite dish from our menu? (optional - type name or 'skip')", state
            # No phone - go straight to create
            phone = state.get("phone")
            res = create_reservation(
                name, state["party_size"], state["date"], state["time"],
                phone=phone
            )
            state["step"] = 0
            state.pop("party_size", None)
            state.pop("date", None)
            state.pop("time", None)
            state.pop("phone", None)
            state.pop("profile", None)
            msg = (
                f"Booking confirmed!\n"
                f"Reservation ID: {res['id']}\n"
                f"✓ {res['party']} people on {res['date']} at {res['time']} under {res['name']}.\n"
                f"Save your ID to modify or cancel later."
            )
            return msg, state
        return "Please enter a name.", state
    
    # Step 6: Favorite dish (optional) + create
    if step == 6:
        fav = state.get("last_input", "").strip()
        if fav and fav.lower() != "skip":
            save_or_update_profile(state.get("phone"), favorite_dish=fav)
        name = state.get("name", "")
        phone = state.get("phone")
        res = create_reservation(
            name, state["party_size"], state["date"], state["time"],
            phone=phone
        )
        save_or_update_profile(phone, name=name, preferences={"party_size": state["party_size"]})
        state["step"] = 0
        state.pop("party_size", None)
        state.pop("date", None)
        state.pop("time", None)
        state.pop("name", None)
        state.pop("phone", None)
        state.pop("profile", None)
        msg = (
            f"Booking confirmed!\n"
            f"Reservation ID: {res['id']}\n"
            f"✓ {res['party']} people on {res['date']} at {res['time']} under {res['name']}.\n"
            f"Save your ID to modify or cancel later."
        )
        return msg, state
    
    return "Something went wrong.", state


def handle_cancel(state):
    """Handle cancellation by confirmation ID."""
    step = state.get("cancel_step", 0)
    
    if step == 0:
        state["cancel_step"] = 1
        return "Enter your confirmation ID (e.g. R1023):", state
    
    if step == 1:
        cid = state.get("last_input", "").strip()
        if cancel_by_id(cid):
            state["cancel_step"] = 0
            return "Reservation cancelled.", state
        state["cancel_step"] = 0
        return "No reservation found with that ID. Check and try again.", state
    
    return "Something went wrong.", state


def handle_history(state):
    """Show reservation history."""
    step = state.get("history_step", 0)
    
    if step == 0:
        state["history_step"] = 1
        return "Show all reservations or by name? (all / name):", state
    
    if step == 1:
        choice = state.get("last_input", "").lower().strip()
        if choice == "name":
            state["history_step"] = 2
            return "Enter name:", state
        # "all" or anything else -> show all
        state["history_step"] = 0
        reservations = get_all_reservations()
        if not reservations:
            return "No reservations found.", state
        lines = ["\n--- Reservation History ---"]
        for r in reservations:
            cid = r.get("id", "-")
            lines.append(f"  {cid} | {r.get('name', '?')} | {r.get('party', '?')} pax | {r.get('date', '?')} @ {r.get('time', '?')}")
        lines.append("")
        return "\n".join(lines), state
    
    if step == 2:
        name = state.get("last_input", "").strip()
        state["history_step"] = 0
        reservations = [r for r in get_all_reservations() if r.get("name", "").lower() == name.lower()]
        if not reservations:
            return f"No reservations found for '{name}'.", state
        lines = [f"\n--- Reservations for {name} ---"]
        for r in reservations:
            cid = r.get("id", "-")
            lines.append(f"  {cid} | {r.get('party', '?')} pax | {r.get('date', '?')} @ {r.get('time', '?')}")
        lines.append("")
        return "\n".join(lines), state
    
    return "Something went wrong.", state


def handle_recommend(state):
    """Recommend dishes based on veg and spicy preference."""
    step = state.get("rec_step", 0)
    
    if step == 0:
        state["rec_step"] = 1
        return "Veg or non-veg? (veg / nonveg / any):", state
    
    if step == 1:
        state["rec_veg"] = state.get("last_input", "").strip() or "any"
        state["rec_step"] = 2
        return "Spicy preference? (mild / medium / hot / any):", state
    
    if step == 2:
        veg = state.get("rec_veg", "any")
        spicy = state.get("last_input", "").strip() or "any"
        state["rec_veg"] = veg
        state["rec_spicy"] = spicy
        state["rec_step"] = 3
        result = recommend_dishes(veg, spicy)
        return result + "\nSave these preferences for next time? (phone or 'skip')", state
    
    if step == 3:
        inp = state.get("last_input", "").strip()
        veg = state.get("rec_veg", "any")
        spicy = state.get("rec_spicy", "any")
        state["rec_step"] = 0
        state.pop("rec_veg", None)
        state.pop("rec_spicy", None)
        if inp and inp.lower() != "skip":
            save_or_update_profile(inp, preferences={"veg": veg, "spicy": spicy})
            return "Preferences saved! We'll remember for your next booking.", state
        return "Got it. Type 'book' when you're ready to reserve.", state
    
    return "Something went wrong.", state


def handle_modify(state):
    """Modify reservation by confirmation ID."""
    step = state.get("modify_step", 0)
    
    if step == 0:
        state["modify_step"] = 1
        return "Enter your confirmation ID (e.g. R1023):", state
    
    if step == 1:
        cid = state.get("last_input", "").strip()
        res = get_by_id(cid)
        if not res:
            state["modify_step"] = 0
            return "No reservation found with that ID.", state
        state["modify_id"] = cid
        state["modify_step"] = 2
        return f"Found: {res['party']} pax on {res['date']} at {res['time']}. What to change? (date / time / party / name):", state
    
    if step == 2:
        field = state.get("last_input", "").lower().strip()
        if field not in ["date", "time", "party", "name"]:
            return "Choose: date, time, party, or name:", state
        state["modify_field"] = field
        state["modify_step"] = 3
        if field == "date":
            return "New date (YYYY-MM-DD):", state
        if field == "time":
            res = get_by_id(state["modify_id"])
            slots = get_available_slots(res["date"], res["party"])
            return f"New time. Available: {', '.join(slots)}:", state
        if field == "party":
            return "New party size (1-10):", state
        if field == "name":
            return "New name:", state
        return "Choose: date, time, party, or name:", state
    
    if step == 3:
        field = state.get("modify_field", "")
        val = state.get("last_input", "").strip()
        cid = state.get("modify_id", "")
        updates = {}
        
        if field == "date":
            if not is_date_valid(val):
                return "Invalid date. Use YYYY-MM-DD:", state
            updates["date"] = val
        elif field == "time":
            res = get_by_id(cid)
            slots = get_available_slots(res["date"], res["party"])
            if val not in slots:
                return f"Pick from: {', '.join(slots)}:", state
            updates["time"] = val
        elif field == "party":
            try:
                n = int(val)
                if 1 <= n <= 10:
                    updates["party"] = n
                else:
                    return "Enter 1-10:", state
            except ValueError:
                return "Enter a number 1-10:", state
        elif field == "name":
            if val:
                updates["name"] = val
            else:
                return "Enter a name:", state
        
        updated = update_reservation(cid, **updates)
        state["modify_step"] = 0
        state.pop("modify_id", None)
        state.pop("modify_field", None)
        if updated:
            return f"Updated! {updated['party']} pax on {updated['date']} at {updated['time']} under {updated['name']}.", state
        return "Update failed.", state
    
    return "Something went wrong.", state


def handle_slots(state):
    """Show available booking slots for a date."""
    step = state.get("slots_step", 0)
    
    if step == 0:
        state["slots_step"] = 1
        today = get_today_str()
        return f"For which date? (YYYY-MM-DD or 'today')\n  Today is {today}", state
    
    if step == 1:
        date_str = state.get("last_input", "").strip()
        if date_str.lower() == "today":
            date_str = get_today_str()
        state["slots_step"] = 0
        if not is_date_valid(date_str):
            return "Invalid date. Use YYYY-MM-DD or 'today'.", state
        slots = get_slots_for_date(date_str)
        if not slots:
            return f"No slots available for {date_str}.", state
        formatted = "\n".join(f"  {t}" for t in slots)
        return f"Available for {date_str}:\n{formatted}", state
    
    return "Something went wrong.", state


def handle_stats(state):
    """Show booking statistics."""
    state.pop("stats_step", None)  # One-shot, no flow
    s = get_booking_stats()
    lines = [
        "\n--- Booking Statistics ---",
        f"  Total reservations: {s['total']}",
        f"  Most booked time: {s['most_booked_time']}",
        f"  Most booked date: {s['most_booked_date']}",
        f"  Most common party size: {s['most_common_party']}",
        f"  Popular dish: {s['popular_dish']}",
        ""
    ]
    return "\n".join(lines), state


def process_input(user_input, state):
    """Process user input and return (response, new_state)."""
    state = state.copy()
    state["last_input"] = user_input
    
    # In-flow handlers (must come first)
    if state.get("step", 0) > 0:
        return handle_book(state)
    if state.get("cancel_step", 0) > 0:
        return handle_cancel(state)
    if state.get("history_step", 0) > 0:
        return handle_history(state)
    if state.get("rec_step", 0) > 0:
        return handle_recommend(state)
    if state.get("modify_step", 0) > 0:
        return handle_modify(state)
    if state.get("slots_step", 0) > 0:
        return handle_slots(state)
    
    intent = detect_intent(user_input)
    
    if intent == "book":
        return handle_book(state)
    if intent == "menu":
        return display_menu(), state
    if intent == "recommend":
        return handle_recommend(state)
    if intent == "history":
        return handle_history(state)
    if intent == "slots":
        return handle_slots(state)
    if intent == "stats":
        return handle_stats(state)
    if intent == "modify":
        return handle_modify(state)
    if intent == "cancel":
        return handle_cancel(state)
    if intent == "help":
        return get_help_message(), state
    if intent == "quit":
        return None, state
    
    return "I can help you book, check slots, recommend dishes, view history or stats. Type 'help' for commands.", state
