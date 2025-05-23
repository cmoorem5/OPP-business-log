import streamlit as st
from utils.dashboard_helpers import (
    load_dashboard_data,
    build_financial_summary,
    render_summary_charts,
    render_property_charts
)

def show():
    st.title("📊 Finance Dashboard")

    df_income, df_expense = load_dashboard_data()
    summary = build_financial_summary(df_income, df_expense)

    render_summary_charts(summary)
    render_property_charts(summary)
