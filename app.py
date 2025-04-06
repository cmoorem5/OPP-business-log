import streamlit as st
from features import dashboard, log_entry, view_entries, receipts, export

st.set_page_config(page_title="OPP Finance Tracker", layout="wide")

st.sidebar.title("📘 OPP Finance Tracker")
page = st.sidebar.radio("Navigate", ["Dashboard", "Log Entry", "View Entries", "Receipts", "Data Export"])

# Version history
with st.sidebar.expander("🕒 Version History"):
    st.markdown("""
    **v1.0.0** – Modular base app complete  
    - Dashboard with income/expenses and graph  
    - Log Entry form UI  
    - View & Export data  
    - Structure uses `features/` folder for pages

    **v1.1.0-dev** – Coming Soon  
    - Save entries to Google Sheets  
    - Receipt file storage  
    - Visual filters & date range tools
    """)

if page == "Dashboard":
    dashboard.show()
elif page == "Log Entry":
    log_entry.show()
elif page == "View Entries":
    view_entries.show()
elif page == "Receipts":
    receipts.show()
elif page == "Data Export":
    export.show()
