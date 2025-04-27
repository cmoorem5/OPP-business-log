import streamlit as st
from datetime import date
import pandas as pd
import tempfile
import os
from utils.google_sheets import get_worksheet, append_row
from utils.google_drive import upload_file_to_drive

# Map month names → Drive folder IDs
monthly_folders_2025 = {
    "April":    "1wPerZFB-9FufTZOGfFXf2xMVg4VlGtdC",
    "May":      "1e12yCfo8WZS8gnYuSPbxeHiZ1aVWbbJe",
    "June":     "1WRSSZUGPHgGvd1cSUNDEjpTGq2FmrqcZ",
    "July":     "10nWoAibOWzVeWx0Qn3TC8Z6g-UXkToPd",
    "August":   "1xvT2NA9rPpXX0SQ1CKE9NeTbc9mvrgxK",
    "September":"160isZV8ja5Kgw7sKx88f969tIUZR6Jfo",
    "October":  "1XbP4T78e71CYA5s-1ksPYK6bujmo-UQn",
    "November": "1zxxtG1cwvpcckQ3nvB3zKHStxDBfRFF6",
    "December": "1iJwfC3siEudH8uzdZGwlid6ufhFG5AMb"
}

def show():
    st.markdown("## 📝 Log New Entry")
    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])

    # ── INCOME FORM ───────────────────────────────────────────────────────────
    if entry_type == "Income":
        with st.form("income_form", clear_on_submit=True):
            entry_date = st.date_input("Date", date.today(), key="income_date")
            amount     = st.number_input("Amount", min_value=0.0, step=1.0, key="income_amount")

            source     = st.text_input("Income Source")
            rental_dates = st.date_input(
                "Rental Date Range", 
                value=(date.today(), date.today()), 
                key="rental_dates"
            )
            property_location = st.selectbox(
                "Property", ["Florida", "Maine"], key="income_property"
            )
            payment_status = st.selectbox(
                "Payment Status",
                ["Paid", "Cancelled", "PMT Due", "Downpayment Received"],
                key="payment_status"
            )

            st.markdown("### 👤 Renter Contact Info (Optional)")
            renter_name    = st.text_input("Renter Name")
            renter_email   = st.text_input("Renter Email")
            renter_address = st.text_input("Address")
            renter_city    = st.text_input("City")
            renter_state   = st.text_input("State")
            renter_zip     = st.text_input("Zip Code")

            submitted = st.form_submit_button("Submit Income Entry")
            if submitted:
                month = entry_date.strftime("%B")
                rental_range = f"{rental_dates[0]} - {rental_dates[1]}"
                row = [
                    month,
                    property_location,
                    rental_range,
                    source,
                    "",           # Description blank
                    amount,
                    payment_status,
                    "",           # Notes blank
                    renter_name,
                    renter_address,
                    renter_city,
                    renter_state,
                    renter_zip,
                    renter_email
                ]
                append_row("OPP Finance Tracker", "2025 OPP Income", row)
                st.success("Income entry submitted!")

    # ── EXPENSE FORM ──────────────────────────────────────────────────────────
    elif entry_type == "Expense":
        with st.form("expense_form", clear_on_submit=True):
            entry_date = st.date_input("Date", date.today(), key="expense_date")
            amount     = st.number_input("Amount", min_value=0.0, step=1.0, key="expense_amount")

            # Purchaser dropdown + “Other”
            purchasers_ws = get_worksheet("OPP Finance Tracker", "Purchasers")
            purchaser_list = sorted(
                pd.DataFrame(purchasers_ws.get_all_records())["Purchaser"]
                .dropna()
                .unique()
            )
            purchaser_list.append("Other")
            purchaser = st.selectbox("Purchaser", purchaser_list)
            if purchaser == "Other":
                purchaser = st.text_input("Enter Purchaser Name")

            item              = st.text_input("Item/Description")
            property_location = st.selectbox("Property", ["Florida", "Maine"])

            # Category dropdown + “Other”
            expenses_ws = get_worksheet("OPP Finance Tracker", "2025 OPP Expenses")
            cat_df = pd.DataFrame(expenses_ws.get_all_records())
            categories = (
                sorted(cat_df["Category"].dropna().unique())
                if "Category" in cat_df.columns
                else []
            )
            categories.append("Other")
            category = st.selectbox("Category", categories)
            if category == "Other":
                category = st.text_input("Enter Category")

            comments      = st.text_area("Comments")
            uploaded_file = st.file_uploader(
                "Upload Receipt File", 
                type=["pdf", "png", "jpg", "jpeg"]
            )

            # Handle Drive upload
            receipt_link = ""
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                try:
                    folder_id = monthly_folders_2025.get(entry_date.strftime("%B"))
                    if folder_id:
                        file_id = upload_file_to_drive(
                            tmp_path, uploaded_file.name, folder_id
                        )
                        receipt_link = f"https://drive.google.com/file/d/{file_id}/view"
                finally:
                    os.remove(tmp_path)

            submitted = st.form_submit_button("Submit Expense Entry")
            if submitted:
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
