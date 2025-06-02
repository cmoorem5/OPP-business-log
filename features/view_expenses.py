import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.google_sheets import load_sheet_as_df
from utils.config import SHEET_ID

def show():
    st.title("💸 View Monthly Expenses")

    year = st.selectbox("Select Year", ["2025", "2026"], index=0)
    sheet_name = f"{year} OPP Expenses"

    try:
        df = load_sheet_as_df(SHEET_ID, sheet_name)

        if df.empty or "Amount" not in df.columns or "Month" not in df.columns:
            st.warning("No valid data found in the expense sheet.")
            return

        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["Month"] = df["Month"].astype(str).str.strip()
        df["Category"] = df["Category"].astype(str).str.strip()

        # Monthly total by category
        summary = df.groupby(["Month", "Category"])["Amount"].sum().reset_index()

        st.markdown("### 📊 Monthly Expenses by Category")
        pivot = summary.pivot(index="Month", columns="Category", values="Amount").fillna(0)
        pivot = pivot.loc[[m for m in [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ] if m in pivot.index]]

        st.bar_chart(pivot)

        st.markdown("### 🧾 Full Expense Table")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV", data=csv, file_name=f"{year}_expenses.csv", mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Failed to load expenses: {e}")
