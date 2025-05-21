import streamlit as st
import pandas as pd
import re
from utils.google_sheets import load_sheet_as_df

def extract_first_valid_date(date_str):
    if not isinstance(date_str, str):
        return None

    # Normalize dash styles
    date_str = date_str.replace("–", "-").replace("--", "-").strip()

    # Look for common date formats
    patterns = [
        r"\d{4}-\d{2}-\d{2}",     # 2025-08-01
        r"\d{2}/\d{2}/\d{4}",     # 08/01/2025
        r"\d{2}-\d{2}-\d{4}",     # 08-01-2025
        r"\d{2}/\d{2}",           # 08/01 (assumes current year)
    ]

    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                date = match.group(0)
                # Append current year if missing
                if len(date) == 5:  # MM/DD
                    date += f"/{pd.Timestamp.now().year}"
                return pd.to_datetime(date, errors='coerce')
            except:
                continue
    return None

def show():
    st.title("📊 Dashboard (2025 Only)")

    try:
        df = load_sheet_as_df("2025 OPP Income")
        if df.empty:
            st.warning("No data found in 2025 OPP Income.")
            return

        if "Rental Dates" not in df.columns:
            st.error("Missing 'Rental Dates' column in the sheet.")
            return

        # Extract and parse rental start date
        df["Rental Start Date"] = df["Rental Dates"].apply(extract_first_valid_date)

        # Separate bad rows
        skipped = df[df["Rental Start Date"].isna()]
        df = df.dropna(subset=["Rental Start Date"])

        if not pd.api.types.is_datetime64_any_dtype(df["Rental Start Date"]):
            st.error("Rental start date column could not be parsed correctly.")
            return

        # Add grouping fields
        df["Rental Month"] = df["Rental Start Date"].dt.strftime("%B")
        df["Rental Year"] = df["Rental Start Date"].dt.year

        # Filter for 2025
        df = df[df["Rental Year"] == 2025]

        # Clean income values
        df["Income Amount"] = pd.to_numeric(df["Income Amount"], errors="coerce")
        summary = df.groupby("Rental Month")["Income Amount"].sum().reindex([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]).fillna(0)

        # Display chart
        st.subheader("Monthly Income Summary (by Rental Start Date)")
        st.bar_chart(summary)

        # Preview cleaned rows
        with st.expander("📋 View Cleaned Rental Data"):
            st.dataframe(df)

        # Show skipped rows
        if not skipped.empty:
            st.warning(f"{len(skipped)} row(s) skipped due to unreadable rental start dates.")
            with st.expander("🔍 View Skipped Rows"):
                st.dataframe(skipped[["Rental Dates"]])

    except Exception as e:
        st.error(f"Failed to load dashboard: {e}")
