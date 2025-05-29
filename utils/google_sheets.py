import json
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

# Scopes for both Sheets & Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Your Google Sheet ID
SPREADSHEET_ID = "1W0sYd7MTTh3Tn8dqUVsG_y0kPBeoWswwgFpdoXmvEy0"


def get_gspread_client() -> gspread.Client:
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    creds.refresh(Request())
    return gspread.authorize(creds)


def get_worksheet(tab_name: str) -> gspread.Worksheet:
    client = get_gspread_client()
    return client.open_by_key(SPREADSHEET_ID).worksheet(tab_name)


@st.cache_data(ttl=300, show_spinner=False)
def load_sheet_as_df(tab_name: str) -> pd.DataFrame:
    ws = get_worksheet(tab_name)
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame()

    header_idx = next((i for i, row in enumerate(values) if any(cell.strip() for cell in row)), 0)
    header = values[header_idx]
    data = values[header_idx + 1:]
    return pd.DataFrame(data, columns=header)


def append_row(tab_name: str, row_data: list) -> None:
    ws = get_worksheet(tab_name)
    ws.append_row(row_data, value_input_option="USER_ENTERED")


def append_row_to_sheet(tab_name: str, row_dict: dict) -> None:
    ws = get_worksheet(tab_name)
    headers = ws.row_values(1)
    if not headers:
        raise ValueError(f"Tab '{tab_name}' has no header row.")

    row = [row_dict.get(col, "") for col in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")


def update_row_in_sheet(tab_name: str, row_index: int, updates: dict) -> None:
    """
    Overwrites specific columns in a given row (zero-based row index from DataFrame).
    Adjusts for Google Sheets row numbers (+2 for header + 0-index).
    """
    ws = get_worksheet(tab_name)
    headers = ws.row_values(1)
    row_number = row_index + 2

    for col, value in updates.items():
        if col in headers:
            col_num = headers.index(col) + 1
            ws.update_cell(row_number, col_num, value)
