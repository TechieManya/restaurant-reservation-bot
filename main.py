"""Restaurant Reservation Bot - multi-page GUI."""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
from pathlib import Path

from availability import (
    get_available_slots,
    get_today_str,
    get_slots_for_date,
    get_available_dates,
    is_date_valid,
)
from reservation import (
    create_reservation,
    get_all_reservations,
    get_booking_stats,
)
from menu import display_menu, recommend_dishes, load_menu
from waitlist import (
    add_to_waitlist,
    get_all_waitlist,
    remove_from_waitlist,
    get_waitlist_by_date_time,
)
from qr_generator import generate_qr_for_reservation, get_qr_image_tk
from bot import get_help_message


WELCOME = (
    "Welcome to Restaurant Reservation Bot!\n"
    "Use the pages on the left to book tables, see the menu, "
    "check availability, and view statistics."
)


class ReservationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Restaurant Reservation Bot")
        self.geometry("900x600")
        self.minsize(850, 520)

        self.pages = {}
        self._configure_style()
        self._build_layout()
        self.show_page("home")

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#111827")
        style.configure(
            "Header.TLabel",
            background="#020617",
            foreground="#e5e7eb",
            font=("Segoe UI", 16, "bold"),
            padding=10,
        )
        style.configure(
            "SubHeader.TLabel",
            background="#020617",
            foreground="#9ca3af",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 6),
        )
        style.map(
            "Primary.TButton",
            foreground=[("disabled", "#6b7280")],
        )

    def _build_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(12, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Restaurant Reservation Assistant",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Choose a section on the left. Each button opens a different page.",
            style="SubHeader.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        content = ttk.Frame(self, padding=(12, 8))
        content.grid(row=1, column=0, sticky="nsew")
        content.rowconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        # Left navigation
        nav = ttk.Frame(content)
        nav.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        ttk.Label(
            nav,
            text="Pages",
            style="SubHeader.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        buttons = [
            ("Home", "home"),
            ("Book table", "book"),
            ("Menu", "menu"),
            ("Recommendations", "recommend"),
            ("Slots", "slots"),
            ("Today's bookings", "today"),
            ("Available dates", "dates"),
            ("History", "history"),
            ("Waitlist", "waitlist"),
            ("Statistics", "stats"),
        ]

        for i, (label, key) in enumerate(buttons, start=1):
            ttk.Button(
                nav,
                text=label,
                style="Primary.TButton",
                command=lambda k=key: self.show_page(k),
                width=18,
            ).grid(row=i, column=0, sticky="ew", pady=2)

        # Right main area where pages are stacked
        main_area = ttk.Frame(content)
        main_area.grid(row=0, column=1, sticky="nsew")
        main_area.rowconfigure(0, weight=1)
        main_area.columnconfigure(0, weight=1)

        self._create_pages(main_area)

    def _create_pages(self, parent):
        # Home page
        home = ttk.Frame(parent)
        home.grid(row=0, column=0, sticky="nsew")
        home.columnconfigure(0, weight=1)
        home.rowconfigure(1, weight=1)

        ttk.Label(
            home,
            text="Welcome",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        home_text = tk.Text(
            home,
            wrap="word",
            state="normal",
            bg="#020617",
            fg="#e5e7eb",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            relief="flat",
        )
        home_text.grid(row=1, column=0, sticky="nsew")
        home_text.insert("end", WELCOME + "\n\n")
        home_text.insert("end", get_help_message().strip())
        home_text.configure(state="disabled")
        self.pages["home"] = home

        # Menu page - text only (fast loading)
        menu_frame = ttk.Frame(parent)
        menu_frame.grid(row=0, column=0, sticky="nsew")
        menu_frame.columnconfigure(0, weight=1)
        menu_frame.rowconfigure(1, weight=1)

        ttk.Label(
            menu_frame,
            text="Menu",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        # Simple text widget with scrollbar
        menu_text_frame = ttk.Frame(menu_frame)
        menu_text_frame.grid(row=1, column=0, sticky="nsew")
        menu_text_frame.columnconfigure(0, weight=1)
        menu_text_frame.rowconfigure(0, weight=1)

        self.menu_text = tk.Text(
            menu_text_frame,
            wrap="word",
            state="normal",
            bg="#020617",
            fg="#FFFFFF",
            font=("Segoe UI", 11),
            padx=15,
            pady=15,
            relief="flat",
            insertbackground="#FFFFFF",
        )
        self.menu_text.grid(row=0, column=0, sticky="nsew")

        scrollbar_menu = ttk.Scrollbar(
            menu_text_frame, orient="vertical", command=self.menu_text.yview
        )
        scrollbar_menu.grid(row=0, column=1, sticky="ns")
        self.menu_text.configure(yscrollcommand=scrollbar_menu.set)

        # Configure text tags for better formatting
        self.menu_text.tag_configure("category", foreground="#FF6B35", font=("Segoe UI", 14, "bold"))
        self.menu_text.tag_configure("item", foreground="#FFFFFF", font=("Segoe UI", 11))
        self.menu_text.tag_configure("price", foreground="#FFD700", font=("Segoe UI", 11, "bold"))
        self.menu_text.tag_configure("veg", foreground="#90EE90", font=("Segoe UI", 10))
        self.menu_text.tag_configure("spice", foreground="#FF6347", font=("Segoe UI", 10))

        ttk.Button(
            menu_frame,
            text="Reload menu",
            style="Primary.TButton",
            command=self._load_menu,
        ).grid(row=2, column=0, sticky="e", pady=(6, 0))

        self.pages["menu"] = menu_frame

        # Book page
        book = ttk.Frame(parent)
        book.grid(row=0, column=0, sticky="nsew")
        for i in range(6):
            book.rowconfigure(i, weight=0)
        book.rowconfigure(6, weight=1)
        book.columnconfigure(1, weight=1)

        ttk.Label(
            book,
            text="Book a table",
            style="Header.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(book, text="Phone (optional):").grid(row=1, column=0, sticky="w", pady=2)
        self.book_phone = ttk.Entry(book)
        self.book_phone.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(book, text="Party size (1-10):").grid(row=2, column=0, sticky="w", pady=2)
        self.book_party = ttk.Entry(book)
        self.book_party.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(book, text="Date (YYYY-MM-DD or 'today'):").grid(
            row=3, column=0, sticky="w", pady=2
        )
        self.book_date = ttk.Entry(book)
        self.book_date.grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Label(book, text="Time slot:").grid(row=4, column=0, sticky="w", pady=2)
        self.book_time = ttk.Combobox(book, state="readonly", values=[])
        self.book_time.grid(row=4, column=1, sticky="ew", pady=2)

        ttk.Button(
            book,
            text="Load slots",
            style="Primary.TButton",
            command=self._load_booking_slots,
        ).grid(row=5, column=1, sticky="e", pady=(2, 6))

        ttk.Label(book, text="Name:").grid(row=6, column=0, sticky="nw", pady=2)
        self.book_name = ttk.Entry(book)
        self.book_name.grid(row=6, column=1, sticky="new", pady=2)

        ttk.Button(
            book,
            text="Confirm booking",
            style="Primary.TButton",
            command=self._confirm_booking,
        ).grid(row=7, column=1, sticky="e", pady=(10, 0))

        self.pages["book"] = book

        # Recommendations page
        rec = ttk.Frame(parent)
        rec.grid(row=0, column=0, sticky="nsew")
        rec.columnconfigure(1, weight=1)
        rec.rowconfigure(3, weight=1)

        ttk.Label(
            rec,
            text="Dish recommendations",
            style="Header.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(rec, text="Veg preference:").grid(row=1, column=0, sticky="w", pady=2)
        self.rec_veg = ttk.Combobox(
            rec, state="readonly", values=["Any", "Veg", "Non-veg"]
        )
        self.rec_veg.current(0)
        self.rec_veg.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(rec, text="Spice level:").grid(row=2, column=0, sticky="w", pady=2)
        self.rec_spice = ttk.Combobox(
            rec, state="readonly", values=["Any", "Mild", "Medium", "Hot"]
        )
        self.rec_spice.current(0)
        self.rec_spice.grid(row=2, column=1, sticky="ew", pady=2)

        self.rec_text = tk.Text(
            rec,
            wrap="word",
            state="normal",
            bg="#020617",
            fg="#e5e7eb",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            relief="flat",
        )
        self.rec_text.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(6, 0))

        ttk.Button(
            rec,
            text="Get recommendations",
            style="Primary.TButton",
            command=self._load_recommendations,
        ).grid(row=4, column=1, sticky="e", pady=(6, 0))

        self.pages["recommend"] = rec

        # Slots page
        slots = ttk.Frame(parent)
        slots.grid(row=0, column=0, sticky="nsew")
        slots.columnconfigure(1, weight=1)
        slots.rowconfigure(2, weight=1)

        ttk.Label(
            slots,
            text="Available time slots",
            style="Header.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        today = get_today_str()
        ttk.Label(
            slots,
            text=f"Date (YYYY-MM-DD or 'today'). Today is {today}:",
        ).grid(row=1, column=0, sticky="w", pady=2)
        self.slots_date = ttk.Entry(slots)
        self.slots_date.grid(row=1, column=1, sticky="ew", pady=2)

        self.slots_text = tk.Text(
            slots,
            wrap="word",
            state="normal",
            bg="#020617",
            fg="#e5e7eb",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            relief="flat",
        )
        self.slots_text.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(6, 0))

        ttk.Button(
            slots,
            text="Show slots",
            style="Primary.TButton",
            command=self._load_slots,
        ).grid(row=3, column=1, sticky="e", pady=(6, 0))

        self.pages["slots"] = slots

        # Today's bookings page
        today_frame = ttk.Frame(parent)
        today_frame.grid(row=0, column=0, sticky="nsew")
        today_frame.columnconfigure(0, weight=1)
        today_frame.rowconfigure(1, weight=1)

        ttk.Label(
            today_frame,
            text="Today's bookings",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.today_text = tk.Text(
            today_frame,
            wrap="word",
            state="normal",
            bg="#020617",
            fg="#e5e7eb",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            relief="flat",
        )
        self.today_text.grid(row=1, column=0, sticky="nsew")

        ttk.Button(
            today_frame,
            text="Refresh",
            style="Primary.TButton",
            command=self._load_today,
        ).grid(row=2, column=0, sticky="e", pady=(6, 0))

        self.pages["today"] = today_frame

        # Available dates page
        dates_frame = ttk.Frame(parent)
        dates_frame.grid(row=0, column=0, sticky="nsew")
        dates_frame.columnconfigure(0, weight=1)
        dates_frame.rowconfigure(1, weight=1)

        ttk.Label(
            dates_frame,
            text="Available booking dates",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.dates_text = tk.Text(
            dates_frame,
            wrap="word",
            state="normal",
            bg="#020617",
            fg="#e5e7eb",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            relief="flat",
        )
        self.dates_text.grid(row=1, column=0, sticky="nsew")

        ttk.Button(
            dates_frame,
            text="Refresh",
            style="Primary.TButton",
            command=self._load_dates,
        ).grid(row=2, column=0, sticky="e", pady=(6, 0))

        self.pages["dates"] = dates_frame

        # History page
        history = ttk.Frame(parent)
        history.grid(row=0, column=0, sticky="nsew")
        history.columnconfigure(1, weight=1)
        history.rowconfigure(2, weight=1)

        ttk.Label(
            history,
            text="Reservation history",
            style="Header.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(history, text="Filter by name (optional):").grid(
            row=1, column=0, sticky="w", pady=2
        )
        self.history_name = ttk.Entry(history)
        self.history_name.grid(row=1, column=1, sticky="ew", pady=2)

        self.history_text = tk.Text(
            history,
            wrap="word",
            state="normal",
            bg="#020617",
            fg="#e5e7eb",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            relief="flat",
        )
        self.history_text.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(6, 0))

        ttk.Button(
            history,
            text="Load history",
            style="Primary.TButton",
            command=self._load_history,
        ).grid(row=3, column=1, sticky="e", pady=(6, 0))

        self.pages["history"] = history

        # Waitlist page
        waitlist_frame = ttk.Frame(parent)
        waitlist_frame.grid(row=0, column=0, sticky="nsew")
        waitlist_frame.columnconfigure(0, weight=1)
        waitlist_frame.rowconfigure(2, weight=1)

        ttk.Label(
            waitlist_frame,
            text="Waitlist Management",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        filter_frame = ttk.Frame(waitlist_frame)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        filter_frame.columnconfigure(1, weight=1)

        ttk.Label(filter_frame, text="Filter by date:").grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.waitlist_date_filter = ttk.Entry(filter_frame)
        self.waitlist_date_filter.grid(row=0, column=1, sticky="ew", padx=(0, 4))

        ttk.Label(filter_frame, text="Time:").grid(row=0, column=2, sticky="w", padx=(0, 4))
        self.waitlist_time_filter = ttk.Entry(filter_frame)
        self.waitlist_time_filter.grid(row=0, column=3, sticky="ew", padx=(0, 4))

        self.waitlist_text = tk.Text(
            waitlist_frame,
            wrap="word",
            state="normal",
            bg="#020617",
            fg="#e5e7eb",
            font=("Consolas", 10),
            padx=10,
            pady=10,
            relief="flat",
        )
        self.waitlist_text.grid(row=2, column=0, sticky="nsew")

        btn_frame = ttk.Frame(waitlist_frame)
        btn_frame.grid(row=3, column=0, sticky="e", pady=(6, 0))

        ttk.Button(
            btn_frame,
            text="Load waitlist",
            style="Primary.TButton",
            command=self._load_waitlist,
        ).grid(row=0, column=0, sticky="e", padx=(0, 4))

        ttk.Button(
            btn_frame,
            text="Clear filters",
            style="Primary.TButton",
            command=self._clear_waitlist_filters,
        ).grid(row=0, column=1, sticky="e")

        self.pages["waitlist"] = waitlist_frame

        # Stats page
        stats = ttk.Frame(parent)
        stats.grid(row=0, column=0, sticky="nsew")
        stats.columnconfigure(0, weight=1)
        for i in range(6):
            stats.rowconfigure(i, weight=0)

        ttk.Label(
            stats,
            text="Booking statistics",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.stats_vars = {
            "total": tk.StringVar(value="-"),
            "time": tk.StringVar(value="-"),
            "date": tk.StringVar(value="-"),
            "party": tk.StringVar(value="-"),
            "dish": tk.StringVar(value="-"),
        }

        ttk.Label(stats, text="Total reservations:").grid(
            row=1, column=0, sticky="w", pady=2
        )
        ttk.Label(stats, textvariable=self.stats_vars["total"]).grid(
            row=1, column=0, sticky="e", padx=(0, 10)
        )

        ttk.Label(stats, text="Most booked time:").grid(
            row=2, column=0, sticky="w", pady=2
        )
        ttk.Label(stats, textvariable=self.stats_vars["time"]).grid(
            row=2, column=0, sticky="e", padx=(0, 10)
        )

        ttk.Label(stats, text="Most booked date:").grid(
            row=3, column=0, sticky="w", pady=2
        )
        ttk.Label(stats, textvariable=self.stats_vars["date"]).grid(
            row=3, column=0, sticky="e", padx=(0, 10)
        )

        ttk.Label(stats, text="Most common party size:").grid(
            row=4, column=0, sticky="w", pady=2
        )
        ttk.Label(stats, textvariable=self.stats_vars["party"]).grid(
            row=4, column=0, sticky="e", padx=(0, 10)
        )

        ttk.Label(stats, text="Most popular dish:").grid(
            row=5, column=0, sticky="w", pady=2
        )
        ttk.Label(stats, textvariable=self.stats_vars["dish"]).grid(
            row=5, column=0, sticky="e", padx=(0, 10)
        )

        ttk.Button(
            stats,
            text="Refresh",
            style="Primary.TButton",
            command=self._load_stats,
        ).grid(row=6, column=0, sticky="e", pady=(10, 0))

        self.pages["stats"] = stats

    def show_page(self, key):
        page = self.pages.get(key)
        if not page:
            return
        page.tkraise()

        # Auto-refresh data for some pages when opened
        if key == "menu":
            self._load_menu()
        elif key == "today":
            self._load_today()
        elif key == "dates":
            self._load_dates()
        elif key == "history":
            self._load_history()
        elif key == "waitlist":
            self._load_waitlist()
        elif key == "stats":
            self._load_stats()

    # --- Data loaders -------------------------------------------------
    def _load_menu(self):
        """Load menu - fast text-only version."""
        menu_data = load_menu()
        items = menu_data.get("items", [])
        
        self.menu_text.configure(state="normal")
        self.menu_text.delete("1.0", "end")
        
        if not items:
            self.menu_text.insert("end", "No menu items available.", "item")
            self.menu_text.configure(state="disabled")
            return

        current_category = None

        for item in items:
            category = item.get("c", "Other")
            
            # Add category header
            if category != current_category:
                current_category = category
                if current_category:
                    self.menu_text.insert("end", "\n\n", "item")
                self.menu_text.insert("end", f"{category}:\n", "category")
            
            # Item name
            name = item.get("n", "Unknown")
            self.menu_text.insert("end", f"  • {name}", "item")
            
            # Veg indicator
            if item.get("v"):
                self.menu_text.insert("end", " (V)", "veg")
            
            # Spice level
            spice = item.get("s", 0)
            if spice == 1:
                self.menu_text.insert("end", " [Medium]", "spice")
            elif spice == 2:
                self.menu_text.insert("end", " [Hot]", "spice")
            
            # Price
            price = item.get("p", 0)
            self.menu_text.insert("end", f" - ", "item")
            self.menu_text.insert("end", f"${price:.2f}", "price")
            self.menu_text.insert("end", "\n", "item")

        self.menu_text.insert("end", "\n", "item")
        self.menu_text.configure(state="disabled")
        self.menu_text.see("1.0")  # Scroll to top

    def _load_recommendations(self):
        veg_map = {"Any": "any", "Veg": "veg", "Non-veg": "nonveg"}
        spice_map = {
            "Any": "any",
            "Mild": "mild",
            "Medium": "medium",
            "Hot": "hot",
        }
        veg = veg_map.get(self.rec_veg.get() or "Any", "any")
        spicy = spice_map.get(self.rec_spice.get() or "Any", "any")
        text = recommend_dishes(veg, spicy)
        self.rec_text.configure(state="normal")
        self.rec_text.delete("1.0", "end")
        self.rec_text.insert("end", text.strip())
        self.rec_text.configure(state="disabled")

    def _load_booking_slots(self):
        party_str = self.book_party.get().strip()
        date_str = self.book_date.get().strip()

        try:
            party = int(party_str)
        except ValueError:
            messagebox.showwarning("Invalid party size", "Enter a number between 1 and 10.")
            return
        if not (1 <= party <= 10):
            messagebox.showwarning("Invalid party size", "Enter a number between 1 and 10.")
            return

        if not date_str:
            messagebox.showwarning("Date required", "Please enter a date.")
            return

        if date_str.lower() == "today":
            date_str = get_today_str()
        if not is_date_valid(date_str):
            messagebox.showwarning("Invalid date", "Use YYYY-MM-DD or 'today'.")
            return

        slots = get_available_slots(date_str, party)
        if not slots:
            # Offer waitlist option
            response = messagebox.askyesno(
                "No slots available",
                f"No time slots available for {date_str} and {party} people.\n\n"
                "Would you like to join the waitlist?",
            )
            if response:
                # Show waitlist dialog
                phone_val = self.book_phone.get().strip() or None
                self._show_waitlist_dialog(name="", party=party, date=date_str, phone=phone_val)
            self.book_time["values"] = []
            return

        self.book_time["values"] = slots
        self.book_time.set(slots[0])
        messagebox.showinfo("Slots loaded", "Select a time slot from the dropdown.")

    def _confirm_booking(self):
        name = self.book_name.get().strip()
        party_str = self.book_party.get().strip()
        date_str = self.book_date.get().strip()
        time_slot = self.book_time.get().strip()
        phone = self.book_phone.get().strip() or None

        if not name:
            messagebox.showwarning("Name required", "Please enter a name.")
            return
        try:
            party = int(party_str)
        except ValueError:
            messagebox.showwarning("Invalid party size", "Enter a number between 1 and 10.")
            return
        if not (1 <= party <= 10):
            messagebox.showwarning("Invalid party size", "Enter a number between 1 and 10.")
            return

        if not date_str:
            messagebox.showwarning("Date required", "Please enter a date.")
            return
        if date_str.lower() == "today":
            date_str = get_today_str()
        if not is_date_valid(date_str):
            messagebox.showwarning("Invalid date", "Use YYYY-MM-DD or 'today'.")
            return

        if not time_slot:
            messagebox.showwarning("Time required", "Please choose a time slot.")
            return

        try:
            res = create_reservation(name, party, date_str, time_slot, phone=phone)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not create reservation:\n{exc}")
            return

        # Show QR code in a new window
        self._show_qr_code(res)

        # Clear form
        self.book_phone.delete(0, "end")
        self.book_party.delete(0, "end")
        self.book_date.delete(0, "end")
        self.book_time.set("")
        self.book_time["values"] = []
        self.book_name.delete(0, "end")

    def _load_slots(self):
        date_str = self.slots_date.get().strip()
        if not date_str:
            messagebox.showwarning("Date required", "Please enter a date.")
            return
        slots = get_slots_for_date(date_str)
        self.slots_text.configure(state="normal")
        self.slots_text.delete("1.0", "end")
        if not slots:
            self.slots_text.insert("end", f"No slots available for {date_str}.")
        else:
            self.slots_text.insert(
                "end",
                f"Available slots for {date_str}:\n"
                + "\n".join(f"  • {t}" for t in slots),
            )
        self.slots_text.configure(state="disabled")

    def _load_today(self):
        today = get_today_str()
        reservations = [
            r for r in get_all_reservations() if r.get("date") == today
        ]
        self.today_text.configure(state="normal")
        self.today_text.delete("1.0", "end")
        if not reservations:
            self.today_text.insert("end", f"No reservations for today ({today}).")
        else:
            self.today_text.insert("end", f"Today's reservations ({today}):\n\n")
            for r in reservations:
                cid = r.get("id", "-")
                self.today_text.insert(
                    "end",
                    f"{cid} | {r.get('name', '?')} | "
                    f"{r.get('party', '?')} pax @ {r.get('time', '?')}\n",
                )
        self.today_text.configure(state="disabled")

    def _load_dates(self):
        dates = get_available_dates()
        today = get_today_str()
        self.dates_text.configure(state="normal")
        self.dates_text.delete("1.0", "end")
        if not dates:
            self.dates_text.insert("end", "No availability data configured yet.")
        else:
            self.dates_text.insert("end", "Available booking dates:\n\n")
            for d in dates:
                marker = " (today)" if d == today else ""
                self.dates_text.insert("end", f"  • {d}{marker}\n")
        self.dates_text.configure(state="disabled")

    def _load_history(self):
        name_filter = self.history_name.get().strip().lower()
        reservations = get_all_reservations()
        if name_filter:
            reservations = [
                r
                for r in reservations
                if r.get("name", "").lower() == name_filter
            ]
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        if not reservations:
            if name_filter:
                self.history_text.insert(
                    "end", f"No reservations found for '{name_filter}'."
                )
            else:
                self.history_text.insert("end", "No reservations found.")
        else:
            self.history_text.insert("end", "Reservation history:\n\n")
            for r in reservations:
                cid = r.get("id", "-")
                self.history_text.insert(
                    "end",
                    f"{cid} | {r.get('name', '?')} | "
                    f"{r.get('party', '?')} pax | "
                    f"{r.get('date', '?')} @ {r.get('time', '?')}\n",
                )
        self.history_text.configure(state="disabled")

    def _show_qr_code(self, reservation):
        """Show QR code in a popup window."""
        qr_window = tk.Toplevel(self)
        qr_window.title("Reservation QR Code")
        qr_window.geometry("400x500")
        qr_window.configure(bg="#111827")

        # Generate QR code
        qr_img = generate_qr_for_reservation(
            reservation["id"],
            reservation["name"],
            reservation["date"],
            reservation["time"],
            reservation["party"],
        )
        photo = get_qr_image_tk(qr_img)

        # Display QR code
        qr_label = ttk.Label(qr_window, image=photo, background="#111827")
        qr_label.image = photo  # Keep reference
        qr_label.pack(pady=20)

        # Reservation details
        details = (
            f"Reservation ID: {reservation['id']}\n"
            f"Name: {reservation['name']}\n"
            f"Date: {reservation['date']}\n"
            f"Time: {reservation['time']}\n"
            f"Party: {reservation['party']} people"
        )
        details_label = ttk.Label(
            qr_window,
            text=details,
            font=("Segoe UI", 10),
            foreground="#e5e7eb",
            background="#111827",
        )
        details_label.pack(pady=10)

        ttk.Button(
            qr_window,
            text="Close",
            command=qr_window.destroy,
        ).pack(pady=10)

        messagebox.showinfo(
            "Reservation created",
            f"Booking confirmed!\n\n"
            f"Reservation ID: {reservation['id']}\n"
            f"{reservation['party']} people on {reservation['date']} at {reservation['time']} "
            f"under {reservation['name']}.\n\n"
            f"QR code displayed above.",
        )

    def _show_waitlist_dialog(self, name="", party=2, date="", phone=None):
        """Show dialog to add to waitlist."""
        dialog = tk.Toplevel(self)
        dialog.title("Join Waitlist")
        dialog.geometry("400x300")
        dialog.configure(bg="#111827")

        ttk.Label(
            dialog,
            text="Join Waitlist",
            font=("Segoe UI", 14, "bold"),
            foreground="#e5e7eb",
            background="#111827",
        ).pack(pady=10)

        ttk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.insert(0, name)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="Phone (optional):").pack(pady=5)
        phone_entry = ttk.Entry(dialog, width=30)
        if phone:
            phone_entry.insert(0, phone)
        phone_entry.pack(pady=5)

        ttk.Label(dialog, text="Preferred time slot:").pack(pady=5)
        time_entry = ttk.Entry(dialog, width=30)
        time_entry.pack(pady=5)

        def add_to_waitlist_click():
            w_name = name_entry.get().strip()
            w_phone = phone_entry.get().strip() or None
            w_time = time_entry.get().strip()

            if not w_name:
                messagebox.showwarning("Name required", "Please enter a name.")
                return
            if not w_time:
                messagebox.showwarning("Time required", "Please enter a preferred time.")
                return

            try:
                entry = add_to_waitlist(w_name, party, date, w_time, w_phone)
                messagebox.showinfo(
                    "Added to waitlist",
                    f"You've been added to the waitlist!\n\n"
                    f"Waitlist ID: {entry['id']}\n"
                    f"We'll notify you if a slot becomes available.",
                )
                dialog.destroy()
            except Exception as exc:
                messagebox.showerror("Error", f"Could not add to waitlist:\n{exc}")

        ttk.Button(
            dialog,
            text="Add to Waitlist",
            command=add_to_waitlist_click,
        ).pack(pady=20)

    def _load_waitlist(self):
        """Load waitlist entries."""
        date_filter = self.waitlist_date_filter.get().strip()
        time_filter = self.waitlist_time_filter.get().strip()

        waitlist = get_all_waitlist()

        if date_filter and time_filter:
            waitlist = [
                w
                for w in waitlist
                if w.get("date") == date_filter and w.get("time") == time_filter
            ]
        elif date_filter:
            waitlist = [w for w in waitlist if w.get("date") == date_filter]
        elif time_filter:
            waitlist = [w for w in waitlist if w.get("time") == time_filter]

        self.waitlist_text.configure(state="normal")
        self.waitlist_text.delete("1.0", "end")

        if not waitlist:
            self.waitlist_text.insert("end", "No waitlist entries found.")
        else:
            self.waitlist_text.insert("end", "Waitlist Entries:\n\n")
            for w in waitlist:
                wid = w.get("id", "-")
                self.waitlist_text.insert(
                    "end",
                    f"{wid} | {w.get('name', '?')} | "
                    f"{w.get('party', '?')} pax | "
                    f"{w.get('date', '?')} @ {w.get('time', '?')}\n",
                )
        self.waitlist_text.configure(state="disabled")

    def _clear_waitlist_filters(self):
        """Clear waitlist filter fields."""
        self.waitlist_date_filter.delete(0, "end")
        self.waitlist_time_filter.delete(0, "end")
        self._load_waitlist()

    def _load_stats(self):
        stats = get_booking_stats()
        self.stats_vars["total"].set(str(stats.get("total", "-")))
        self.stats_vars["time"].set(str(stats.get("most_booked_time", "-")))
        self.stats_vars["date"].set(str(stats.get("most_booked_date", "-")))
        self.stats_vars["party"].set(str(stats.get("most_common_party", "-")))
        self.stats_vars["dish"].set(str(stats.get("popular_dish", "-")))


def main():
    app = ReservationApp()
    app.mainloop()


if __name__ == "__main__":
    main()
