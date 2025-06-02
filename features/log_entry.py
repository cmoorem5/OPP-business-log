import streamlit as st
from features.log_income import show_income_form
from features.log_expense import show_expense_form

def show():
    st.title("📝 Log New Entry")
    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])

    if entry_type == "Income":
        show_income_form()
    elif entry_type == "Expense":
        show_expense_form()
