import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df


def show():
    st.title("📂 View Logged Entries")

    # Load data
    sheet = "OPP Finance Tracker"
    income_df = load_sheet_as_df(sheet, "2025 OPP Income")
    expense_df = load_sheet_as_df(sheet, "2025 OPP Expenses")

    # Ensure date columns
    for df in (income_df, expense_df):
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])

    # View selector
    view_option = st.radio("View", ["Income", "Expense"], key="view_option")

    if view_option == "Income":
        st.subheader("💰 Income Entries")
        df = income_df.copy()
        filter_status = False
    else:
        st.subheader("💸 Expense Entries")
        df = expense_df.copy()
        filter_status = True
        # Convert receipt URLs into markdown links
        if "Receipt Link" in df.columns:
            df["Receipt Link"] = df["Receipt Link"].apply(
                lambda url: f"<a href=\"{url}\" target=\"_blank\">View Receipt</a>" if isinstance(url, str) and url else ""
            )

    # --- Filters ---
    # Property filter
    props = st.multiselect(
        "Property", df["Property"].unique(), default=df["Property"].unique()
    )
    # Date range filter
    if "Date" in df.columns:
        date_min, date_max = df["Date"].min(), df["Date"].max()
        date_range = st.date_input(
            "Date range", [date_min, date_max]
        )
    else:
        date_range = None

    # Status filter (only for Expense)
    if filter_status and "Complete" in df.columns:
        statuses = st.multiselect(
            "Status", df["Complete"].unique(), default=df["Complete"].unique()
        )
    else:
        statuses = None

    # Category filter (only for Expense)
    if filter_status and "Category" in df.columns:
        categories = st.multiselect(
            "Category", df["Category"].unique(), default=df["Category"].unique()
        )
    else:
        categories = None

    # Apply filters to DataFrame
    mask = df["Property"].isin(props)
    if date_range:
        mask &= df["Date"] >= pd.to_datetime(date_range[0])
        mask &= df["Date"] <= pd.to_datetime(date_range[1])
    if statuses is not None:
        mask &= df["Complete"].isin(statuses)
    if categories is not None:
        mask &= df["Category"].isin(categories)

    filtered = df.loc[mask]

    # --- Display ---
    if filter_status and "Receipt Link" in filtered.columns:
        # Render clickable links in HTML table
        html = filtered.to_html(escape=False, index=False)
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.dataframe(filtered, use_container_width=True)

