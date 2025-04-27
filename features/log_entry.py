import streamlit as st
from datetime import date
from utils.google_sheets import get_worksheet, append_row
from utils.google_drive import upload_file_to_drive
import pandas as pd
import tempfile
import os

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
    st.markdown("## 📝 Log New Entry")
    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])
    entry_date = st.date_input("Date", date.today())
    amount = st.number_input("Amount", min_value=0.0, value=0.0, step=1.0)

    # Income Entry Section
    if entry_type == "Income":
        st.markdown("### 💰 Income Entry")

        source = st.text_input("Income Source")
        rental_dates = st.date_input("Rental Date Range", value=(date.today(), date.today()))
        property_location = st.selectbox("Property", ["Florida", "Maine"])
        payment_status = st.selectbox("Payment Status", [
            "Paid", "Cancelled", "PMT Due", "Downpayment Received"
        ])

        st.markdown("### 👤 Renter Contact Info (Optional)")
        renter_name = st.text_input("Renter Name")
        renter_email = st.text_input("Renter Email")
        renter_address = st.text_input("Address")
        renter_city = st.text_input("City")
        renter_state = st.text_input("State")
        renter_zip = st.text_input("Zip Code")

        if st.button("Submit Income Entry"):
            month = entry_date.strftime("%B")
            rental_range = f"{rental_dates[0]} - {rental_dates[1]}"

            row = [
                month, property_location, rental_range, source, "",  # Description blank
                amount, payment_status, "",  # Notes blank
                renter_name, renter_address, renter_city, renter_state, renter_zip, renter_email
            ]

            append_row("OPP Finance Tracker", "2025 OPP Income", row)
            st.success("Income entry submitted!")

    # Expense Entry Section
    if entry_type == "Expense":
        purchasers_ws = get_worksheet("OPP Finance Tracker", "Purchasers")
        purchasers_df = pd.DataFrame(purchasers_ws.get_all_records())
        purchaser_list = purchasers_df["Purchaser"].dropna().unique().tolist()

        purchaser = st.selectbox("Purchaser", purchaser_list + ["Other"])
        if purchaser == "Other":
            purchaser = st.text_input("Enter Purchaser Name")

        item = st.text_input("Item")
        property_location = st.selectbox("Property", ["Florida", "Maine"])

        expenses_ws = get_worksheet("OPP Finance Tracker", "2025 OPP Expenses")
        expenses_df = pd.DataFrame(expenses_ws.get_all_records())
        categories = expenses_df["Category"].dropna().unique() if "Category" in expenses_df.columns else []
        category = st.selectbox("Category", categories if len(categories) else ["General"])
        comments = st.text_area("Comments")

        uploaded_file = st.file_uploader("Upload Receipt File", type=["pdf", "png", "jpg", "jpeg"])
        receipt_link = ""
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_file_path = tmp_file.name
            try:
                month_name = entry_date.strftime("%B")
                folder_id = monthly_folders_2025.get(month_name)
                if folder_id:
                    file_id = upload_file_to_drive(tmp_file_path, uploaded_file.name, folder_id)
                    receipt_link = f"https://drive.google.com/file/d/{file_id}/view"
            finally:
                os.remove(tmp_file_path)

        row = [entry_date.strftime("%B"), str(entry_date), purchaser, item, property_location, category, amount, comments, receipt_link]
        append_row("OPP Finance Tracker", "2025 OPP Expenses", row)
        st.success("Expense entry submitted!")


    else:
        st.info("Income entry handling can be added here as needed.")
