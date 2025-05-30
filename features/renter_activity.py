import streamlit as st
from utils.config import DEFAULT_TAB_YEAR
from utils.renter_helpers import (
    load_renter_data,
    display_renter_table,
    edit_renter_form
)

def show():
    st.title("📋 Renter Activity")

    # --- Year Selection ---
    year = st.selectbox("Select Year", ["2025", "2026"], index=["2025", "2026"].index(DEFAULT_TAB_YEAR), key="renter_year")

    # --- Load + Validate ---
    try:
        df, sheet_name = load_renter_data(year)
    except Exception as e:
        st.error(f"❌ Failed to load sheet: {e}")
        st.stop()

    if df.empty:
        st.warning(f"No data found in {sheet_name}")
        return

    required_cols = ["Check-in", "Renter Name", "Amount", "Status", "Email", "Location"]
    if not all(col in df.columns for col in required_cols):
        st.error("Sheet is missing one or more required columns.")
        return

    # --- Display + Edit ---
    display_renter_table(df)
    st.markdown("---")
    edit_renter_form(df, sheet_name)
