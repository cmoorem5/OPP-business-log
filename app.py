import streamlit as st
from PIL import Image
from features import dashboard, log_entry, view_entries, receipts, export, debug_credentials, debug_dashboard

st.set_page_config(page_title="OPP Finance Tracker", layout="wide")

logo = Image.open("assets/logo.jpg")
st.sidebar.image(logo, use_container_width=True)

st.sidebar.title("📘 OPP Finance Tracker")
page = st.sidebar.radio("Navigate", [
    "Dashboard", 
    "Rental Entry", 
    "View Entries", 
    "Receipts", 
    "Data Export", 
    "Debug Credentials",
    "Debug Dashboard"
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
elif page == "Debug Credentials":
    debug_credentials.show()
elif page == "Debug Dashboard":
    debug_dashboard.show()
