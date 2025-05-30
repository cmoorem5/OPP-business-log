import streamlit as st
from utils.renter_helpers import (
    load_renter_data,
    display_renter_table,
    edit_renter_form
)
from utils.config import SHEET_ID, DEFAULT_TAB_YEAR

def show():
    st.title("📋 Renter Activity")

    # --- Year Selector ---
    year = st.selectbox("Select Year", ["2025", "2026"], index=["2025", "2026"].index(DEFAULT_TAB_YEAR), key="renter_year")
    sheet_name = f"{year} OPP Income"

    # --- Load Data ---
    try:
        df = load_renter_data(SHEET_ID, sheet_name)
    except Exception as e:
        st.error(f"❌ Failed to load sheet: {e}")
        st.stop()

    if df.empty:
        st.warning(f"No data found in {sheet_name}")
        return

    display_renter_table(df)
    edit_renter_form(df, SHEET_ID, sheet_name)
