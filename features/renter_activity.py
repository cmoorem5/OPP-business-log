import streamlit as st
import pandas as pd
from datetime import date
from utils.google_sheets import load_sheet_as_df, update_row_in_sheet
from utils.config import SHEET_ID

def show():
    st.title("📋 Renter Activity")

    year = st.selectbox("Select Year", ["2025", "2026"], key="renter_year")
    sheet_name = f"{year} OPP Income"

    df = load_sheet_as_df(SHEET_ID, sheet_name)
    if df.empty:
        st.warning(f"No data found in {sheet_name}")
        return

    editable_cols = ["Status", "Amount", "Renter Name", "Email", "Location"]
    df_display = df[["Check-in", "Renter Name", "Amount", "Status", "Email", "Location"]].copy()
    st.dataframe(df_display, use_container_width=True)

    st.markdown("### Edit Renter Entry")
    with st.form("edit_renter_form", clear_on_submit=False):
        selected_index = st.number_input("Row number to edit (starting at 0)", min_value=0, max_value=len(df) - 1, step=1)
        selected_row = df.iloc[selected_index]

        renter_name = st.text_input("Renter Name", selected_row.get("Renter Name", ""))
        email = st.text_input("Email", selected_row.get("Email", ""))
        location = st.text_input("Location", selected_row.get("Location", ""))
        amount = st.number_input("Amount", value=float(selected_row.get("Amount", 0.0)), step=10.0)
        status_options = ["Paid", "PMT Due", "Downpayment Received"]
        status = st.selectbox("Status", status_options, index=status_options.index(selected_row.get("Status", "PMT Due")) if selected_row.get("Status", "PMT Due") in status_options else 1)

        submitted = st.form_submit_button("Update Entry")
        if submitted:
            updated_row = selected_row.to_dict()
            updated_row.update({
                "Renter Name": renter_name,
                "Email": email,
                "Location": location,
                "Amount": amount,
                "Status": status
            })
            update_row_in_sheet(SHEET_ID, sheet_name, selected_index + 2, updated_row)  # +2 for 1-based index + header
            st.success("Entry updated. Please refresh to see changes.")

