"""QR Code generation for reservations."""

import qrcode
from PIL import Image, ImageTk
import io


def generate_qr_code(data, size=200):
    """
    Generate QR code image from data string.
    Returns PIL Image object.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img


def generate_qr_for_reservation(reservation_id, name, date, time, party):
    """Generate QR code with reservation details."""
    data = f"Reservation ID: {reservation_id}\nName: {name}\nDate: {date}\nTime: {time}\nParty: {party}"
    return generate_qr_code(data)


def get_qr_image_tk(qr_image):
    """Convert PIL Image to PhotoImage for tkinter."""
    return ImageTk.PhotoImage(qr_image)
