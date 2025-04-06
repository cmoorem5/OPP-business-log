import streamlit as st
from utils.data_loader import load_excel_data

def show():
    st.markdown("## 📤 Export Data")
    st.write("Download your income and expense records as CSV files.")

    income_df = load_excel_data("2025 OPP Income")
    expenses_df = load_excel_data("2025 OPP Expenses")

    st.download_button(
        label="📥 Download Income Data",
        data=income_df.to_csv(index=False),
        file_name="income_data.csv",
        mime="text/csv"
    )

    st.download_button(
        label="📥 Download Expense Data",
        data=expenses_df.to_csv(index=False),
        file_name="expense_data.csv",
        mime="text/csv"
    )

    st.markdown("✅ Your data is always available for export and analysis.")
