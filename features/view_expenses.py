import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.google_sheets import load_sheet_as_df
from utils.config import SHEET_ID

def show():
    st.title("💸 View Monthly Expenses")

    year = st.selectbox("Select Year", ["2025", "2026"], index=0)
    expense_sheet = f"{year} OPP Expenses"
    income_sheet = f"{year} OPP Income"

    try:
        # --- Load Expense Data ---
        df_expense = load_sheet_as_df(SHEET_ID, expense_sheet)

        if df_expense.empty or "Amount" not in df_expense.columns or "Month" not in df_expense.columns:
            st.warning("No valid expense data found.")
            return

        df_expense["Amount"] = pd.to_numeric(df_expense["Amount"], errors="coerce").fillna(0)
        df_expense["Month"] = df_expense["Month"].astype(str).str.strip()
        df_expense["Category"] = df_expense["Category"].astype(str).str.strip()

        summary = df_expense.groupby(["Month", "Category"])["Amount"].sum().reset_index()
        pivot = summary.pivot(index="Month", columns="Category", values="Amount").fillna(0)

        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        pivot = pivot.loc[[m for m in month_order if m in pivot.index]]

        st.markdown("### 📊 Monthly Expenses by Category")
        st.bar_chart(pivot)

        st.markdown("### 🧾 Full Expense Table")
        st.dataframe(df_expense, use_container_width=True)

        csv = df_expense.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name=f"{year}_expenses.csv", mime="text/csv")

        # --- Income by Source ---
        with st.expander("💰 Income by Source"):
            df_income = load_sheet_as_df(SHEET_ID, income_sheet)
            df_income["Amount Received"] = pd.to_numeric(df_income["Amount Received"], errors="coerce").fillna(0)

            source_summary = (
                df_income.groupby("Income Source")["Amount Received"]
                .sum()
                .reset_index()
                .sort_values(by="Amount Received", ascending=False)
            )

            source_summary.loc["Total"] = ["Total", source_summary["Amount Received"].sum()]
            st.dataframe(source_summary, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
