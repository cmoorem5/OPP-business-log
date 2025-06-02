import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from utils.google_sheets import load_sheet_as_df
from utils.config import SHEET_ID

def load_dashboard_data(year: str, property_name: str):
    df_income = load_sheet_as_df(SHEET_ID, f"{year} OPP Income")
    df_expense = load_sheet_as_df(SHEET_ID, f"{year} OPP Expenses")

    df_income = df_income[df_income["Property"].str.strip() == property_name]
    df_expense = df_expense[df_expense["Property"].str.strip() == property_name]

    df_income["Amount Received"] = pd.to_numeric(df_income["Amount Received"], errors="coerce").fillna(0)
    df_income["Amount Owed"] = pd.to_numeric(df_income["Amount Owed"], errors="coerce").fillna(0)
    df_income["Month"] = df_income["Month"].astype(str).str.strip()

    df_expense["Amount"] = pd.to_numeric(df_expense["Amount"], errors="coerce").fillna(0)
    df_expense["Month"] = df_expense["Month"].astype(str).str.strip()

    return df_income, df_expense

def calculate_summary_metrics(df_income, df_expense):
    total_received = df_income["Amount Received"].sum()
    total_due = df_income["Amount Owed"].sum() - total_received
    total_expenses = df_expense["Amount"].sum()
    net_profit = total_received - total_expenses
    return total_received, total_due, total_expenses, net_profit

def plot_monthly_financials(df_income, df_expense):
    income_by_month = df_income.groupby("Month")["Amount Received"].sum()
    expense_by_month = df_expense.groupby("Month")["Amount"].sum()

    months_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    income_by_month = income_by_month.reindex(months_order, fill_value=0)
    expense_by_month = expense_by_month.reindex(months_order, fill_value=0)
    profit_line = income_by_month - expense_by_month

    fig, ax = plt.subplots()
    ax.bar(income_by_month.index, income_by_month.values, label="Income", alpha=0.6)
    ax.bar(expense_by_month.index, expense_by_month.values, label="Expenses", alpha=0.6)
    ax.plot(profit_line.index, profit_line.values, color="green", marker="o", label="Profit")

    ax.set_ylabel("Amount ($)")
    ax.set_title("Monthly Income vs Expenses")
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

def plot_outstanding_chart(df_income):
    df = df_income.copy()
    df["Outstanding"] = df["Amount Owed"] - df["Amount Received"]
    by_status = df.groupby("Status")["Outstanding"].sum().sort_values(ascending=False)

    if by_status.empty or by_status.sum() == 0:
        st.info("No outstanding balances.")
        return

    fig, ax = plt.subplots()
    by_status.plot(kind="bar", color="orange", ax=ax)
    ax.set_ylabel("Amount ($)")
    ax.set_title("What Is Still Owed (by Status)")
    st.pyplot(fig)
