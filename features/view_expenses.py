import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from utils.google_sheets import load_sheet_as_df
from utils.config import SHEET_ID

def show():
    st.title("💸 View Monthly Expenses & Income")

    year = st.selectbox("Select Year", ["2025", "2026"])
    property_filter = st.selectbox("Select Property", ["Islamorada", "Standish"])
    income_sheet = f"{year} OPP Income"
    expense_sheet = f"{year} OPP Expenses"

    # Load data
    try:
        df_income = load_sheet_as_df(SHEET_ID, income_sheet)
        df_expense = load_sheet_as_df(SHEET_ID, expense_sheet)
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return

    # Standardize and clean
    df_income["Property"] = df_income["Property"].astype(str).str.strip()
    df_expense["Property"] = df_expense["Property"].astype(str).str.strip()

    # --- EXPENSES ---
    st.markdown("### 📊 Monthly Expenses by Category")
    expense_data = df_expense[df_expense["Property"] == property_filter].copy()
    if not expense_data.empty and "Amount" in expense_data.columns and "Category" in expense_data.columns:
        expense_data["Amount"] = pd.to_numeric(expense_data["Amount"], errors="coerce").fillna(0)
        expense_data["Category"] = expense_data["Category"].astype(str).str.strip()
        summary_expense = expense_data.groupby("Category")["Amount"].sum().sort_values(ascending=False).reset_index()

        fig, ax = plt.subplots()
        ax.barh(summary_expense["Category"], summary_expense["Amount"], color="#FF7043")
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.set_xlabel("Total ($)")
        ax.set_title(f"{property_filter} - Expenses by Category")
        st.pyplot(fig)
    else:
        st.info("No expense data for this property.")

    # --- INCOME ---
    st.markdown("### 💰 Income by Source")
    income_data = df_income[df_income["Property"] == property_filter].copy()
    if not income_data.empty and "Amount Received" in income_data.columns and "Income Source" in income_data.columns:
        income_data["Amount Received"] = pd.to_numeric(income_data["Amount Received"], errors="coerce").fillna(0)
        income_data["Income Source"] = income_data["Income Source"].astype(str).str.strip()
        summary_income = income_data.groupby("Income Source")["Amount Received"].sum().sort_values(ascending=False).reset_index()

        fig, ax = plt.subplots()
        ax.barh(summary_income["Income Source"], summary_income["Amount Received"], color="#4CAF50")
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.set_xlabel("Total ($)")
        ax.set_title(f"{property_filter} - Income by Source")
        st.pyplot(fig)
    else:
        st.info("No income data for this property.")
