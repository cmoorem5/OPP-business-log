import streamlit as st
import os
import tempfile
from datetime import date
from utils.google_drive import upload_file_to_drive

monthly_folders_2025 = {
    "April": "1wPerZFB-9FufTZOGfFXf2xMVg4VlGtdC",
    "May": "1e12yCfo8WZS8gnYuSPbxeHiZ1aVWbbJe",
    "June": "1WRSSZUGPHgGvd1cSUNDEjpTGq2FmrqcZ",
    "July": "10nWoAibOWzVeWx0Qn3TC8Z6g-UXkToPd",
    "August": "1xvT2NA9rPpXX0SQ1CKE9NeTbc9mvrgxK",
    "September": "160isZV8ja5Kgw7sKx88f969tIUZR6Jfo",
    "October": "1XbP4T78e71CYA5s-1ksPYK6bujmo-UQn",
    "November": "1zxxtG1cwvpcckQ3nvB3zKHStxDBfRFF6",
    "December": "1iJwfC3siEudH8uzdZGwlid6ufhFG5AMb"
}

def show():
    st.markdown("## 📸 Upload Receipts to Monthly Folder")

    uploaded_file = st.file_uploader("Choose a receipt file", type=["pdf", "png", "jpg", "jpeg"])
    receipt_date = st.date_input("Date of Receipt", value=date.today())
    selected_year = receipt_date.year

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_file_path = tmp_file.name

        try:
            month_name = receipt_date.strftime("%B")

            if selected_year == 2025:
                folder_id = monthly_folders_2025.get(month_name)
                if not folder_id:
                    st.error("No folder found for {} 2025.".format(month_name))
                    return
            else:
                st.warning("Only 2025 monthly folders are configured. File not uploaded.")
                return

            file_id = upload_file_to_drive(
                file_path=tmp_file_path,
                file_name=uploaded_file.name,
                folder_id=folder_id
            )
            st.success("✅ File uploaded to {} 2025 folder.".format(month_name))
            st.markdown("📁 [View file in Drive](https://drive.google.com/file/d/{}/view)".format(file_id), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to upload: {e}")
        finally:
            os.remove(tmp_file_path)
