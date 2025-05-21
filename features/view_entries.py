import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📊 Recurring vs. One-Time Expenses")

    try:
        df = load_sheet_as_df("2025 OPP Expenses")

        if df.empty:
            st.warning("No expense data found.")
            return

        # Only process rows with valid amounts
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df = df.dropna(subset=["Amount"])

        # Tag as Recurring vs One-Time based on comments
        df["Type"] = df["Comments"].fillna("").str.lower().str.contains("recurring").map({
            True: "Recurring", False: "One-Time"
        })
        df["Type"] = pd.Categorical(df["Type"], categories=["Recurring", "One-Time"])

        # Extract and sort by month
        df["Month"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%B")
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
        df = df.dropna(subset=["Month"])

        # Group for chart
        summary = df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0).loc[month_order]

        st.subheader("Monthly Expense Breakdown")
        st.bar_chart(summary)

        st.subheader("📋 Totals by Type")
        totals = df.groupby("Type")["Amount"].sum().reindex(["Recurring", "One-Time"], fill_value=0)
        st.dataframe(totals.reset_index(), use_container_width=True)

        # Toggle for viewing full dataset
        with st.expander("📄 View Full Expense Data"):
            if st.checkbox("Show full dataset (may impact performance)", key="show_data"):
                st.dataframe(df, use_container_width=True)

        # Optional CSV download
        csv = df.to_csv(index=False)
        st.download_button("Download Full Expense Data", csv, file_name="expenses_2025.csv")

    except Exception as e:
        st.error(f"Failed to load recurring summary: {e}")
