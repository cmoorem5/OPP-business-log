import json
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- Shared scopes for both Sheets & Drive ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# --- Load service account credentials once ---
@st.cache_resource(show_spinner=False)
def get_gspread_client() -> gspread.Client:
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

# --- Sheet accessor ---
def get_worksheet(sheet_id: str, tab_name: str) -> gspread.Worksheet:
    client = get_gspread_client()
    return client.open_by_key(sheet_id).worksheet(tab_name)

# --- Load a tab as a DataFrame ---
@st.cache_data(ttl=300, show_spinner=False)
def load_sheet_as_df(sheet_id: str, tab_name: str) -> pd.DataFrame:
    ws = get_worksheet(sheet_id, tab_name)
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame()

    header_idx = next((i for i, row in enumerate(values) if any(cell.strip() for cell in row)), 0)
    header = values[header_idx]
    data = values[header_idx + 1:]
    return pd.DataFrame(data, columns=header)

# --- Append a full list row ---
def append_row(sheet_id: str, tab_name: str, row_data: list) -> None:
    ws = get_worksheet(sheet_id, tab_name)
    ws.append_row(row_data, value_input_option="USER_ENTERED")

# --- Append a row by header-keyed dict ---
def append_row_to_sheet(sheet_id: str, tab_name: str, row_dict: dict) -> None:
    ws = get_worksheet(sheet_id, tab_name)
    headers = ws.row_values(1)
    if not headers:
        raise ValueError(f"Tab '{tab_name}' has no header row.")

    row = [row_dict.get(col, "") for col in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")

# --- Update existing row by dict of column updates ---
def update_row_in_sheet(sheet_id: str, tab_name: str, row_index: int, updates: dict) -> None:
    ws = get_worksheet(sheet_id, tab_name)
    headers = ws.row_values(1)
    row_number = row_index + 2  # header + 0-index offset

    for col, value in updates.items():
        if col in headers:
            col_num = headers.index(col) + 1
            ws.update_cell(row_number, col_num, value)
