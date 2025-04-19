import streamlit as st
import pandas as pd
from utils.google_sheets import get_worksheet

def show():
    st.title("📂 View Logged Entries")

    sheet_name = "OPP Finance Tracker"

    # Load Google Sheet data
    income_ws = get_worksheet(sheet_name, "2025 OPP Income")
    expense_ws = get_worksheet(sheet_name, "2025 OPP Expenses")

    income_df = pd.DataFrame(income_ws.get_all_records())
    expense_df = pd.DataFrame(expense_ws.get_all_records())

    # Fix month sort order
    month_order = ["January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]

    if "Month" in income_df.columns:
        income_df["Month"] = pd.Categorical(income_df["Month"], categories=month_order, ordered=True)
        income_df = income_df.sort_values(by="Month")

    if "Month" in expense_df.columns:
        expense_df["Month"] = pd.Categorical(expense_df["Month"], categories=month_order, ordered=True)
        expense_df = expense_df.sort_values(by="Month")

    view_option = st.radio("Select Entry Type", ["Income", "Expense"], horizontal=True)

    if view_option == "Income":
        st.subheader("💰 Income Entries")
        st.dataframe(income_df, use_container_width=True)
    else:
        st.subheader("💸 Expense Entries")

        # Format links as clickable markdown-style strings
        if "Receipt Link" in expense_df.columns:
            expense_df["Receipt Link"] = expense_df["Receipt Link"].apply(
                lambda url: f"[View Receipt]({url})" if isinstance(url, str) and url.startswith("http") else ""
            )

        st.markdown("### Expense Log with Clickable Receipt Links")
        st.markdown(expense_df.to_markdown(index=False), unsafe_allow_html=True)
