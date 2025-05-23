import streamlit as st
import pandas as pd
import re
from utils.google_sheets import load_sheet_as_df


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[:, df.columns.str.strip() != ""]
    counts, new_cols = {}, []
    for col in df.columns:
        counts[col] = counts.get(col, 0)
        new_cols.append(col if counts[col] == 0 else f"{col}_{counts[col]}")
        counts[col] += 1
    df.columns = new_cols
    return df


def extract_first_valid_date(date_str):
    if not isinstance(date_str, str):
        return None
    date_str = date_str.replace("–", "-").replace("--", "-").strip()
    patterns = [
        r"\d{4}-\d{2}-\d{2}", r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}", r"\d{2}/\d{2}"
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
            st.warning("Cache cleared. Please reload the page.")
            return

    income_df = _clean_df(load_sheet_as_df("2025 OPP Income"))
    if "Income Amount" in income_df.columns:
        income_df.rename(columns={"Income Amount": "Amount"}, inplace=True)

    expense_df = _clean_df(load_sheet_as_df("2025 OPP Expenses"))

    view_option = st.radio("View", ["Income", "Expense"], key="view_option")

    if view_option == "Income":
        st.subheader("💰 Income Entries")

        income_df["Rental Start Date"] = income_df["Rental Dates"].apply(extract_first_valid_date)
        skipped = income_df[income_df["Rental Start Date"].isna()]
        df = income_df.dropna(subset=["Rental Start Date"]).copy()

        df["Rental Month"] = df["Rental Start Date"].dt.strftime("%B")
        df["Rental Year"] = df["Rental Start Date"].dt.year

        props = st.multiselect("Property", df["Property"].dropna().unique().tolist(), default=df["Property"].dropna().unique().tolist())
        today = pd.Timestamp.now().date()
        date_range = st.date_input("Rental Start Date Range", [today.replace(day=1), today], key="date_range_income")

        mask = df["Property"].isin(props)
        if isinstance(date_range, list) and len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            mask &= df["Rental Start Date"].between(start, end)

        st.dataframe(df.loc[mask], use_container_width=True)

        if not skipped.empty:
            st.warning(f"{len(skipped)} row(s) skipped due to unreadable rental dates.")
            with st.expander("🔍 View Skipped Rows"):
                st.dataframe(skipped[["Rental Dates"]])

    else:
        st.subheader("💸 Expense Entries")
        df = expense_df.copy()

        if "Receipt Link" in df.columns:
            df["Receipt Link"] = df["Receipt Link"].apply(
                lambda url: f'<a href="{url}" target="_blank">View Receipt</a>' if isinstance(url, str) and url else ""
            )

        props = st.multiselect("Property", df["Property"].dropna().unique().tolist(), default=df["Property"].dropna().unique().tolist())
        statuses = df["Complete"].dropna().unique().tolist() if "Complete" in df.columns else []
        selected_statuses = st.multiselect("Status", statuses, default=statuses) if statuses else None
        categories = df["Category"].dropna().unique().tolist() if "Category" in df.columns else []
        selected_categories = st.multiselect("Category", categories, default=categories) if categories else None

        date_range = st.date_input("Expense Date Range", [pd.to_datetime("2025-01-01"), pd.Timestamp.now()], key="date_range_expense")

        mask = df["Property"].isin(props)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            if isinstance(date_range, list) and len(date_range) == 2:
                start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
                mask &= df["Date"].between(start, end)
        if selected_statuses and "Complete" in df.columns:
            mask &= df["Complete"].isin(selected_statuses)
        if selected_categories and "Category" in df.columns:
            mask &= df["Category"].isin(selected_categories)

        filtered = df.loc[mask]

        if "Receipt Link" in filtered.columns:
            st.markdown(filtered.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.dataframe(filtered, use_container_width=True)
