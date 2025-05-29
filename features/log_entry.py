import streamlit as st
from datetime import date
from utils.google_sheets import append_row_to_sheet
from utils.google_drive import upload_file_to_drive
from utils.config import get_drive_folder_id


def show():
    st.title("📝 Log New Entry")
    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])

    if entry_type == "Income":
        with st.form("income_form", clear_on_submit=True):
            year = st.selectbox("Log Income To:", ["2025", "2026"], key="income_year")
            sheet_name = f"{year} OPP Income"

            booking_date = st.date_input("Booking Date", date.today())
            rental_dates = st.date_input("Rental Date Range", (date.today(), date.today()))
            check_in, check_out = rental_dates

            amount = st.number_input("Amount Received", min_value=0.0, step=10.0)
            payment_type = st.selectbox("Payment Type", ["Zelle", "Check", "Cash", "Venmo", "Other"])
            status = st.selectbox("Payment Status", ["Paid", "PMT due", "Downpayment received"])
            renter_name = st.text_input("Renter Name")
            email = st.text_input("Renter Email")
            origin = st.text_input("Where are they from?")
            notes = st.text_area("Notes (optional)")

            submitted = st.form_submit_button("Log Income")
            if submitted:
                row = {
                    "Booking Date": booking_date.strftime("%Y-%m-%d"),
                    "Check-in": check_in.strftime("%Y-%m-%d"),
                    "Check-out": check_out.strftime("%Y-%m-%d"),
                    "Amount": amount,
                    "Payment Type": payment_type,
                    "Complete": status,
                    "Renter Name": renter_name,
                    "Email": email,
                    "Location": origin,
                    "Notes": notes,
                }
                append_row_to_sheet(sheet_name, row)
                st.success("✅ Income entry added.")

    elif entry_type == "Expense":
        with st.form("expense_form", clear_on_submit=True):
            year = st.selectbox("Log Expense To:", ["2025", "2026"], key="expense_year")
            sheet_name = f"{year} OPP Expenses"

            expense_date = st.date_input("Date", date.today())
            property_name = st.selectbox("Property", ["Hooked on Islamorada", "Other"])
            category = st.selectbox("Category", ["Mortgage", "Cable/Internet", "Electric", "Repairs", "Supplies", "Other"])
            description = st.text_input("Item/Description")
            amount = st.number_input("Amount", min_value=0.0, step=5.0)
            receipt_file = st.file_uploader("Upload Receipt (optional)", type=["jpg", "jpeg", "png", "pdf"])

            submitted = st.form_submit_button("Log Expense")
            if submitted:
                receipt_link = ""
                if receipt_file:
                    folder_id = get_drive_folder_id(year, expense_date.month)
                    receipt_link = upload_file_to_drive(receipt_file, folder_id)

                row = {
                    "Date": expense_date.strftime("%Y-%m-%d"),
                    "Property": property_name,
                    "Category": category,
                    "Item/Description": description,
                    "Amount": amount,
                    "Receipt": receipt_link,
                }
                append_row_to_sheet(sheet_name, row)
                st.success("✅ Expense entry added.")
