import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents"
]

def _get_credentials():
    creds_raw = st.secrets["gdrive_credentials"]
    creds_dict = json.loads(creds_raw) if isinstance(creds_raw, str) else creds_raw
    return service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

def _get_docs_service():
    creds = _get_credentials()
    return build("docs", "v1", credentials=creds)

def _get_drive_service():
    creds = _get_credentials()
    return build("drive", "v3", credentials=creds)

def generate_rental_agreement_doc(
    renter_name: str,
    start_date: str,
    end_date: str,
    full_cost: float,
    down_payment: float,
    total_due: float,
    pet_fee: float,
    email: str,
    output_folder_id: str
) -> str:
    template_id = "1HIE5iVfK6gMHUfb9gprb5TLcCB-4R3WkLMk2UFr1fCo"  # Short-Term Rental Agreement

    drive_service = _get_drive_service()
    docs_service = _get_docs_service()

    title = f"{renter_name} Rental Agreement - {start_date}"
    copy = drive_service.files().copy(
        fileId=template_id,
        body={"name": title, "parents": [output_folder_id]}
    ).execute()
    new_doc_id = copy["id"]

    requests = [
        {"replaceAllText": {"containsText": {"text": "{{Renter Name}}", "matchCase": True}, "replaceText": renter_name}},
        {"replaceAllText": {"containsText": {"text": "{{Start Date}}", "matchCase": True}, "replaceText": start_date}},
        {"replaceAllText": {"containsText": {"text": "{{End Date}}", "matchCase": True}, "replaceText": end_date}},
        {"replaceAllText": {"containsText": {"text": "{{Full Cost}}", "matchCase": True}, "replaceText": f"${full_cost:.2f}"}},
        {"replaceAllText": {"containsText": {"text": "{{Down Payment}}", "matchCase": True}, "replaceText": f"${down_payment:.2f}"}},
        {"replaceAllText": {"containsText": {"text": "{{Total Due}}", "matchCase": True}, "replaceText": f"${total_due:.2f}"}},
        {"replaceAllText": {"containsText": {"text": "{{Pet Fee}}", "matchCase": True}, "replaceText": f"${pet_fee:.2f}"}},
        {"replaceAllText": {"containsText": {"text": "{{Email}}", "matchCase": True}, "replaceText": email}},
    ]

    docs_service.documents().batchUpdate(documentId=new_doc_id, body={"requests": requests}).execute()

    return f"https://docs.google.com/document/d/{new_doc_id}/edit"
