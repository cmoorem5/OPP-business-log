from datetime import date

# Map years → months → Drive folder IDs
MONTHLY_FOLDERS = {
    2025: {
        "April":    "1wPerZFB-9FufTZOGfFXf2xMVg4VlGtdC",
        "May":      "1e12yCfo8WZS8gnYuSPbxeHiZ1aVWbbJe",
        "June":     "1WRSSZUGPHgGvd1cSUNDEjpTGq2FmrqcZ",
        "July":     "10nWoAibOWzVeWx0Qn3TC8Z6g-UXkToPd",
        "August":   "1xvT2NA9rPpXX0SQ1CKE9NeTbc9mvrgxK",
        "September":"160isZV8ja5Kgw7sKx88f969tIUZR6Jfo",
        "October":  "1XbP4T78e71CYA5s-1ksPYK6bujmo-UQn",
        "November": "1zxxtG1cwvpcckQ3nvB3zKHStxDBfRFF6",
        "December": "1iJwfC3siEudH8uzdZGwlid6ufhFG5AMb",
    }
}

def get_drive_folder_id(entry_date: date) -> str | None:
    """Return the Drive folder ID for the given date, or None if not configured."""
    year_map = MONTHLY_FOLDERS.get(entry_date.year, {})
    return year_map.get(entry_date.strftime("%B"))
