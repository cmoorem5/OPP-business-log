import streamlit as st
import pandas as pd
from datetime import date
from utils.google_sheets import load_sheet_as_df

def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    1) Drop columns whose header is blank/whitespace.
    2) Ensure all column names are unique by appending _1, _2, etc.
    """
    # 1) drop blank headers
    df = df.loc[:, df.columns.str.strip() != ""]

    # 2) dedupe names
    counts = {}
    new_cols = []
    for col in df.columns:
        if col in counts:
            counts[col] += 1
            new_cols.append(f"{col}_{counts[col]}")
        else:
            counts[col] = 0
            new_cols.append(col)
    df.columns = new_cols
    return df

def show():
    st.title("📂 View Logged Entries")

    # Load and clean both sheets
    income_df  = _clean_df(load_sheet_as_df("2025 OPP Income"))
    expense_df = _clean_df(load_sheet_as_df("2025 OPP Expenses"))

    # Parse any Date columns
    for df in (income_df, expense_df):
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Switch between Income vs Expense
    choice = st.radio("View", ["Income", "Expense"], key="view_option")
    if choice == "Income":
        st.subheader("💰 Income Entries")
        df = income_df.copy()
        is_expense = False
    else:
        st.subheader("💸 Expense Entries")
        df = expense_df.copy()
        is_expense = True
        # Make receipt links clickable if present
        if "Receipt Link" in df.columns:
            df["Receipt Link"] = df["Receipt Link"].apply(
                lambda url: f'<a href="{url}" target="_blank">View Receipt</a>'
                if isinstance(url, str) and url else ""
            )

    # — Filters —
    # Property filter
    props = st.multiselect(
        "Property",
        df["Property"].dropna().unique().tolist(),
        default=df["Property"].dropna().unique().tolist()
    )

    # Date range (default: 1st of this month → today)
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
            "Status",
            df["Complete"].dropna().unique().tolist(),
            default=df["Complete"].dropna().unique().tolist()
        )
    else:
        statuses = None

    if is_expense and "Category" in df.columns:
        categories = st.multiselect(
            "Category",
            df["Category"].dropna().unique().tolist(),
            default=df["Category"].dropna().unique().tolist()
        )
    else:
        categories = None

    # — Apply filters —
    mask = df["Property"].isin(props)
    if date_range:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        mask &= df["Date"].between(start, end)
    if statuses is not None:
        mask &= df["Complete"].isin(statuses)
    if categories is not None:
        mask &= df["Category"].isin(categories)

    filtered = df.loc[mask]

    # — Display —
    if is_expense and "Receipt Link" in filtered.columns:
        html = filtered.to_html(escape=False, index=False)
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.dataframe(filtered, use_container_width=True)
