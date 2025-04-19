import streamlit as st
import os
import tempfile
from utils.google_drive import upload_file_to_drive

def show():
    st.markdown("## 📸 Upload Receipts to Google Drive")
    uploaded_file = st.file_uploader("Choose a receipt file", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_file_path = tmp_file.name

        try:
            folder_id = "1vbNUWQZcitohosIuhQ7FRRPQl747Mb-V"  # Your Drive folder ID
            credentials_path = "opp-rental-tracker-f7fe7e5ad486.json"
            file_id = upload_file_to_drive(
                file_path=tmp_file_path,
                file_name=uploaded_file.name,
                folder_id=folder_id,
                credentials_path=credentials_path
            )
            st.success("✅ Receipt uploaded to Google Drive.")
            st.markdown(f"[View file in Drive](https://drive.google.com/file/d/{file_id}/view)", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to upload: {e}")
        finally:
            os.remove(tmp_file_path)
