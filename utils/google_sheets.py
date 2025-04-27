import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource(show_spinner=False)
def get_gspread_client():
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    return gspread.authorize(creds)

@st.cache_data(ttl=300, show_spinner=False)
def load_sheet_as_df(sheet_name: str, tab_name: str) -> pd.DataFrame:
    client = get_gspread_client()
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(tab_name)
    return pd.DataFrame(worksheet.get_all_records())

def append_row(sheet_name: str, tab_name: str, row_data: list):
    client = get_gspread_client()
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(tab_name)
    worksheet.append_row(row_data, value_input_option="USER_ENTERED")
