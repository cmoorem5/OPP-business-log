import streamlit as st
from datetime import date

from utils.config import SHEET_ID
from utils.log_helpers import build_income_payload, log_income
from utils.dropdown_config import INCOME_YEARS, INCOME_SOURCES, PAYMENT_STATUS

def show_income_form():
    with st.form("income_form", clear_on_submit=True):
        year = st.selectbox("Log Income To:", INCOME_YEARS, key="income_year")
        sheet_name = f"{year} OPP Income"

        booking_date = st.date_input("Booking Date", date.today())
        rental_dates = st.date_input("Rental Date Range", (date.today(), date.today()))
        check_in, check_out = rental_dates

        amount = st.number_input("Amount Received", min_value=0.0, step=10.0)
        payment_type = st.selectbox("Payment Type", INCOME_SOURCES)
        status = st.selectbox("Payment Status", PAYMENT_STATUS)

        renter_name = st.text_input("Renter Name")
        email = st.text_input("Renter Email")
        phone = st.text_input("Phone Number")
        origin = st.text_input("Where are they from?")
        notes = st.text_area("Notes (optional)")

        if st.form_submit_button("Log Income"):
            row_dict = build_income_payload(
                booking_date, check_in, check_out, amount, payment_type,
                status, renter_name, email, phone, origin, notes
            )
            log_income(sheet_name, row_dict)
            st.success("✅ Income logged successfully.")
