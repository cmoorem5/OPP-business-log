import streamlit as st
from datetime import date

from utils.config import SHEET_ID
from utils.log_helpers import build_expense_payload, log_expense
from utils.dropdown_config import INCOME_YEARS, PROPERTIES, EXPENSE_CATEGORIES, PURCHASERS

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
