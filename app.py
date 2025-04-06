import streamlit as st
from pages import dashboard, log_entry, view_entries, receipts, export

st.set_page_config(page_title="OPP Finance Tracker", layout="wide")

st.sidebar.title("📘 OPP Finance Tracker")
page = st.sidebar.radio("Navigate", ["Dashboard", "Log Entry", "View Entries", "Receipts", "Data Export"])

# TEST: Confirm app is rendering and the page is being selected
st.write("✅ App loaded")
st.write("📂 Page selected:", page)

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
