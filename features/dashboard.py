import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📊 Finance Dashboard")

    # Current year logic
    current_year = str(datetime.now().year)
    income_sheet = f"{current_year} OPP Income"
    expense_sheet = f"{current_year} OPP Expenses"

    # Load and clean income
    df_income = load_sheet_as_df(income_sheet)
    df_income["Amount Received"] = pd.to_numeric(df_income["Amount Received"], errors="coerce").fillna(0)
    df_income["Month"] = df_income["Month"].str.strip()
    df_income = df_income.dropna(subset=["Month", "Property"])

    # Load and clean expenses
    df_expense = load_sheet_as_df(expense_sheet)
    df_expense["Amount"] = pd.to_numeric(df_expense["Amount"], errors="coerce").fillna(0)
    df_expense["Month"] = df_expense["Month"].str.strip()
    df_expense = df_expense.dropna(subset=["Month", "Property"])

    # Month sort helper
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    # Group summaries
    income_grouped = df_income.groupby(["Property", "Month"])["Amount Received"].sum().reset_index()
    expense_grouped = df_expense.groupby(["Property", "Month"])["Amount"].sum().reset_index()

    # Merge for profit calculation
    summary = pd.merge(income_grouped, expense_grouped, how="outer", on=["Property", "Month"])
    summary["Amount Received"] = summary["Amount Received"].fillna(0)
    summary["Amount"] = summary["Amount"].fillna(0)
    summary["Profit"] = summary["Amount Received"] - summary["Amount"]
    summary["Month Num"] = summary["Month"].map(month_order)
    summary = summary.sort_values("Month Num")

    # Combined Summary Chart
    with st.expander("📋 Summary Chart (All Properties)", expanded=True):
        st.subheader("Total Income, Expenses, and Profit by Month")
        total = summary.groupby("Month").agg({
            "Amount Received": "sum",
            "Amount": "sum",
            "Profit": "sum",
            "Month Num": "first"
        }).reset_index().sort_values("Month Num")

        fig, ax = plt.subplots()
        ax.bar(total["Month"], total["Amount Received"], label="Income", color="#4CAF50")
        ax.bar(total["Month"], total["Amount"], label="Expenses", color="#F44336", alpha=0.7)
        ax.plot(total["Month"], total["Profit"], label="Profit", color="#2196F3", marker="o", linewidth=2)
        ax.set_ylabel("Amount ($)")
        ax.set_title("Monthly Financial Overview")
        ax.legend()
        st.pyplot(fig)

    # Per-property breakdown
    properties = sorted(summary["Property"].dropna().unique())

    for prop in properties:
        with st.expander(f"🏡 {prop}", expanded=False):
            prop_data = summary[summary["Property"] == prop]

            fig, ax = plt.subplots()
            ax.bar(prop_data["Month"], prop_data["Amount Received"], label="Income", color="#4CAF50")
            ax.bar(prop_data["Month"], prop_data["Amount"], label="Expenses", color="#F44336", alpha=0.7)
            ax.plot(prop_data["Month"], prop_data["Profit"], label="Profit", color="#2196F3", marker="o", linewidth=2)
            ax.set_ylabel("Amount ($)")
            ax.set_title(f"{prop} - Monthly Breakdown")
            ax.legend()
            st.pyplot(fig)
