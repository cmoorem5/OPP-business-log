import streamlit as st
from utils.data_loader import load_excel_data

def show():
    st.markdown("## 📤 Export Data")
    income_df = load_excel_data("2025 OPP Income")
    expenses_df = load_excel_data("2025 OPP Expenses")

    st.download_button("📥 Download Income Data", income_df.to_csv(index=False), "income_data.csv", "text/csv")
    st.download_button("📥 Download Expense Data", expenses_df.to_csv(index=False), "expense_data.csv", "text/csv")
