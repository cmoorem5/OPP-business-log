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

# Your spreadsheet ID
SPREADSHEET_ID = "1W0sYd7MTTh3Tn8dqUVsG_y0kPBeoWswwgFpdoXmvEy0"


def get_gspread_client() -> gspread.Client:
    """
    Create a fresh gspread client with refreshed service account credentials.
    """
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    creds.refresh(Request())
    return gspread.authorize(creds)


@st.cache_data(ttl=300, show_spinner=False)
def load_sheet_as_df(tab_name: str) -> pd.DataFrame:
    """
    Load the worksheet `tab_name` into a pandas DataFrame using the first non-empty row as the header.
    Cached for 5 minutes.
    """
    client = get_gspread_client()
    ws = client.open_by_key(SPREADSHEET_ID).worksheet(tab_name)

    all_values = ws.get_all_values()
    if not all_values:
        return pd.DataFrame()

    header_idx = next((i for i, row in enumerate(all_values) if any(cell.strip() for cell in row)), 0)
    header = all_values[header_idx]
    data = all_values[header_idx + 1:]
    df = pd.DataFrame(data, columns=header)

    return df


def get_worksheet(tab_name: str) -> gspread.Worksheet:
    """
    Return the raw gspread Worksheet object for a given tab.
    """
    client = get_gspread_client()
    return client.open_by_key(SPREADSHEET_ID).worksheet(tab_name)


def append_row(tab_name: str, row_data: list) -> None:
    """
    Append a raw list of values as a row to the given worksheet tab.
    """
    ws = get_worksheet(tab_name)
    ws.append_row(row_data, value_input_option="USER_ENTERED")


def append_row_to_sheet(tab_name: str, row_dict: dict) -> None:
    """
    Append a dictionary as a row to the worksheet tab, matching the order of header columns.
    """
    ws = get_worksheet(tab_name)
    headers = ws.row_values(1)

    if not headers:
        raise ValueError(f"Tab '{tab_name}' has no header row to align with.")

    row = [row_dict.get(col, "") for col in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")
