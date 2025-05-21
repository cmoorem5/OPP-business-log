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

        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df = df.dropna(subset=["Amount"])

        # Determine recurring status
        df["Type"] = df["Comments"].fillna("").apply(
            lambda x: "Recurring" if "recurring" in x.lower() else "One-Time"
        )

        # Ensure "Type" has both expected categories
        df["Type"] = pd.Categorical(df["Type"], categories=["Recurring", "One-Time"])

        # Monthly breakdown
        df["Month"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%B")
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
        df = df.dropna(subset=["Month"])

        # Aggregate by month and type
        summary = df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0).loc[month_order]

        st.subheader("Monthly Expense Breakdown")
        st.bar_chart(summary)

        st.subheader("📋 Totals by Type")
        totals = df.groupby("Type")["Amount"].sum().reindex(["Recurring", "One-Time"], fill_value=0)
        st.write(totals.reset_index())

        # Optional download
        csv = df.to_csv(index=False)
        st.download_button("Download Full Expense Data", csv, file_name="expenses_2025.csv")

    except Exception as e:
        st.error(f"Failed to load recurring summary: {e}")
