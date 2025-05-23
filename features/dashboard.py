import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df
import matplotlib.pyplot as plt
from datetime import datetime

def show():
    st.title("📊 Finance Dashboard")

    # Default to current year
    current_year = str(datetime.now().year)
    income_sheet = f"{current_year} OPP Income"
    expense_sheet = f"{current_year} OPP Expenses"

    # Load data
    df_income = load_sheet_as_df(income_sheet)
    df_expense = load_sheet_as_df(expense_sheet)

    # Clean up numeric fields
    df_income["Amount Owed"] = pd.to_numeric(df_income["Amount Owed"], errors="coerce").fillna(0)
    df_income["Amount Received"] = pd.to_numeric(df_income["Amount Received"], errors="coerce").fillna(0)
    df_income["Balance"] = pd.to_numeric(df_income["Balance"], errors="coerce").fillna(0)

    df_expense["Amount"] = pd.to_numeric(df_expense["Amount"], errors="coerce").fillna(0)

    # Month sort logic
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    if "Month" in df_income.columns:
        df_income["Month Num"] = df_income["Month"].map(month_order)
        df_income = df_income.sort_values("Month Num").drop(columns="Month Num")

    if "Month" in df_expense.columns:
        df_expense["Month Num"] = df_expense["Month"].map(month_order)
        df_expense = df_expense.sort_values("Month Num").drop(columns="Month Num")

    # Summary
    income_summary = df_income.groupby("Month")["Amount Received"].sum()
    expense_summary = df_expense.groupby("Month")["Amount"].sum()

    # Plot income
    with st.expander("📈 Income Overview", expanded=True):
        st.subheader("Total Income by Month")
        fig, ax = plt.subplots()
        income_summary.plot(kind="bar", ax=ax)
        ax.set_ylabel("Amount ($)")
        ax.set_xlabel("Month")
        st.pyplot(fig)

    # Plot expenses
    with st.expander("💸 Expense Overview", expanded=True):
        st.subheader("Total Expenses by Month")
        fig2, ax2 = plt.subplots()
        expense_summary.plot(kind="bar", color="orange", ax=ax2)
        ax2.set_ylabel("Amount ($)")
        ax2.set_xlabel("Month")
        st.pyplot(fig2)
