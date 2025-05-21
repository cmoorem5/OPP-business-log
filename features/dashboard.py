import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df

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

        # Extract potential rental start date from string
        df["Rental Start Raw"] = df["Rental Dates"].astype(str).str.split("–").str[0].str.strip()
        df["Rental Start Date"] = pd.to_datetime(df["Rental Start Raw"], errors="coerce")

        # Separate invalid rows
        invalid_rows = df[df["Rental Start Date"].isna()]
        df = df.dropna(subset=["Rental Start Date"])

        # Type safety check
        if not pd.api.types.is_datetime64_any_dtype(df["Rental Start Date"]):
            st.error("Rental start date column could not be parsed correctly.")
            return

        # Create month/year fields
        df["Rental Month"] = df["Rental Start Date"].dt.strftime("%B")
        df["Rental Year"] = df["Rental Start Date"].dt.year

        # Filter to 2025 only
        df = df[df["Rental Year"] == 2025]

        # Income cleaning
        df["Income Amount"] = pd.to_numeric(df["Income Amount"], errors="coerce")
        summary = df.groupby("Rental Month")["Income Amount"].sum().reindex([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]).fillna(0)

        # Bar chart
        st.subheader("Monthly Income Summary (by Rental Start Date)")
        st.bar_chart(summary)

        # Raw data preview
        with st.expander("📋 View Cleaned Rental Data"):
            st.dataframe(df)

        # Show skipped rows if any
        if not invalid_rows.empty:
            st.warning(f"{len(invalid_rows)} row(s) skipped due to unreadable rental start date.")
            with st.expander("🔍 View Skipped Rows"):
                st.dataframe(invalid_rows)

    except Exception as e:
        st.error(f"Failed to load dashboard: {e}")
