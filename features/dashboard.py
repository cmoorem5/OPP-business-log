import streamlit as st
import pandas as pd
from utils.google_sheets import get_worksheet
import plotly.graph_objects as go

def show():
    st.title("📊 Dashboard Overview")
    
    sheet_name = "OPP Finance Tracker"
    
    # Load Google Sheet tabs
    income_ws = get_worksheet(sheet_name, "2025 OPP Income")
    expenses_ws = get_worksheet(sheet_name, "2025 OPP Expenses")
    
    # Convert to DataFrames
    income_data = income_ws.get_all_records()
    expense_data = expenses_ws.get_all_records()
    income_df = pd.DataFrame(income_data)
    expense_df = pd.DataFrame(expense_data)
    
    # Ensure date parsing
    income_df["Date"] = pd.to_datetime(income_df["Date"], errors="coerce")
    expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors="coerce")
    
    # Summarize totals
    income_df["Amount"] = pd.to_numeric(income_df["Amount"], errors="coerce")
    expense_df["Amount"] = pd.to_numeric(expense_df["Amount"], errors="coerce")
    
    income_df["Month"] = income_df["Date"].dt.strftime("%B")
    expense_df["Month"] = expense_df["Date"].dt.strftime("%B")
    
    # Monthly totals by property
    monthly_income = income_df.groupby(["Month", "Property"])["Amount"].sum().reset_index(name="Income")
    monthly_expense = expense_df.groupby(["Month", "Property"])["Amount"].sum().reset_index(name="Expenses")
    
    # Merge and fill missing
    summary = pd.merge(monthly_income, monthly_expense, on=["Month", "Property"], how="outer").fillna(0)
    summary["Profit"] = summary["Income"] - summary["Expenses"]
    
    # Sort months in calendar order
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
