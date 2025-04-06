import streamlit as st
from datetime import date
from utils.data_loader import load_excel_data

def show():
    st.markdown("## 📝 Log New Entry")

    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])
    entry_date = st.date_input("Date", date.today())
    amount = st.number_input("Amount", min_value=0.0, value=0.0, step=1.0)
    description = st.text_input("Description or Invoice #")

    if entry_type == "Income":
        source = st.text_input("Income Source")
        rental_dates = st.text_input("Rental Dates (optional)")
    else:
        purchaser = st.text_input("Purchaser")
        item = st.text_input("Item Description")
        expenses_df = load_excel_data("2025 OPP Expenses")
        categories = expenses_df["Category"].dropna().unique() if "Category" in expenses_df.columns else []
        category = st.selectbox("Category", categories if len(categories) else ["General"])
        comments = st.text_area("Comments")

    if st.button("Submit Entry"):
        st.success(f"{entry_type} entry submitted!")
        st.info("Note: This version does not save to the Excel file — saving feature coming soon.")
