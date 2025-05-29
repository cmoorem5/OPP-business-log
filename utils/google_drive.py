import json
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive"]

def _get_drive_service():
    creds_raw = st.secrets["gdrive_credentials"]
    creds_dict = json.loads(creds_raw) if isinstance(creds_raw, str) else creds_raw
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

def upload_file_to_drive(uploaded_file, filename: str, folder_id: str) -> str:
    service = _get_drive_service()
    media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
    file_metadata = {
        "name": filename,
        "parents": [folder_id]
    }
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    return file.get("id")

def generate_drive_link(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/view"
