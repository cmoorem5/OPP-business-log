import pandas as pd
import streamlit as st

from utils.google_sheets import load_sheet_as_df
from utils.google_drive import generate_drive_link
from utils.config import SHEET_ID, PROPERTIES, STATUS_OPTIONS


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[:, df.columns.str.strip() != ""]
    counts = {}
    new_cols = []
    for col in df.columns:
        counts[col] = counts.get(col, 0)
        new_cols.append(col if counts[col] == 0 else f"{col}_{counts[col]}")
        counts[col] += 1
    df.columns = new_cols
    return df


def load_and_prepare_data(view_type: str, year: str):
    if view_type == "Income":
        df = _clean_df(load_sheet_as_df(SHEET_ID, f"{year} OPP Income"))

        if "Amount Received" not in df.columns:
            st.error("❌ Missing 'Amount Received' column in Income sheet.")
            return pd.DataFrame(), pd.DataFrame(), None

        if "Check-in" not in df.columns:
            st.error("❌ Missing 'Check-in' column in Income sheet.")
            return pd.DataFrame(), pd.DataFrame(), None

        df["Rental Start Date"] = pd.to_datetime(df["Check-in"], errors="coerce")
        skipped = df[df["Rental Start Date"].isna()]
        df = df.dropna(subset=["Rental Start Date"]).copy()

        df["Rental Month"] = pd.Categorical(
            df["Rental Start Date"].dt.strftime("%B"),
            categories=[
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ],
            ordered=True
        )
        df["Rental Year"] = df["Rental Start Date"].dt.year
        return df, skipped, "Rental Start Date"

    else:
        df = _clean_df(load_sheet_as_df(SHEET_ID, f"{year} OPP Expenses"))
        skipped = pd.DataFrame()
        return df, skipped, "Date"


def get_filters_ui(df: pd.DataFrame, view_type: str, year: str):
    props = st.multiselect("Property", PROPERTIES, default=PROPERTIES)

    cats = []
    if "Category" in df.columns:
        unique_cats = df["Category"].dropna().unique().tolist()
        cats = st.multiselect("Category", unique_cats, default=unique_cats)

    stats = []
    if view_type == "Income" and "Status" in df.columns:
        stats = st.multiselect("Status", STATUS_OPTIONS, default=STATUS_OPTIONS)
    elif view_type == "Expense" and "Complete" in df.columns:
        unique_stats = df["Complete"].dropna().unique().tolist()
        stats = st.multiselect("Status", unique_stats, default=unique_stats)

    default_start = pd.to_datetime(f"{year}-01-01")
    default_end = pd.Timestamp.now()
    date_range = st.date_input("Date Range", [default_start, default_end], key=f"date_range_{view_type.lower()}")

    return {
        "props": props,
        "cats": cats,
        "stats": stats,
        "date_range": date_range
    }


def apply_filters(df: pd.DataFrame, filters: dict, date_col: str) -> pd.DataFrame:
    mask = df["Property"].isin(filters["props"])

    if filters["cats"] and "Category" in df.columns:
        mask &= df["Category"].isin(filters["cats"])

    if filters["stats"]:
        if "Status" in df.columns:
            mask &= df["Status"].isin(filters["stats"])
        elif "Complete" in df.columns:
            mask &= df["Complete"].isin(filters["stats"])

    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        start, end = pd.to_datetime(filters["date_range"][0]), pd.to_datetime(filters["date_range"][1])
        mask &= df[date_col].between(start, end)

    return df.loc[mask]


def show_data_table(filtered: pd.DataFrame, view_type: str, year: str, skipped: pd.DataFrame):
    if "Receipt Link" in filtered.columns:
        filtered["Receipt Link"] = filtered["Receipt Link"].apply(
            lambda fid: f'<a href="{generate_drive_link(fid)}" target="_blank">📄 View</a>' if pd.notna(fid) and fid else ""
        )

    st.markdown(f"**{len(filtered)} entries found**")
    st.markdown(filtered.to_html(escape=False, index=False), unsafe_allow_html=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv, file_name=f"{view_type.lower()}_{year}_filtered.csv", mime="text/csv")

    if view_type == "Income" and not skipped.empty:
        st.warning(f"{len(skipped)} row(s) skipped due to unreadable check-in dates.")
        with st.expander("🔍 View Skipped Rows"):
            st.dataframe(skipped[["Check-in"]])
