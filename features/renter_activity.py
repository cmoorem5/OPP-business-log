import streamlit as st
from utils.config import SHEET_ID, STATUS_OPTIONS, DEFAULT_TAB_YEAR
from utils.renter_helpers import load_renter_data, display_renter_table, edit_renter_form

def show():
    st.title("📋 Renter Activity")

    # --- Year Selection ---
    year = st.selectbox("Select Year", ["2025", "2026"], index=["2025", "2026"].index(DEFAULT_TAB_YEAR), key="renter_year")
    sheet_name = f"{year} OPP Income"

    # --- Load Data ---
    df = load_renter_data(SHEET_ID, sheet_name)
    if df is None:
        return

    display_renter_table(df)
    edit_renter_form(df, sheet_name)
