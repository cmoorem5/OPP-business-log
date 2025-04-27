import streamlit as st
import os
import tempfile
from datetime import date

from utils.google_drive import upload_file_to_drive
from utils.config       import get_drive_folder_id

def show():
    st.markdown("## 📸 Upload Receipt to Monthly Folder")

    uploaded_file = st.file_uploader(
        "Choose a receipt file",
        type=["pdf", "png", "jpg", "jpeg"],
        key="receipt_uploader"
    )
    receipt_date = st.date_input("Date of Receipt", value=date.today(), key="receipt_date")
    if receipt_date > date.today():
        st.error("❗ Date cannot be in the future.")
        return

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_file_path = tmp_file.name

        try:
            folder_id = get_drive_folder_id(receipt_date)
            if not folder_id:
                st.warning(
                    f"No folder configured for {receipt_date.year} "
                    f"{receipt_date.strftime('%B')}. File not uploaded."
                )
                return

            file_id = upload_file_to_drive(
                file_path=tmp_file_path,
                file_name=uploaded_file.name,
                folder_id=folder_id
            )
            st.success(f"✅ File uploaded to {receipt_date.strftime('%B')} {receipt_date.year} folder.")
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            st.markdown(f"📁 [View file in Drive]({drive_url})", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Failed to upload: {e}")

        finally:
            os.remove(tmp_file_path)

