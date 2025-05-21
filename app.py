import streamlit as st
from PIL import Image
from features import dashboard, log_entry, view_entries, receipts, export
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="OPP Finance Tracker",
    page_icon="assets/favicon.png",
    layout="wide",
)

# Inject custom CSS for theming
st.markdown(
    """
    <style>
    /* Base font and background */
    body, .main { font-family: 'Arial', sans-serif; background-color: #f8f9fa; }
    /* Card shadows */
    .stCard, .stFrame { box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    /* Heading color */
    h1, h2, h3, h4 { color: #2c3e50; }
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True
)

# Optional: Apple touch icon for bookmarks/home screen
st.markdown(
    '<link rel="apple-touch-icon" sizes="180x180" href="assets/logo-180.png">',
    unsafe_allow_html=True,
)

# Sidebar: logo & navigation
sidebar_logo = Image.open("assets/favicon.png")
st.sidebar.image(sidebar_logo, use_container_width=True)
st.sidebar.title("📘 OPP Finance Tracker")

page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Rental Entry", "View Entries", "Receipts", "Data Export"]
)

with st.sidebar.expander("🕒 Version History"):
    st.markdown(
        """
        **v1.3.0** – Support for 2026 income tracking  
        - Rental income now routed by year  
        - Dashboard uses rental start date  
        - Locked to 2025 data for now  
        
        **v1.2.0-dev** – Debugging tools added  
        **v1.1.0-dev** – Added Google Sheets + Drive integration  
        **v1.0.0** – Modular base app complete  
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

# Custom footer
st.markdown("---")
st.markdown(f"**© {datetime.now().year} Oceanview Property Partners** — Version 1.2.0-dev — Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
