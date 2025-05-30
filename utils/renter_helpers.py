import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df, update_row_in_sheet
from utils.config import STATUS_OPTIONS

def load_renter_data(sheet_id, sheet_name):
    return load_sheet_as_df(sheet_id, sheet_name)

def display_renter_table(df):
    st.markdown("### Renter Log")
    st.dataframe(df[["Check-in", "Renter Name", "Amount", "Status", "Email", "Location"]], use_container_width=True)

def edit_renter_form(df, sheet_id, sheet_name):
    st.markdown("---")
    st.subheader("🔧 Edit Renter Entry")

    with st.form("edit_renter_form", clear_on_submit=False):
        row_index = st.number_input("Row index to edit (starting at 0)", min_value=0, max_value=len(df) - 1, step=1)
        selected = df.iloc[row_index]

        renter_name = st.text_input("Renter Name", selected.get("Renter Name", ""))
        email = st.text_input("Email", selected.get("Email", ""))
        location = st.text_input("Location", selected.get("Location", ""))
        amount = st.number_input("Amount", value=float(selected.get("Amount", 0.0)), step=10.0)

        current_status = selected.get("Status", STATUS_OPTIONS[1])
        status_index = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 1
        status = st.selectbox("Status", STATUS_OPTIONS, index=status_index)

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
            update_row_in_sheet(sheet_id, sheet_name, row_index + 2, updated_row)
            st.success("✅ Entry updated. Refresh to view changes.")
