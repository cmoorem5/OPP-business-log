import streamlit as st
from datetime import date, datetime
import tempfile
import os

from utils.google_sheets import load_sheet_as_df, append_row
from utils.google_drive import upload_file_to_drive
from utils.config import get_drive_folder_id

def show():
    """Log a new income or expense entry with optional receipt upload."""
    st.title("📝 Log New Entry")

    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])

    if entry_type == "Income":
        # ─── INCOME FORM ───────────────────────────────────────────────
        with st.form("income_form", clear_on_submit=True):
            entry_date = st.date_input("Date", date.today(), key="income_date")
            amount = st.number_input("Amount", min_value=0.0, step=0.01, key="income_amount")
            source = st.text_input("Income Source", key="income_source")
            rental_dates = st.date_input(
                "Rental Date Range",
                (date.today(), date.today()),
                key="rental_dates"
            )
            property_location = st.selectbox(
                "Property",
                ["Florida", "Maine"],
                key="income_property"
            )
            payment_status = st.selectbox(
                "Payment Status",
                ["Paid", "Cancelled", "PMT Due", "Downpayment Received"],
                key="payment_status"
            )

            st.markdown("#### 👤 Renter Contact Info (Optional)")
            renter_name    = st.text_input("Renter Name", key="renter_name")
            renter_email   = st.text_input("Renter Email", key="renter_email")
            renter_address = st.text_input("Address", key="renter_address")
            renter_city    = st.text_input("City", key="renter_city")
            renter_state   = st.text_input("State", key="renter_state")
            renter_zip     = st.text_input("Zip Code", key="renter_zip")

            submitted = st.form_submit_button("Submit Income Entry")

        if submitted:
            errors = []
            if entry_date > date.today():
                errors.append("❗ Date cannot be in the future.")
            if amount <= 0:
                errors.append("❗ Amount must be greater than zero.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                month        = entry_date.strftime("%B")
                rental_range = f"{rental_dates[0]} - {rental_dates[1]}"
                row = [
                    month,
                    property_location,
                    rental_range,
                    source,
                    "",            # placeholder for any unused column
                    amount,
                    payment_status,
                    "",            # placeholder
                    renter_name,
                    renter_address,
                    renter_city,
                    renter_state,
                    renter_zip,
                    renter_email,
                ]
                with st.spinner("Submitting income entry..."):
                    append_row("2025 OPP Income", row)
                st.success("✅ Income entry submitted!")

    else:
        # ─── EXPENSE FORM ───────────────────────────────────────────────
        with st.spinner("Loading dropdown data..."):
            purchasers_df_
