import streamlit as st
from PIL import Image
from features import (
    dashboard,
    log_entry,
    view_entries,
    receipts,
    export,
)

# Load icons
icon = Image.open("assets/logo-180.png")      # for favicon & iOS home-screen
sidebar_logo = Image.open("assets/logo.jpg")  # full-size for sidebar

# Configure page
st.set_page_config(
    page_title="OPP Finance Tracker",
    page_icon=icon,
    layout="wide",
)

# Inject Apple touch icon
st.markdown(
    '<link rel="apple-touch-icon" sizes="180x180" href="assets/logo-180.png">',
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.image(sidebar_logo, use_container_width=True)
st.sidebar.title("📘 OPP Finance Tracker")
page = st.sidebar.radio("Navigate", [
    "Dashboard",
    "Rental Entry",
    "View Entries",
    "Receipts",
    "Data Export",
    "Debug Credentials",
    "Debug Dashboard",
])

with st.sidebar.expander("🕒 Version History"):
    st.markdown("""
    **v1.0.0** – Modular base app complete  
    - Dashboard with income/expenses and graph  
    - Log Entry form UI  
    - View & Export data  
    - Structure uses `features/` folder for pages

    **v1.1.0-dev** – Added Google Sheets + Drive integration  
    - Monthly routing for receipts  
    - Income & expense logging live  
    - View clickable receipt links

    **v1.2.0-dev** – Debugging tools added  
    - Secret validator  
    - Live income data parser
    """)

# Page routing
if page == "Dashboard":
    dashboard.show()
elif page == "Rental Entry":
    log_entry.show()
elif page == "View Entries":
    view_entries.show()
elif page == "Receipts":
    receipts.show()
elif page == "Data Export":
    export.show()


