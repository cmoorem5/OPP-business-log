import streamlit as st
from utils.export_helpers import (
    load_and_process_expenses,
    generate_monthly_summary,
    generate_type_totals
)

def show():
    st.title("📊 Recurring vs. One-Time Expenses")
    year = st.radio("Select Year", ["2025", "2026"], horizontal=True)

    try:
        df = load_and_process_expenses(year)
        if df.empty:
            st.warning("No expense data found.")
            return

        st.subheader("Monthly Expense Breakdown")
        summary = generate_monthly_summary(df)
        st.bar_chart(summary)

        st.subheader("📋 Totals by Type")
        totals = generate_type_totals(df)
        st.write(totals.reset_index())

        csv = df.to_csv(index=False)
        st.download_button("Download Full Expense Data", csv, file_name=f"expenses_{year}.csv")

    except Exception as e:
        st.error(f"Failed to load recurring summary: {e}")
