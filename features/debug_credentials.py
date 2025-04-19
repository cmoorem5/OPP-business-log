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

        creds = Credentials.from_service_account_info(creds_dict)
        creds.refresh(Request())

        st.success("✅ JWT Signature is valid — Google accepted the token.")
        st.write("Your credentials are fully working.")
        st.json({
            "client_email": creds.service_account_email,
            "token_uri": creds.token_uri,
            "project_id": creds.project_id
        })
    except Exception as e:
        st.error(f"❌ Failed to load or validate credentials:
{e}")
