import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df, update_row_in_sheet

# --- Load Google Sheet ID from secrets ---
SHEET_ID = st.secrets["gsheet_id"]

def show():
    st.title("📋 Renter Activity")

    # --- Year Selection ---
    year = st.selectbox("Select Year", ["2025", "2026"], key="renter_year")
    sheet_name = f"{year} OPP Income"

    # --- Load Data ---
    df = load_sheet_as_df(SHEET_ID, sheet_name)
    if df.empty:
        st.warning(f"No data found in {sheet_name}")
        return

    # --- Display Table ---
    st.markdown("### Renter Log")
    st.dataframe(df[["Check-in", "Renter Name", "Amount", "Status", "Email", "Location"]], use_container_width=True)

    # --- Edit Entry Form ---
    st.markdown("---")
    st.subheader("🔧 Edit Renter Entry")
    with st.form("edit_renter_form", clear_on_submit=False):
        row_index = st.number_input("Row index to edit (starting at 0)", min_value=0, max_value=len(df) - 1, step=1)
        selected = df.iloc[row_index]

        renter_name = st.text_input("Renter Name", selected.get("Renter Name", ""))
        email = st.text_input("Email", selected.get("Email", ""))
        location = st.text_input("Location", selected.get("Location", ""))
        amount = st.number_input("Amount", value=float(selected.get("Amount", 0.0)), step=10.0)

        status_options = ["Paid", "PMT Due", "Downpayment Received"]
        current_status = selected.get("Status", "PMT Due")
        status_index = status_options.index(current_status) if current_status in status_options else 1
        status = st.selectbox("Status", status_options, index=status_index)

        submitted = st.form_submit_button("Update Entry")
        if submitted:
            updated_row = selected.to_dict()
            updated_row.update({
                "Renter Name": renter_name,
                "Email": email,
                "Location": location,
                "Amount": amount,
                "Status": status
            })
            update_row_in_sheet(SHEET_ID, sheet_name, row_index + 2, updated_row)  # +2 to account for header + 1-index
            st.success("Entry updated. Refresh to view updated table.")

