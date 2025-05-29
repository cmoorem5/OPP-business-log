import streamlit as st
from datetime import date, datetime
import tempfile
import os
import pandas as pd

from utils.google_sheets import load_sheet_as_df, get_worksheet
from utils.google_drive import upload_file_to_drive
from utils.config import get_drive_folder_id
from utils.google_docs import generate_rental_agreement_doc

def show():
    st.title("📝 Log New Entry")
    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])

    if entry_type == "Income":
        with st.form("income_form", clear_on_submit=True):
            year = st.selectbox("Log Income To:", ["2025", "2026"], key="income_year")
            sheet_name = f"{year} OPP Income"

            booking_date = st.date_input("Booking Date (when reservation made)", date.today(), key="booking_date")
            month = booking_date.strftime("%B")
            rental_dates = st.date_input("Rental Date Range", (date.today(), date.today()), key="rental_dates")
            check_in = rental_dates[0].strftime("%Y-%m-%d")
            check_out = rental_dates[1].strftime("%Y-%m-%d")
            property_location = st.selectbox("Property", ["Florida", "Maine"], key="income_property")
            source = st.text_input("Income Source", key="income_source")
            amount_owed = st.number_input("Amount Owed", min_value=0.0, step=0.01, key="income_amount_owed")
            amount_received = st.number_input("Amount Received", min_value=0.0, step=0.01, key="income_amount_received")
            pet_fee = st.number_input("Pet Fee (if any)", min_value=0.0, step=0.01, key="income_pet_fee")
            status = st.selectbox("Payment Status", ["Paid", "Cancelled", "PMT Due", "Downpayment Received"], key="income_status")

            st.markdown("#### 👤 Renter Contact Info")
            renter_name = st.text_input("Name", key="renter_name")
            renter_address = st.text_input("Address", key="renter_address")
            renter_city = st.text_input("City", key="renter_city")
            renter_state = st.text_input("State", key="renter_state")
            renter_zip = st.text_input("Zip", key="renter_zip")
            renter_phone = st.text_input("Phone", key="renter_phone")
            renter_email = st.text_input("Email", key="renter_email")
            notes = st.text_area("Notes", key="income_notes")

            st.markdown("#### 📄 Document Options")
            generate_agreement = st.checkbox("Generate Rental Agreement")

            submitted = st.form_submit_button("Submit Income Entry")

        if submitted:
            errors = []
            if amount_owed <= 0:
                errors.append("❗ Amount Owed must be greater than zero.")
            if amount_received < 0:
                errors.append("❗ Amount Received cannot be negative.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                ws = get_worksheet(sheet_name)
                headers = ws.row_values(1)
                balance = round(amount_owed - amount_received, 2)

                row_dict = {
                    "Month": month,
                    "Name": renter_name,
                    "Address": renter_address,
                    "City": renter_city,
                    "State": renter_state,
                    "Zip": renter_zip,
                    "Phone": renter_phone,
                    "Email": renter_email,
                    "Check-in": check_in,
                    "Check-out": check_out,
                    "Property": property_location,
                    "Income Source": source,
                    "Amount Owed": amount_owed,
                    "Amount Received": amount_received,
                    "Pet Fee": pet_fee,
                    "Balance": balance,
                    "Status": status,
                    "Notes": notes,
                }
                row = [row_dict.get(col, "") for col in headers]
                with st.spinner(f"Submitting income entry to {sheet_name}..."):
                    ws.append_row(row, value_input_option="USER_ENTERED")
                st.success(f"✅ Income entry submitted to {sheet_name}!")

                if generate_agreement:
                    try:
                        doc_link = generate_rental_agreement_doc(
                            renter_name=renter_name,
                            start_date=check_in,
                            end_date=check_out,
                            full_cost=amount_owed,
                            down_payment=amount_received,
                            total_due=balance,
                            pet_fee=pet_fee,
                            email=renter_email,
                            output_folder_id="1KLhZ10jf_hgBxtWGPBIL4iSfVzxSFg8h"
                        )
                        st.success("Rental agreement generated.")
                        st.markdown(f"[📄 View Agreement]({doc_link})", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Failed to generate agreement: {e}")

    else:
        # EXPENSE FORM SECTION — unchanged from your latest version
        # If you want me to update the Expense part as well, let me know.
        pass

    st.markdown("---")
    last = datetime.now().strftime("%B %d, %Y %I:%M %p")
    st.markdown(
        f'<div style="text-align:center; color:gray; font-size:0.85em;">'
        f'Oceanview Property Partners • v1.3.0 • Last updated: {last}'
        f'</div>',
        unsafe_allow_html=True
    )
