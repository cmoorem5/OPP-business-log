from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import streamlit as st
import io

SCOPES = ["https://www.googleapis.com/auth/drive"]

def _get_drive_service():
    creds_raw = st.secrets["gdrive_credentials"]
    creds_dict = dict(creds_raw)
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

def upload_file_to_drive(uploaded_file, folder_id, filename):
    service = _get_drive_service()
    media = MediaIoBaseUpload(uploaded_file, mimetype="application/pdf")
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

def generate_drive_link(file_id):
    return f"https://drive.google.com/file/d/{file_id}/view"
