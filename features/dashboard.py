import streamlit as st
from datetime import datetime
from utils.dashboard_helpers import (
    load_dashboard_data,
    calculate_summary_metrics,
    plot_monthly_financials,
    plot_outstanding_chart
)

def show():
    st.title("📊 Finance Dashboard")

    years = st.secrets["years"]
    current_year = str(datetime.now().year)
    selected_year = st.selectbox("Select Year", years, index=years.index(current_year))

    properties = ["Islamorada", "Standish"]
    selected_property = st.selectbox("Select Property", properties)

    df_income, df_expense = load_dashboard_data(selected_year, selected_property)

    if df_income.empty and df_expense.empty:
        st.warning("No financial data found for this property/year.")
        return

    # Metrics
    total_received, total_due, total_expenses, net_profit = calculate_summary_metrics(df_income, df_expense)

    st.columns(4)[0].metric("✅ Received", f"${total_received:,.0f}")
    st.columns(4)[1].metric("🕗 Still Owed", f"${total_due:,.0f}")
    st.columns(4)[2].metric("💸 Expenses", f"${total_expenses:,.0f}")
    st.columns(4)[3].metric("📈 Profit", f"${net_profit:,.0f}")

    # Financial Graphs
    plot_monthly_financials(df_income, df_expense)

    with st.expander("📉 What Is Still Owed"):
        plot_outstanding_chart(df_income)
