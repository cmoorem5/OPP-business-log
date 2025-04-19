import streamlit as st
from datetime import date
from utils.data_loader import load_excel_data
from utils.google_sheets import append_row
from utils.google_drive import upload_file_to_drive
import os
import tempfile

def show():
    st.markdown("## 📝 Log New Entry")

    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])
    entry_date = st.date_input("Date", date.today())
    amount = st.number_input("Amount", min_value=0.0, value=0.0, step=1.0)

    if entry_type == "Income":
        source = st.text_input("Income Source")
        rental_dates = st.date_input("Rental Date Range", value=(date.today(), date.today()))

        st.markdown("### 👤 Renter Details")
        renter_name = st.text_input("Renter Name")
        renter_email = st.text_input("Email Address")
        renter_location = st.text_input("Where are they from?")
        property_location = st.selectbox("Property", ["Florida", "Maine"])
    else:
        purchasers_df = load_excel_data("Purchasers")
        purchaser_list = purchasers_df["Purchaser"].dropna().unique().tolist()
        purchaser = st.selectbox("Purchaser", purchaser_list + ["Other"])
        if purchaser == "Other":
            purchaser = st.text_input("Enter Purchaser Name")

        item = st.text_input("Item")
        property_location = st.selectbox("Property", ["Florida", "Maine"])

        expenses_df = load_excel_data("2025 OPP Expenses")
        categories = expenses_df["Category"].dropna().unique() if "Category" in expenses_df.columns else []
        category = st.selectbox("Category", categories if len(categories) else ["General"])
        comments = st.text_area("Comments")

        st.markdown("### 📎 Upload Receipt (optional)")
        uploaded_file = st.file_uploader("Upload Receipt File", type=["pdf", "png", "jpg", "jpeg"])
        receipt_link = ""

        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_file_path = tmp_file.name

            try:
                receipt_folder_id = "1olfna0Ob8u8LBnxG9Gz0hDW8Eyzxc5Tt"  # 2025 folder
                file_id = upload_file_to_drive(
                    file_path=tmp_file_path,
                    file_name=uploaded_file.name,
                    folder_id=receipt_folder_id
                )
                receipt_link = f"https://drive.google.com/file/d/{file_id}/view"
            except Exception as e:
                st.warning(f"Receipt upload failed: {e}")
            finally:
                os.remove(tmp_file_path)

    if st.button("Submit Entry"):
        try:
            sheet_name = "OPP Finance Tracker"

            if entry_type == "Income":
                tab_name = "2025 OPP Income"
                month = entry_date.strftime("%B")
                row = [
                    month, str(entry_date), source,
                    str(rental_dates[0]), str(rental_dates[1]),
                    renter_name, renter_email, renter_location,
                    property_location
                ]
            else:
                tab_name = "2025 OPP Expenses"
                month = entry_date.strftime("%B")
                row = [
                    month, str(entry_date), purchaser, item,
                    property_location, category, amount, comments, receipt_link
                ]

            response = append_row(sheet_name, tab_name, row)
            if response is None or (hasattr(response, "status_code") and response.status_code == 200):
                st.success(f"{entry_type} entry submitted and saved to Google Sheets!")
            else:
                st.warning(f"Entry submitted but returned: {response}")
        except Exception as e:
            st.error(f"Failed to save entry: {e}")
