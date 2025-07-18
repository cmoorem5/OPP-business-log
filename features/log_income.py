import streamlit as st
from datetime import date

from utils.log_helpers import build_income_payload, log_income
from utils.config import YEARS as INCOME_YEARS, PAYMENT_STATUS, PROPERTIES, SHEET_ID
from utils.google_sheets import load_sheet_as_df

@st.cache_data(ttl=600)
def get_unique_income_sources(sheet_name):
    try:
        df = load_sheet_as_df(SHEET_ID, sheet_name)
        return sorted(df["Income Source"].dropna().unique().tolist())
    except Exception:
        return []

def show_income_form():
    try:
        with st.form("income_form", clear_on_submit=True):
            year = st.selectbox("Log Income To:", INCOME_YEARS, key="income_year")
            sheet_name = f"{year} OPP Income"
            income_sources = get_unique_income_sources(sheet_name)

            booking_date = st.date_input("Booking Date", date.today())
            rental_dates = st.date_input("Rental Date Range", (date.today(), date.today()))
            check_in, check_out = rental_dates

            amount_owed = st.number_input("Amount Owed", min_value=0.0, step=10.0)
            amount_received = st.number_input("Amount Received", min_value=0.0, step=10.0)
            status = st.selectbox("Payment Status", PAYMENT_STATUS)

            renter_name = st.text_input("Renter Name")
            email = st.text_input("Renter Email")
            phone = st.text_input("Phone")
            address = st.text_input("Address")
            city = st.text_input("City")
            state = st.text_input("State")
            zip_code = st.text_input("Zip Code")

            property_name = st.selectbox("Property", PROPERTIES)
            income_source = st.selectbox("Income Source", income_sources) if income_sources else st.text_input("Income Source")
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Log Income"):
                row_dict = build_income_payload(
                    booking_date=booking_date,
                    check_in=check_in,
                    check_out=check_out,
                    amount_owed=amount_owed,
                    amount_received=amount_received,
                    status=status,
                    renter_name=renter_name,
                    email=email,
                    phone=phone,
                    address=address,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    property_name=property_name,
                    income_source=income_source,
                    notes=notes
                )
                log_income(sheet_name, row_dict)
                st.success("✅ Income logged successfully.")
                st.rerun()
    except Exception as e:
        st.error(f"❌ Income form crashed: {e}")
