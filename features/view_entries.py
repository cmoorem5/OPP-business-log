import streamlit as st
import pandas as pd
from datetime import date
from utils.google_sheets import load_sheet_as_df
import re

def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Drop blank/whitespace column names and make duplicates unique."""
    df = df.loc[:, df.columns.str.strip() != ""]
    counts, new_cols = {}, []
    for col in df.columns:
        counts[col] = counts.get(col, 0)
        new_cols.append(col if counts[col] == 0 else f"{col}_{counts[col]}")
        counts[col] += 1
    df.columns = new_cols
    return df

def extract_first_valid_date(date_str):
    """Extracts the first valid date from a string with fallback to current year."""
    if not isinstance(date_str, str):
        return None

    date_str = date_str.replace("–", "-").replace("--", "-").strip()

    patterns = [
        r"\d{4}-\d{2}-\d{2}",     # 2025-08-01
        r"\d{2}/\d{2}/\d{4}",     # 08/01/2025
        r"\d{2}-\d{2}-\d{4}",     # 08-01-2025
        r"\d{2}/\d{2}",           # 08/01 (assume current year)
    ]

    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            date = match.group(0)
            if len(date) == 5:
                date += f"/{pd.Timestamp.now().year}"
            return pd.to_datetime(date, errors='coerce')
    return None

def show():
    st.title("📂 View Logged Entries")

    if st.button("🔄 Refresh Data"):
        load_sheet_as_df.clear()
        try:
            st.experimental_rerun()
        except AttributeError:
            st.warning("Cache cleared. Please reload the page (F5) to see updated data.")
            return

    # Load & clean both sheets
    income_df = _clean_df(load_sheet_as_df("2025 OPP Income"))
    expense_df = _clean_df(load_sheet_as_df("2025 OPP Expenses"))

    choice = st.radio("View", ["Income", "Expense"], key="view_option")
    if choice == "Income":
        st.subheader("💰 Income Entries")

        # --- Rental Start Date Parsing ---
        income_df["Rental Start Date"] = income_df["Rental Dates"].apply(extract_first_valid_date)
        skipped = income_df[income_df["Rental Start Date"].isna()]
        df = income_df.dropna(subset=["Rental Start Date"]).copy()

        df["Rental Month"] = df["Rental Start Date"].dt.strftime("%B")
        df["Rental Year"] = df["Rental Start Date"].dt.year

        # --- Filters ---
        props = st.multiselect(
            "Property",
            df["Property"].dropna().unique().tolist(),
            default=df["Property"].dropna().unique().tolist()
        )

        today = date.today()
        first_of_month = today.replace(day=1)
        date_range = st.date_input("Rental Start Date Range", [first_of_month, today], key="date_range_income")

        mask = df["Property"].isin(props)
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        mask &= df["Rental Start Date"].between(start, end)

        filtered = df.loc[mask]
        st.dataframe(filtered, use_container_width=True)

        # Show skipped rows
        if not skipped.empty:
            st.warning(f"{len(skipped)} row(s) skipped due to unreadable rental dates.")
            with st.expander("🔍 View Skipped Rows"):
                st.dataframe(skipped[["Rental Dates"]])

    else:
        st.subheader("💸 Expense Entries")
        df, is_expense = expense_df.copy(), True

        if "Receipt Link" in df.columns:
            df["Receipt Link"] = df["Receipt Link"].apply(
                lambda url: f'<a href="{url}" target="_blank">View Receipt</a>'
                if isinstance(url, str) and url else ""
            )

        props = st.multiselect(
            "Property",
            df["Property"].dropna().unique().tolist(),
            default=df["Property"].dropna().unique().tolist()
        )

        statuses = st.multiselect(
            "Status",
            df["Complete"].dropna().unique().tolist() if "Complete" in df.columns else [],
            default=df["Complete"].dropna().unique().tolist() if "Complete" in df.columns else []
        )

        categories = st.multiselect(
            "Category",
            df["Category"].dropna().unique().tolist() if "Category" in df.columns else [],
            default=df["Category"].dropna().unique().tolist() if "Category" in df.columns else []
        )

        date_range = st.date_input(
            "Expense Date Range",
            [date.today().replace(day=1), date.today()],
            key="date_range_expense"
        )

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            mask = (
                df["Property"].isin(props) &
                df["Complete"].isin(statuses) &
                df["Category"].isin(categories) &
                df["Date"].between(start, end)
            )
        else:
            mask = df["Property"].isin(props)

        filtered = df.loc[mask]

        if "Receipt Link" in filtered.columns:
            st.markdown(filtered.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.dataframe(filtered, use_container_width=True)
