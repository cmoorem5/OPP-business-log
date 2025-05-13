import streamlit as st
import pandas as pd
from datetime import date
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📂 View Logged Entries")

    # Load data from each tab
    income_df = load_sheet_as_df("2025 OPP Income")
    expense_df = load_sheet_as_df("2025 OPP Expenses")

    # Ensure any “Date” columns are actual datetimes
    for df in (income_df, expense_df):
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])

    # View selector
    view_option = st.radio("View", ["Income", "Expense"], key="view_option")
    if view_option == "Income":
        st.subheader("💰 Income Entries")
        df = income_df.copy()
        is_expense = False
    else:
        st.subheader("💸 Expense Entries")
        df = expense_df.copy()
        is_expense = True
        # Turn receipt URLs into clickable links
        if "Receipt Link" in df.columns:
            df["Receipt Link"] = df["Receipt Link"].apply(
                lambda url: f'<a href="{url}" target="_blank">View Receipt</a>'
                if isinstance(url, str) and url else ""
            )

    # --- Filters ---
    # Property filter
    properties = df["Property"].unique().tolist()
    props = st.multiselect("Property", properties, default=properties)

    # Date range filter (default to current month)
    if "Date" in df.columns:
        today = date.today()
        first_of_month = today.replace(day=1)
        date_range = st.date_input(
            "Date range",
            [first_of_month, today],
            key="date_range"
        )
    else:
        date_range = None

    # Expense‑only filters
    if is_expense and "Complete" in df.columns:
        statuses = st.multiselect(
            "Status", df["Complete"].unique().tolist(),
            default=df["Complete"].unique().tolist()
        )
    else:
        statuses = None

    if is_expense and "Category" in df.columns:
        categories = st.multiselect(
            "Category", df["Category"].unique().tolist(),
            default=df["Category"].unique().tolist()
        )
    else:
        categories = None

    # Apply filters
    mask = df["Property"].isin(props)
    if date_range:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        mask &= df["Date"].between(start, end)
    if statuses is not None:
        mask &= df["Complete"].isin(statuses)
    if categories is not None:
        mask &= df["Category"].isin(categories)

    filtered = df.loc[mask]

    # --- Display ---
    if is_expense and "Receipt Link" in filtered.columns:
        html = filtered.to_html(escape=False, index=False)
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.dataframe(filtered, use_container_width=True)
