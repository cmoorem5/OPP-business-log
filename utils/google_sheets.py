import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Scopes for Google Sheets and Drive
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource(show_spinner=False)
def get_gspread_client() -> gspread.Client:
    """
    Create and cache a gspread client authorized with service account credentials.
    """
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    return gspread.authorize(creds)

@st.cache_data(ttl=300, show_spinner=False)
def load_sheet_as_df(sheet_name: str, tab_name: str) -> pd.DataFrame:
    """
    Load a Google Sheet tab into a Pandas DataFrame, cached for 5 minutes.

    Args:
        sheet_name: The name of the Google Spreadsheet.
        tab_name: The worksheet/tab name inside the spreadsheet.

    Returns:
        DataFrame containing all records from the worksheet.
    """
    client = get_gspread_client()
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(tab_name)
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

@st.cache_data(show_spinner=False)
def get_worksheet(sheet_name: str, tab_name: str) -> gspread.Worksheet:
    """
    Retrieve the raw gspread Worksheet object (cached).

    Args and returns similar to load_sheet_as_df, but returns the worksheet object.
    """
    client = get_gspread_client()
    sheet = client.open(sheet_name)
    return sheet.worksheet(tab_name)


def append_row(sheet_name: str, tab_name: str, row_data: list) -> None:
    """
    Append a single row to the specified sheet/tab.

    Args:
        sheet_name: The name of the Google Spreadsheet.
        tab_name: The worksheet/tab name inside the spreadsheet.
        row_data: List of values corresponding to columns in the sheet.
    """
    worksheet = get_worksheet(sheet_name, tab_name)
    worksheet.append_row(row_data, value_input_option="USER_ENTERED")
