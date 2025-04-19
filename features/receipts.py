import streamlit as st
import os
import tempfile
from datetime import date
from utils.google_drive import upload_file_to_drive

def show():
    st.markdown("## 📸 Upload Receipts by Year")

    uploaded_file = st.file_uploader("Choose a receipt file", type=["pdf", "png", "jpg", "jpeg"])
    selected_year = st.selectbox("Select Receipt Year", ["2024", "2025"], index=1)

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_file_path = tmp_file.name

        try:
            folder_map = {
                "2024": "1EzfFR_Gscz1hKvnfUr6X0JUrAIfWm5sK",
                "2025": "1olfna0Ob8u8LBnxG9Gz0hDW8Eyzxc5Tt"
            }
            credentials_path = "opp-rental-tracker-f7fe7e5ad486.json"
            folder_id = folder_map[selected_year]

            file_id = upload_file_to_drive(
                file_path=tmp_file_path,
                file_name=uploaded_file.name,
                folder_id=folder_id,
                credentials_path=credentials_path
            )
            st.success(f"✅ File uploaded to {selected_year} folder in Google Drive.")
            st.markdown(f"[View file in Drive](https://drive.google.com/file/d/{file_id}/view)", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to upload: {e}")
        finally:
            os.remove(tmp_file_path)
