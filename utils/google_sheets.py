import gspread
from google.oauth2.service_account import Credentials

# Define the scope and authorize
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_worksheet(json_keyfile_path, sheet_name, tab_name):
    creds = Credentials.from_service_account_file(json_keyfile_path, scopes=SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open(sheet_name)
    return spreadsheet.worksheet(tab_name)

def append_row(json_keyfile_path, sheet_name, tab_name, row_data):
    worksheet = get_worksheet(json_keyfile_path, sheet_name, tab_name)
    worksheet.append_row(row_data, value_input_option="USER_ENTERED")
