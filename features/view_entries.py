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

    view_option = st.radio("Select Entry Type", ["Income", "Expense"], horizontal=True)

    if view_option == "Income":
        st.subheader("💰 Income Entries")
        st.dataframe(income_df, use_container_width=True)
    else:
        st.subheader("💸 Expense Entries")

        # Convert links to clickable markdown
        if "Receipt Link" in expense_df.columns:
            expense_df["Receipt Link"] = expense_df["Receipt Link"].apply(
                lambda url: f"[View]({url})" if url else ""
            )

        st.dataframe(expense_df, use_container_width=True)
