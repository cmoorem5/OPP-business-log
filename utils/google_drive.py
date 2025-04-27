import os
import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

@st.cache_resource(show_spinner=False)
def get_drive_service():
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

def upload_file_to_drive(file_path: str, file_name: str, folder_id: str) -> str:
    service = get_drive_service()
    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    return uploaded_file.get("id")
