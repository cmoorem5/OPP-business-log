import streamlit as st
from PIL import Image
from datetime import datetime
from features import dashboard, log_entry, view_entries, export, renter_activity

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
st.sidebar.image(Image.open("assets/favicon.png"), use_container_width=True)
st.sidebar.title("📘 OPP Finance Tracker")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Rental Entry",
        "Renter Activity",
        "View Entries",
        "Data Export"
    ]
)

with st.sidebar.expander("🧭 App Info", expanded=True):
    st.markdown("**Version:** 1.3.0  \n**Updated:** May 2025")
    st.markdown("Built by: **Oceanview Property Partners**")

# --- Route Pages ---
routes = {
    "Dashboard": dashboard,
    "Rental Entry": log_entry,
    "Renter Activity": renter_activity,
    "View Entries": view_entries,
    "Data Export": export
}

# --- Load Selected Page with Error Catch ---
try:
    routes[page].show()
except Exception as e:
    st.error(f"❌ Page load failed: {type(e).__name__} — {e}")
