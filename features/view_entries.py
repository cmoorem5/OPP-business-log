import streamlit as st
import pandas as pd
from datetime import date
from utils.google_sheets import load_sheet_as_df

def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    # Drop blank headers & dedupe names
    df = df.loc[:, df.columns.str.strip() != ""]
    counts, new_cols = {}, []
    for col in df.columns:
        counts[col] = counts.get(col, 0)
        new_cols.append(col if counts[col] == 0 else f"{col}_{counts[col]}")
        counts[col] += 1
    df.columns = new_cols
    return df

def show():
    st.title("📂 View Logged Entries")

    # — Refresh button —
    if st.button("🔄 Refresh Data"):
        load_sheet_as_df.clear()
        st.experimental_rerun()

    # Load & clean
    income_df  = _clean_df(load_sheet_as_df("2025 OPP Income"))
    expense_df = _clean_df(load_sheet_as_df("2025 OPP Expenses"))

    # Parse dates
    for df in (income_df, expense_df):
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Choose view
    choice = st.radio("View", ["Income", "Expense"], key="view_option")
    if choice == "Income":
        st.subheader("💰 Income Entries")
        df, is_expense = income_df.copy(), False
    else:
        st.subheader("💸 Expense Entries")
        df, is_expense = expense_df.copy(), True
        if "Receipt Link" in df.columns:
            df["Receipt Link"] = df["Receipt Link"].apply(
                lambda url: f'<a href="{url}" target="_blank">View Receipt</a>'
                if isinstance(url, str) and url else ""
            )

    # — Filters —
    props = st.multiselect(
        "Property",
        df["Property"].dropna().unique().tolist(),
        default=df["Property"].dropna().unique().tolist()
    )

    # Date range defaults to this month
    if "Date" in df.columns:
        today = date.today()
        first = today.replace(day=1)
        date_range = st.date_input("Date range", [first, today], key="date_range")
    else:
        date_range = None

    statuses = (
        st.multiselect(
            "Status",
            df["Complete"].dropna().unique().tolist(),
            default=df["Complete"].dropna().unique().tolist()
        ) if is_expense and "Complete" in df.columns else None
    )

    categories = (
        st.multiselect(
            "Category",
            df["Category"].dropna().unique().tolist(),
            default=df["Category"].dropna().unique().tolist()
        ) if is_expense and "Category" in df.columns else None
    )

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
        st.markdown(filtered.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.dataframe(filtered, use_container_width=True)
