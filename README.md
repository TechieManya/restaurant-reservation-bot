# Restaurant Reservation Bot

A CLI chatbot for making dining reservations using compressed menu data and availability schedules.

## Run

```bash
python main.py
```

## Commands

- **book** / **reserve** - Book a table (phone → welcome back for returning users)
- **menu** - View the menu
- **recommend** - Get dish suggestions (veg + spicy) + save preferences
- **history** - View all reservations or filter by name
- **slots** - Show available booking times for a date
- **stats** - Booking statistics (total, most booked time, popular dish)
- **modify** - Change a booking using confirmation ID
- **cancel** - Cancel using confirmation ID (e.g. R1023)
- **help** - Show commands
- **quit** / **exit** - Exit

## Features

- **User Profiles** - Store name, phone, preferences. "Welcome back Name! Your usual 2-person spicy veg booking?"
- **Slot Availability** - `slots` shows available times for any date
- **Analytics** - `stats` shows total reservations, most booked time, popular dish
- **Persistence** - All data saved in JSON files (survives program restart)
- **Confirmation IDs** - Unique ID (e.g. R1023) for cancel/modify

## Data Files (JSON - persistent)

- `data/menu.json` - Compressed menu
- `data/availability.json` - Time slots per date
- `data/reservations.json` - Bookings
- `data/profiles.json` - User profiles (name, phone, preferences)

## Requirements

Python 3.7+. No external packages required.
