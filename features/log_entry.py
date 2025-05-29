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
                    "Check-out": c
