import re
from datetime import date

from utils.google_sheets import append_row_to_sheet
from utils.google_drive import upload_file_to_drive
from utils.config import SHEET_ID, get_drive_folder_id

# Optional normalization
CATEGORY_MAP = {
    "property expense": "Property Expense",
    "prop. exp": "Property Expense",
    "propertyexpenses": "Property Expense",
    "furnishings & supplies": "Furnishings & Supplies",
    "supplies": "Furnishings & Supplies",
    "guest expenses": "Guest & Operational Expenses",
    "misc": "Misc & Other",
    "miscellaneous": "Misc & Other",
    "legal": "Legal & Professional Services",
    "food": "Food & Beverage",
    "tax": "Taxes & Compliance",
    "improvements": "Business Expansion & Improvements"
}


def sanitize_filename(filename: str) -> str:
    name = filename.strip().lower().replace(" ", "_")
    return re.sub(r"[^a-zA-Z0-9_.-]", "", name)


def build_income_payload(
    booking_date: date,
    check_in: date,
    check_out: date,
    amount: float,
    payment_type: str,
    status: str,
    renter_name: str,
    email: str,
    phone: str,
    origin: str,
    notes: str
) -> dict:
    headers = [
        "Month", "Date", "Purchaser", "Item", "Property", "Category",
        "Amount", "Comments", "Receipt Link", "Email", "Phone", "Origin",
        "Check-in", "Check-out", "Payment Status", "Paid", "Total", "Balance"
    ]
    values = [
        booking_date.strftime("%B"),
        booking_date.strftime("%Y-%m-%d"),
        renter_name,
        f"Rental {check_in} to {check_out}",
        "Islamorada",  # If supporting multiple, pass property in
        payment_type,
        amount,
        notes,
        "",
        email,
        phone,
        origin,
        check_in.strftime("%Y-%m-%d"),
        check_out.strftime("%Y-%m-%d"),
        status,
        amount,
        amount,
        0.0
    ]
    return dict(zip(headers, values))


def build_expense_payload(
    expense_date: date,
    purchaser: str,
    item: str,
    property_selected: str,
    category: str,
    amount: float,
    comments: str,
    receipt_file
) -> dict:
    month = expense_date.strftime("%B")
    receipt_link = ""

    if receipt_file:
        folder_id = get_drive_folder_id(expense_date)
        filename = sanitize_filename(receipt_file.name)
        file_id = upload_file_to_drive(receipt_file, filename, folder_id)
        receipt_link = f"https://drive.google.com/file/d/{file_id}/view"

    normalized_category = CATEGORY_MAP.get(category.strip().lower(), category)

    headers = [
        "Month", "Date", "Purchaser", "Item", "Property",
        "Category", "Amount", "Comments", "Receipt Link"
    ]
    values = [
        month,
        expense_date.strftime("%Y-%m-%d"),
        purchaser,
        item,
        property_selected,
        normalized_category,
        amount,
        comments,
        receipt_link
    ]
    return dict(zip(headers, values))


def log_income(sheet_name: str, row_data: dict):
    append_row_to_sheet(SHEET_ID, sheet_name, row_data)


def log_expense(sheet_name: str, row_data: dict):
    append_row_to_sheet(SHEET_ID, sheet_name, row_data)
