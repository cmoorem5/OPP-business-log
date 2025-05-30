import streamlit as st
from utils.config import years
from utils.renter_helpers import load_renter_data, display_renter_table, edit_renter_form

def show():
    st.title("📋 Renter Activity")

    year = st.radio("Select Year", years, horizontal=True)
    sheet_name = f"{year} OPP Income"

    df = load_renter_data(sheet_name)

    if df.empty:
        return

    display_renter_table(df)
    edit_renter_form(df, sheet_name)
