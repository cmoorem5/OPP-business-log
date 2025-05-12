import streamlit as st
from datetime import date, datetime
import tempfile
import os

from utils.google_drive import upload_file_to_drive
from utils.config import get_drive_folder_id

def show():
    """Upload a receipt file into the proper Google Drive folder by date."""
    st.title("📸 Upload Receipt to Drive")

    # ─── Date Input & Validation ──────────────────────────────────────────
    receipt_date = st.date_input("Date of Receipt", date.today(), key="receipt_date")
    if receipt_date > date.today():
        st.error("❗ Date cannot be in the future.")
        return

    # ─── File Uploader ────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Choose a receipt file",
        type=["pdf", "png", "jpg", "jpeg"],
        key="receipt_uploader"
    )
    if not uploaded_file:
        return  # nothing to do yet

    # ─── Save temp file & Upload ─────────────────────────────────────────
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    try:
        with st.spinner("Finding Drive folder..."):
            folder_id = get_drive_folder_id(receipt_date)

        if not folder_id:
            st.warning(
                f"No folder configured for {receipt_date.strftime('%B %Y')}. "
                "Receipt not uploaded."
            )
            return

        with st.spinner("Uploading receipt to Drive..."):
            file_id = upload_file_to_drive(tmp_path, uploaded_file.name, folder_id)

        st.success("✅ File successfully uploaded!")
        drive_url = f"https://drive.google.com/file/d/{file_id}/view"
        st.markdown(f"📁 [View in Drive]({drive_url})")

    except Exception as e:
        st.error(f"Failed to upload receipt: {e}")

    finally:
        os.remove(tmp_path)

    # ─── Custom footer ─────────────────────────────────────────────────────
    st.markdown("---")
    last_updated = datetime.now().strftime("%B %d, %Y %I:%M %p")
    footer_md = f"""
    <div style="text-align:center; font-size:0.85em; color:gray;">
      Oceanview Property Partners • v1.3.0 • Last updated: {last_updated}
    </div>
    """
    st.markdown(footer_md, unsafe_allow_html=True)
