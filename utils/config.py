import streamlit as st
from datetime import date

# --- Load centralized values from secrets ---
SHEET_ID = st.secrets["gsheet_id"]
DRIVE_FOLDER_ID = st.secrets["gdrive_folder_id"]
YEARS = st.secrets["years"]
INCOME_TABS = st.secrets["income_tabs"]
EXPENSE_TABS = st.secrets["expense_tabs"]
RECURRING_TABS = st.secrets["recurring_expense_tabs"]
STATUS_OPTIONS = st.secrets["payment_statuses"]

# --- Load monthly Drive folders by year from secrets (optional future feature) ---
# Example structure in secrets.toml (not yet added):
# monthly_folders.2025.April = "folder_id"
# monthly_folders.2025.May = "folder_id"
MONTHLY_FOLDERS = st.secrets.get("monthly_folders", {})


def get_drive_folder_id(entry_date: date) -> str | None:
    """Return Google Drive folder ID based on the entry date's year and month."""
    year = str(entry_date.year)
    month = entry_date.strftime("%B")
    return MONTHLY_FOLDERS.get(year, {}).get(month)
