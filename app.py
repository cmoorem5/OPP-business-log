import streamlit as st
from PIL import Image
from features import dashboard, log_entry, view_entries, receipts, export

# Page configuration
st.set_page_config(
    page_title="OPP Finance Tracker",
    page_icon="assets/favicon.png",
    layout="wide",
)

# Optional: Apple touch icon for home screen bookmarks
st.markdown(
    """
    <link rel="apple-touch-icon" sizes="180x180" href="assets/favicon.png">
    """,
    unsafe_allow_html=True,
)

# Sidebar: Logo and navigation
sidebar_logo = Image.open("assets/logo-180.png")
st.sidebar.image(sidebar_logo, use_container_width=True)
st.sidebar.title("📘 OPP Finance Tracker")

page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Rental Entry", "View Entries", "Receipts", "Data Export"]
)

with st.sidebar.expander("🕒 Version History"):
    st.markdown(
        """
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
        """
    )

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
