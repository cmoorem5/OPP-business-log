import streamlit as st
import pandas as pd
from utils.google_sheets import get_worksheet
import plotly.graph_objects as go

def show():
    st.title("📊 Dashboard Overview with Income Debug")

    sheet_name = "OPP Finance Tracker"
    income_ws = get_worksheet(sheet_name, "2025 OPP Income")
    expense_ws = get_worksheet(sheet_name, "2025 OPP Expenses")

    income_df = pd.DataFrame(income_ws.get_all_records())
    expense_df = pd.DataFrame(expense_ws.get_all_records())

    # --- CLEANING & PARSING ---
    income_df["Income Amount"] = pd.to_numeric(income_df["Income Amount"], errors="coerce")
    income_df["Property"] = income_df.get("Property", "").fillna("").replace("", "Unknown")
    income_df["Month"] = income_df["Month"].str.strip().str.capitalize()

    expense_df["Amount"] = pd.to_numeric(expense_df["Amount"], errors="coerce")
    expense_df["Property"] = expense_df.get("Property", "").fillna("").replace("", "Unknown")
    expense_df["Month"] = expense_df["Month"].astype(str).str.strip().str.capitalize()

  
    monthly_expense = expense_df.groupby(["Month", "Property"])["Amount"].sum().reset_index()

    # --- MERGE & CALCULATE ---
    summary = pd.merge(monthly_income, monthly_expense, on=["Month", "Property"], how="outer").fillna(0)
    summary["Profit"] = summary["Income Amount"] - summary["Amount"]

    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    summary["Month"] = pd.Categorical(summary["Month"], categories=month_order, ordered=True)
    summary = summary.sort_values(by=["Month", "Property"])

    # --- PLOT ---
    for prop in summary["Property"].unique():
        prop_df = summary[summary["Property"] == prop]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=prop_df["Month"], y=prop_df["Income Amount"], name="Income"))
        fig.add_trace(go.Bar(x=prop_df["Month"], y=prop_df["Amount"], name="Expenses"))
        fig.add_trace(go.Scatter(x=prop_df["Month"], y=prop_df["Profit"], name="Profit", mode="lines+markers"))
        fig.update_layout(title=f"{prop} - Monthly Summary", barmode="group", xaxis_title="Month", yaxis_title="Amount ($)")
        st.plotly_chart(fig, use_container_width=True)
