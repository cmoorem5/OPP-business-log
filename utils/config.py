import streamlit as st
from datetime import date, datetime

# --- Load centralized values from secrets ---
SHEET_ID = st.secrets["gsheet_id"]
DRIVE_FOLDER_ID = st.secrets["gdrive_folder_id"]
YEARS = st.secrets["years"]
INCOME_TABS = st.secrets["income_tabs"]
EXPENSE_TABS = st.secrets["expense_tabs"]
STATUS_OPTIONS = st.secrets["payment_statuses"]

# --- Default to current year ---
CURRENT_YEAR = str(datetime.now().year)
DEFAULT_TAB_YEAR = CURRENT_YEAR if CURRENT_YEAR in YEARS else YEARS[0]

# --- Monthly Drive folder mapping ---
MONTHLY_FOLDERS = st.secrets.get("monthly_folders", {})

def get_drive_folder_id(entry_date: date) -> str | None:
    """Return Google Drive folder ID based on the entry date's year and month."""
    year = str(entry_date.year)
    month = entry_date.strftime("%B")
    return MONTHLY_FOLDERS.get(year, {}).get(month)
