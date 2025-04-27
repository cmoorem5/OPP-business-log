import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📊 Dashboard Overview")

    sheet = "OPP Finance Tracker"
    # Load data
    income_df  = load_sheet_as_df(sheet, "2025 OPP Income").rename(columns={"Income Amount": "Income"})
    expense_df = load_sheet_as_df(sheet, "2025 OPP Expenses").rename(columns={"Amount": "Expense"})

    # Merge and compute profit
    df = pd.merge(income_df, expense_df, on=["Month", "Property"], how="outer")
    df["Income"] = df["Income"].fillna(0)
    df["Expense"] = df["Expense"].fillna(0)
    df["Profit"] = df["Income"] - df["Expense"]    # Totals summary    # Individual property charts with income/expense bars + profit line
    for prop in df["Property"].unique():
        prop_df = df[df["Property"] == prop]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=prop_df["Month"],
            y=prop_df["Income"],
            name="Income"
        ))
        fig.add_trace(go.Bar(
            x=prop_df["Month"],
            y=prop_df["Expense"],
            name="Expense"
        ))
        fig.add_trace(go.Scatter(
            x=prop_df["Month"],
            y=prop_df["Profit"],
            name="Profit",
            mode="lines+markers"
        ))

        
        fig.update_layout(
            title=f"{prop} – Monthly Summary",
            barmode="group",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            legend_title="Metric",
            
        )

        st.plotly_chart(fig, use_container_width=True)
