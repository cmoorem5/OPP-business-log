import streamlit as st
from utils.data_loader import load_excel_data

def show():
    st.markdown("## 📂 View Entries")
    view_type = st.radio("Select data to view:", ["Income", "Expenses"], horizontal=True)

    if view_type == "Income":
        df = load_excel_data("2025 OPP Income")
        st.dataframe(df, use_container_width=True)
    else:
        df = load_excel_data("2025 OPP Expenses")
        st.dataframe(df, use_container_width=True)
