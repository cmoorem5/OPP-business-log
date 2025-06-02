import streamlit as st
from datetime import date, datetime

# --- Secrets-based values ---
SHEET_ID = st.secrets["gsheet_id"]
DRIVE_FOLDER_ID = st.secrets["gdrive_folder_id"]
YEARS = st.secrets["years"]
INCOME_TABS = st.secrets["income_tabs"]
EXPENSE_TABS = st.secrets["expense_tabs"]
STATUS_OPTIONS = st.secrets["payment_statuses"]
MONTHLY_FOLDERS = st.secrets.get("monthly_folders", {})

# --- Defaults ---
CURRENT_YEAR = str(datetime.now().year)
DEFAULT_TAB_YEAR = CURRENT_YEAR if CURRENT_YEAR in YEARS else YEARS[0]

# --- Static dropdown options ---
PROPERTIES = ["Islamorada", "Standish"]
INCOME_SOURCES = ["Renter", "Airbnb", "VRBO", "Florida Rental", "FreeWheeler"]
PAYMENT_STATUS = ["Paid", "PMT due", "Downpayment received"]
EXPENSE_CATEGORIES = [
    "Utilities", "Maintenance", "Supplies", "Cleaning", "Fees",
    "Marketing", "Insurance", "Capital Improvements", "Other"
]
PURCHASERS = ["Charlie", "Katie"]

# --- Drive folder resolver ---
def get_drive_folder_id(entry_date: date) -> str | None:
    year = str(entry_date.year)
    month = entry_date.strftime("%B")
    return MONTHLY_FOLDERS.get(year, {}).get(month)
