import streamlit as st
from PIL import Image
from datetime import datetime
from features import dashboard, log_entry, view_entries, receipts, export, debug_expenses, log_payment

# --- Page Configuration ---
st.set_page_config(
    page_title="OPP Finance Tracker",
    page_icon="assets/favicon.png",
    layout="wide"
)

# --- Global Styles ---
st.markdown("""
<style>
body, .main {
    font-family: 'Segoe UI', sans-serif;
}
section[data-testid="stSidebar"] {
    background-color: #fdfdfd;
}
div[data-testid="metric-container"] {
    margin-bottom: 12px;
}
hr {
    margin-top: 30px;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# --- Optional Apple Touch Icon ---
st.markdown(
    '<link rel="apple-touch-icon" sizes="180x180" href="assets/logo-180.png">',
    unsafe_allow_html=True
)

# --- Sidebar Layout ---
sidebar_logo = Image.open("assets/favicon.png")
st.sidebar.image(sidebar_logo, use_container_width=True)
st.sidebar.title("📘 OPP Finance Tracker")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Rental Entry",
        "Log Payment",        # ✅ New Feature
        "View Entries",
        "Receipts",
        "Data Export",
        "Expense Debug"
    ]
)

# --- Sidebar Info ---
with st.sidebar.expander("🧭 App Info", expanded=True):
    st.markdown("**Version:** 1.3.0  \n**Updated:** May 2025")
    st.markdown("Built by: **Oceanview Property Partners**")

# --- Route Pages ---
routes = {
    "Dashboard": dashboard,
    "Rental Entry": log_entry,
    "Log Payment": log_payment,        # ✅ Route Added
    "View Entries": view_entries,
    "Receipts": receipts,
    "Data Export": export,
    "Expense Debug": debug_expenses,
}

routes[page].show()
