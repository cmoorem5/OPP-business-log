import streamlit as st
from utils.view_helpers import (
    load_and_prepare_data,
    get_filters_ui,
    apply_filters,
    show_data_table,
)
from utils.view_charts import show_summary_charts


def show():
    st.title("📂 View Logged Entries")

    if st.button("🔄 Refresh Data"):
        from utils.google_sheets import load_sheet_as_df
        load_sheet_as_df.clear()
        st.experimental_rerun()

    view_type = st.radio("Select Entry Type", ["Income", "Expense"], horizontal=True)
    year = st.selectbox("Year", ["2025", "2026"])

    df, skipped, date_col = load_and_prepare_data(view_type, year)
    filters = get_filters_ui(df, view_type, year)
    filtered = apply_filters(df.copy(), filters, date_col)

    show_data_table(filtered, view_type, year, skipped)
    show_summary_charts(filtered, view_type, date_col)
