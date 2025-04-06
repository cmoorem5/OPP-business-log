import streamlit as st
from pages import dashboard, log_entry, view_entries, receipts, export

st.set_page_config(page_title="OPP Finance Tracker", layout="wide")

st.sidebar.title("📘 OPP Finance Tracker")
page = st.sidebar.radio("Navigate", ["Dashboard", "Log Entry", "View Entries", "Receipts", "Data Export"])

# Debug info
st.write("DEBUG: App loaded. Selected page:", page)
st.write("DEBUG: dashboard is", dashboard)

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
