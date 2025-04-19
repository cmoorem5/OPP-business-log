import streamlit as st
import json
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

def show():
    st.markdown("## 🔍 Credential Debugger")

    try:
        st.write("Loading credentials from secrets...")
        creds_dict = json.loads(st.secrets["gdrive_credentials"])
        st.success("✅ Secrets loaded and parsed.")

        SCOPES = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        creds.refresh(Request())

        st.success("✅ JWT Signature and scopes are valid — Google accepted the token.")
        st.write("Your credentials are fully working.")
        st.json({
            "client_email": creds.service_account_email,
            "project_id": creds.project_id
        })
    except Exception as e:
        st.error(f"❌ Failed to load or validate credentials:\n{e}")
