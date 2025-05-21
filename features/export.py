import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📊 Recurring vs. One-Time Expenses")

    year = st.radio("Select Year", ["2025", "2026"], horizontal=True)

    try:
        df = load_sheet_as_df(f"{year} OPP Expenses")

        if df.empty:
            st.warning("No expense data found.")
            return

        if "Amount" not in df.columns:
            st.error("'Amount' column missing in sheet.")
            return

        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df = df.dropna(subset=["Amount"])

        df["Type"] = df["Comments"].fillna("").apply(
            lambda x: "Recurring" if "recurring" in x.lower() else "One-Time"
        )

        df["Month"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%B")
        df = df.dropna(subset=["Month"])

        summary = df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)
        summary = summary.reindex([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ], fill_value=0)

        st.subheader("Monthly Expense Breakdown")
        st.bar_chart(summary)

        st.subheader("📋 Totals by Type")
        totals = df.groupby("Type")["Amount"].sum()
        st.write(totals.reset_index())

        csv = df.to_csv(index=False)
        st.download_button("Download Full Expense Data", csv, file_name=f"expenses_{year}.csv")

    except Exception as e:
        st.error(f"Failed to load recurring summary: {e}")
