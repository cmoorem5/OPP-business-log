import streamlit as st
from datetime import datetime
from utils.dashboard_helpers import (
    load_dashboard_data,
    build_financial_summary,
    render_property_charts,
)

def show():
    st.title("📊 Finance Dashboard")

    # Year selector
    years = st.secrets["years"]
    current_year = str(datetime.now().year)
    default_index = years.index(current_year) if current_year in years else 0
    selected_year = st.selectbox("Select Year", years, index=default_index)

    # Load + summarize
    df_income, df_expense = load_dashboard_data(selected_year)
    summary = build_financial_summary(df_income, df_expense)

    # CSV Export
    csv = summary.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Summary CSV",
        data=csv,
        file_name=f"{selected_year}_summary.csv",
        mime="text/csv",
    )

    # Charts
    render_property_charts(summary)
