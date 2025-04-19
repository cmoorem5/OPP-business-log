import streamlit as st
import pandas as pd
from utils.google_sheets import get_worksheet
import plotly.graph_objects as go

def normalize_month(series):
    if series is not None:
        return series.str.strip().str.capitalize()
    return series

def show():
    st.title("📊 Dashboard Overview")

    sheet_name = "OPP Finance Tracker"

    income_ws = get_worksheet(sheet_name, "2025 OPP Income")
    expense_ws = get_worksheet(sheet_name, "2025 OPP Expenses")

    income_df = pd.DataFrame(income_ws.get_all_records())
    expense_df = pd.DataFrame(expense_ws.get_all_records())

    if "Rental Dates" in income_df.columns:
        income_df["Parsed Date"] = pd.to_datetime(income_df["Rental Dates"].str.extract(r"(\d{4}-\d{2}-\d{2})")[0], errors="coerce")
    else:
        income_df["Parsed Date"] = pd.NaT

    expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors="coerce")

    # Use verified parsing logic
    income_df["Income Amount"] = pd.to_numeric(income_df["Income Amount"], errors="coerce").fillna(0)
    expense_df["Amount"] = pd.to_numeric(expense_df["Amount"], errors="coerce")

    income_df["Month"] = normalize_month(income_df["Parsed Date"].dt.strftime("%B"))
    expense_df["Month"] = normalize_month(expense_df["Month"].astype(str))

    monthly_income = income_df.groupby(["Month", "Property"])["Income Amount"].sum().reset_index(name="Income")
    monthly_expense = expense_df.groupby(["Month", "Property"])["Amount"].sum().reset_index(name="Expenses")

    summary = pd.merge(monthly_income, monthly_expense, on=["Month", "Property"], how="outer").fillna(0)
    summary["Profit"] = summary["Income"] - summary["Expenses"]

    month_order = ["January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]
    summary["Month"] = pd.Categorical(summary["Month"], categories=month_order, ordered=True)
    summary = summary.sort_values(by=["Month", "Property"])

    st.markdown("### 📅 Monthly Profit/Loss by Property")
    for prop in summary["Property"].unique():
        prop_df = summary[summary["Property"] == prop]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=prop_df["Month"], y=prop_df["Income"], name="Income"))
        fig.add_trace(go.Bar(x=prop_df["Month"], y=prop_df["Expenses"], name="Expenses"))
        fig.add_trace(go.Scatter(x=prop_df["Month"], y=prop_df["Profit"], name="Profit", mode="lines+markers"))
        fig.update_layout(title=f"{prop} - Monthly Summary", barmode="group", xaxis_title="Month", yaxis_title="Amount ($)")
        st.plotly_chart(fig, use_container_width=True)
