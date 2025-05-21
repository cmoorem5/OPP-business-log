import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df
from datetime import datetime

def show():
    st.title("📊 Dashboard (2025 Only)")

    try:
        df = load_sheet_as_df("2025 OPP Income")
        if df.empty:
            st.warning("No data found in 2025 OPP Income.")
            return

        # Ensure "Rental Dates" column exists
        if "Rental Dates" not in df.columns:
            st.error("Missing 'Rental Dates' column in sheet.")
            return

        # Extract rental start date
        df["Rental Start Date"] = df["Rental Dates"].str.split("–").str[0].str.strip()
        df["Rental Start Date"] = pd.to_datetime(df["Rental Start Date"], errors="coerce")

        # Drop rows where date couldn't be parsed
        df = df.dropna(subset=["Rental Start Date"])

        # Add month and year for grouping
        df["Rental Month"] = df["Rental Start Date"].dt.strftime("%B")
        df["Rental Year"] = df["Rental Start Date"].dt.year

        # Filter only 2025 (safe guard)
        df = df[df["Rental Year"] == 2025]

        # Clean and prepare for summary
        df["Income Amount"] = pd.to_numeric(df["Income Amount"], errors="coerce")
        summary = df.groupby("Rental Month")["Income Amount"].sum().reindex([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]).fillna(0)

        # Show summary table
        st.subheader("Monthly Income Summary (based on Rental Start Date)")
        st.bar_chart(summary)

        # Optional: View raw data
        with st.expander("View Raw Data"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Failed to load dashboard: {e}")
