# utils/google_sheets.py

import json
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

# Scopes for Sheets & Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Your spreadsheet ID (from the URL between /d/ and /edit)
SPREADSHEET_ID = "1W0sYd7MTTh3Tn8dqUVsG_y0kPBeoWswwgFpdoXmvEy0"

def get_gspread_client() -> gspread.Client:
    """
    Create a new gspread client on each call, refreshing credentials so
    you never get a stale‑token error.
    """
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    creds.refresh(Request())
    return gspread.authorize(creds)

@st.cache_data(ttl=300, show_spinner=False)
def load_sheet_as_df(tab_name: str) -> pd.DataFrame:
    """
    Load the worksheet `tab_name` from SPREADSHEET_ID into a DataFrame,
    by pulling all values and using the first non-empty row as header.
    Cached for 5 minutes.
    """
    client = get_gspread_client()
    sheet = client.open_by_key(SPREADSHEET_ID)
    ws = sheet.worksheet(tab_name)

    all_values = ws.get_all_values()
    if not all_values:
        return pd.DataFrame()

    # find first non-blank row to use as header
    header_idx = next(
        (i for i, row in enumerate(all_values) if any(cell.strip() for cell in row)),
        0
    )
    header = all_values[header_idx]
    data = all_values[header_idx + 1 :]

    df = pd.DataFrame(data, columns=header)
    return df

def get_worksheet(tab_name: str) -> gspread.Worksheet:
    """
    Retrieve the raw gspread Worksheet object for `tab_name`.
    """
    client = get_gspread_client()
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet.worksheet(tab_name)

def append_row(tab_name: str, row_data: list) -> None:
    """
    Append a single row to the given worksheet tab.
    """
    ws = get_worksheet(tab_name)
    ws.append_row(row_data, value_input_option="USER_ENTERED")
