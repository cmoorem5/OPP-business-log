import streamlit as st
from datetime import date
from utils.google_sheets import get_worksheet, append_row
from utils.google_drive import upload_file_to_drive
import pandas as pd
import tempfile
import os

monthly_folders_2025 = {
    "April": "1wPerZFB-9FufTZOGfFXf2xMVg4VlGtdC",
    # … rest of your month → folder_id map …
}

def show():
    st.markdown("## 📝 Log New Entry")
    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])
    entry_date = st.date_input("Date", date.today())
    amount = st.number_input("Amount", min_value=0.0, value=0.0, step=1.0)

    if entry_type == "Income":
        st.markdown("### 💰 Income Entry")
        # … your existing Income code here …

    elif entry_type == "Expense":
        st.markdown("### 💸 Expense Entry")
        with st.form("expense_form"):
            # --- Dropdowns & inputs ---
            purchasers_ws = get_worksheet("OPP Finance Tracker", "Purchasers")
            purchasers_df = pd.DataFrame(purchasers_ws.get_all_records())
            purchaser_list = sorted(purchasers_df["Purchaser"].dropna().unique()) + ["Other"]

            purchaser = st.selectbox("Purchaser", purchaser_list)
            if purchaser == "Other":
                purchaser = st.text_input("Enter Purchaser Name")

            item = st.text_input("Item/Description")
            property_location = st.selectbox("Property", ["Florida", "Maine"])

            expenses_ws = get_worksheet("OPP Finance Tracker", "2025 OPP Expenses")
            expenses_df = pd.DataFrame(expenses_ws.get_all_records())
            categories = sorted(expenses_df["Category"].dropna().unique()) if "Category" in expenses_df.columns else []
            category = st.selectbox("Category", categories + ["Other"])
            if category == "Other":
                category = st.text_input("Enter Category")

            comments = st.text_area("Comments")
            uploaded_file = st.file_uploader("Upload Receipt", type=["pdf", "png", "jpg", "jpeg"])

            submitted = st.form_submit_button("Submit Expense Entry")
            if submitted:
                # build Drive link
                receipt_link = ""
                if uploaded_file:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        tmp_path = tmp.name
                    try:
                        month_name = entry_date.strftime("%B")
                        folder_id = monthly_folders_2025.get(month_name)
                        if folder_id:
                            file_id = upload_file_to_drive(tmp_path, uploaded_file.name, folder_id)
                            receipt_link = f"https://drive.google.com/file/d/{file_id}/view"
                    finally:
                        os.remove(tmp_path)

                # append row
                row = [
                    entry_date.strftime("%B"),
                    str(entry_date),
                    purchaser,
                    item,
                    property_location,
                    category,
                    amount,
                    comments,
                    receipt_link,
                ]
                append_row("OPP Finance Tracker", "2025 OPP Expenses", row)
                st.success("Expense entry submitted!")

    else:
        st.info("Please select an entry type to get started.")



    else:
        st.info("Income entry handling can be added here as needed.")
