import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import load_excel_data

def show():
    st.markdown("## 📊 Dashboard Overview")
    st.write("A summary of income, expenses, and net profit with visual insights.")

    # Load data
    income_df = load_excel_data("2025 OPP Income")
    expenses_df = load_excel_data("2025 OPP Expenses")

    # Totals
    total_income = income_df["Income Amount"].sum()
    total_expenses = expenses_df["Amount"].sum()
    net_profit = total_income - total_expenses

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Income", f"${total_income:,.2f}")
    col2.metric("📉 Total Expenses", f"${total_expenses:,.2f}")
    col3.metric("📈 Net Profit", f"${net_profit:,.2f}")

    st.markdown("---")
    st.markdown("### 📅 Monthly Income vs Expenses")

    # Monthly summary
    income_by_month = income_df.groupby("Month")["Income Amount"].sum()
    expenses_by_month = expenses_df.groupby("Month")["Amount"].sum()

    months = sorted(set(income_by_month.index).union(set(expenses_by_month.index)))
    income_values = [income_by_month.get(month, 0) for month in months]
    expense_values = [expenses_by_month.get(month, 0) for month in months]

    # Plotly Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=income_values, name="Income", marker_color="green"))
    fig.add_trace(go.Bar(x=months, y=expense_values, name="Expenses", marker_color="red"))
    fig.update_layout(barmode="group", title="Monthly Income vs Expenses", xaxis_title="Month", yaxis_title="Amount ($)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("✅ This dashboard updates automatically based on your spreadsheet.")
