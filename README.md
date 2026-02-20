
---

# 🍽️ Restaurant Reservation Bot (GUI)

A modern **multi-page GUI application** for managing restaurant reservations with an intuitive interface.
The system supports table booking, menu browsing, personalized recommendations, waitlist management, QR code generation, and real-time analytics.

---

## 🚀 Quick Start

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install qrcode[pil] Pillow
```

### 2️⃣ Run the Application

```bash
python main.py
```

The GUI will open with a sidebar navigation and main content area.

---

## 📱 GUI Pages

### 🏠 Home

* Welcome message
* Feature overview
* Help guide

### 📅 Book Table

* Phone number (optional → profile recognition)
* Party size (1–10 people)
* Date selection (YYYY-MM-DD or “today”)
* Time slot loading
* Name entry

**Extras**

* QR code generation after booking
* Waitlist option when slots are full

---

### 🍕 Menu

30+ dishes across categories:

* Pizza (5)
* Starters (7)
* Main Courses (12)
* Desserts (6)

**Visual indicators**

* Vegetarian items (green)
* Spice level labels
* Category color coding

---

### 💡 Recommendations

Personalized suggestions based on:

* Veg / Non-veg preference
* Spice level

Preferences are saved for returning users.

---

### ⏰ Slots

Displays available time slots for selected date.

---

### 📋 Today’s Bookings

Quick overview of daily reservations.

---

### 📆 Available Dates

Shows dates with booking availability and highlights today.

---

### 📜 History

* View all reservations
* Filter by customer name

---

### ⏳ Waitlist

* Manage waitlist entries
* Filter by date/time
* Unique waitlist IDs

---

### 📊 Statistics

Analytics including:

* Total reservations
* Most booked time
* Popular dishes
* Common party size

---

## ✨ Key Features

### 🎯 User Profiles

* Stores name, phone, preferences
* Welcome-back greeting
* Remembers usual booking

---

### 📱 QR Code Generation

Each booking generates a QR code containing:

* Reservation ID
* Customer name
* Date & time
* Party size

---

### ⏳ Waitlist Management

Automatic waitlist when slots are full with unique IDs.

---

### 📊 Analytics Dashboard

Real-time insights into booking patterns and preferences.

---

### 💾 Data Persistence

All data stored in JSON files — survives restart.

---

### 🆔 Confirmation IDs

Unique reservation IDs (R1000+) for modify/cancel.

---

## 📁 Data Files

Located in the `data/` directory:

* `menu.json` → Menu items
* `availability.json` → Slots & capacity
* `reservations.json` → Bookings
* `profiles.json` → Customer profiles
* `waitlist.json` → Waitlist entries

---

## 🕐 Time Slots

Lunch: 12:00 – 15:00
Dinner: 17:00 – 22:00

10 slots per day with configurable capacity.

---

## 🛠️ Tech Stack

* Python
* Tkinter (GUI)
* JSON (persistence)
* Pillow (image processing)
* QRCode library

Fully self-contained — no external APIs.

---

## 🎨 UI Highlights

* Dark theme interface
* Color-coded navigation
* Responsive layout
* Scrollable content
* Quick action buttons

---

## 📝 Example Workflow

**Booking**

1. Book Table → Enter details
2. Load slots → Select time
3. Confirm booking
4. QR code generated

**Recommendations**

1. Choose preferences
2. Get dish suggestions
3. Save for future use

---

## 🔮 Future Improvements

* AI-based recommendations
* Online booking integration
* Payments
* Notifications
* Cloud database

---

## 📄 License

Educational project.

---

## 🤝 Contributing

Open for improvements and learning.


