import streamlit as st
import pandas as pd
from datetime import datetime
from utils.google_sheets import load_sheet_as_df, append_row_to_sheet
from utils.drive_utils import generate_drive_link

def show():
    st.header("🧾 Renter Activity")

    year = st.selectbox("Select Year", ["2025", "2026"], index=0)
    sheet_name = f"{year} OPP Income"
    df = load_sheet_as_df(sheet_name)

    st.subheader("Add Payment or Update Renter Info")

    with st.form("renter_activity_form"):
        renter_name = st.text_input("Renter Name")
        email = st.text_input("Email Address")
        origin = st.text_input("Location (City, State)")
        property_name = st.selectbox("Property", sorted(df["Property"].dropna().unique()))
        amount = st.number_input("Payment Amount", min_value=0.0, step=10.0)
        start_date = st.date_input("Rental Start Date")
        end_date = st.date_input("Rental End Date")
        payment_status = st.selectbox("Payment Status", ["Paid", "PMT due", "Downpayment received"])
        notes = st.text_area("Additional Notes (optional)")
        submitted = st.form_submit_button("Submit")

    if submitted:
        new_entry = {
            "Date Submitted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Renter Name": renter_name,
            "Email": email,
            "Location": origin,
            "Property": property_name,
            "Amount": amount,
            "Rental Start": start_date.strftime("%Y-%m-%d"),
            "Rental End": end_date.strftime("%Y-%m-%d"),
            "Complete": payment_status,
            "Notes": notes
        }

        append_row_to_sheet(sheet_name, new_entry)
        st.success("Renter info and payment logged successfully.")
