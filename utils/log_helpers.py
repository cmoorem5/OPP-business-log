import streamlit as st
from datetime import date

from utils.config import SHEET_ID
    build_income_payload,
    build_expense_payload,
    log_income,
    log_expense
)
from utils.dropdown_config import INCOME_YEARS, PROPERTIES, INCOME_SOURCES, PAYMENT_STATUS, EXPENSE_CATEGORIES, PURCHASERS


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


def show_expense_form():
    with st.form("expense_form", clear_on_submit=True):
        year = st.selectbox("Log Expense To:", INCOME_YEARS, key="expense_year")
        sheet_name = f"{year} OPP Expenses"

        expense_date = st.date_input("Expense Date", date.today())
        purchaser = st.selectbox("Purchaser", PURCHASERS)
        item = st.text_input("Item/Description")
        property_selected = st.selectbox("Property", PROPERTIES)
        category = st.selectbox("Category", EXPENSE_CATEGORIES)
        amount = st.number_input("Amount", min_value=0.0, step=10.0)
        comments = st.text_area("Comments (optional)")
        receipt_file = st.file_uploader("Upload Receipt", type=["jpg", "jpeg", "png", "pdf"])

        if st.form_submit_button("Log Expense"):
            try:
                row_dict = build_expense_payload(
                    expense_date, purchaser, item, property_selected,
                    category, amount, comments, receipt_file
                )
                log_expense(sheet_name, row_dict)
                st.success("✅ Expense logged successfully.")
            except Exception as e:
                st.error(f"❌ Upload failed: {e}")
