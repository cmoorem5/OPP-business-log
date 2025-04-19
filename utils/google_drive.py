import os
import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_file_to_drive(file_path, file_name, folder_id):
    creds_dict = json.loads(st.secrets["gdrive_credentials"])
    creds = Credentials.from_service_account_info(creds_dict)
    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return uploaded_file.get("id")
