import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Scopes for Google Sheets and Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Spreadsheet ID from your URL: https://…/d/<ID>/edit
SPREADSHEET_ID = "1W0sYd7MTTh3Tn8dqUVsG_y0kPBeoWswwgFpdoXmvEy0"

@st.cache_resource(show_spinner=False)
def get_gspread_client() -> gspread.Client:
    """
    Returns a cached gspread client authorized with the service account
    credentials stored in st.secrets["gdrive_credentials"].
    """
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

@st.cache_data(ttl=300, show_spinner=False)
def load_sheet_as_df(tab_name: str) -> pd.DataFrame:
    """
    Loads the worksheet tab called `tab_name` from the fixed SPREADSHEET_ID
    into a pandas DataFrame. Results are cached for 5 minutes.
    """
    client = get_gspread_client()
    sheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = sheet.worksheet(tab_name)
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

@st.cache_data(show_spinner=False)
def get_worksheet(tab_name: str) -> gspread.Worksheet:
    """
    Retrieves the raw gspread Worksheet object for the given tab name.
    """
    client = get_gspread_client()
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet.worksheet(tab_name)

def append_row(tab_name: str, row_data: list) -> None:
    """
    Appends a single row (row_data) to the specified worksheet tab.
    """
    ws = get_worksheet(tab_name)
    ws.append_row(row_data, value_input_option="USER_ENTERED")

