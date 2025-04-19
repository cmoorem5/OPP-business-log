import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_worksheet(sheet_name, tab_name):
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open(sheet_name)
    return spreadsheet.worksheet(tab_name)

def append_row(sheet_name, tab_name, row_data):
    worksheet = get_worksheet(sheet_name, tab_name)
    worksheet.append_row(row_data, value_input_option="USER_ENTERED")
