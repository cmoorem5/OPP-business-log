import streamlit as st 
import pandas as pd
from utils.google_sheets import load_sheet_as_df, update_row_in_sheet
from utils.config import SHEET_ID, STATUS_OPTIONS

REQUIRED_COLUMNS = [
    "Check-in", "Name", "Email", "Phone", "Address", "City", "State", "Zip",
    "Amount Owed", "Amount Received", "Balance", "Status", "Notes"
]

def load_renter_data(sheet_name: str) -> pd.DataFrame:
    try:
        df = load_sheet_as_df(SHEET_ID, sheet_name)
        if df.empty:
            st.warning(f"No data found in '{sheet_name}'")
        return df
    except Exception as e:
        st.error(f"❌ Failed to load sheet: {e}")
        return pd.DataFrame()

def display_renter_table(df: pd.DataFrame):
    st.markdown("### Renter Log")
    valid_cols = [col for col in REQUIRED_COLUMNS if col in df.columns]
    if not valid_cols:
        st.error("❌ Sheet is missing all required columns.")
    else:
        st.dataframe(df[valid_cols], use_container_width=True)

def edit_renter_form(df: pd.DataFrame, sheet_name: str):
    if df.empty:
        return

    if not all(col in df.columns for col in REQUIRED_COLUMNS):
        st.error("❌ Sheet is missing one or more required columns for editing.")
        return

    st.markdown("---")
    st.subheader("🔧 Edit Renter Entry")

    with st.form("edit_renter_form", clear_on_submit=False):
        row_index = st.number_input("Row index to edit (starting at 0)", min_value=0, max_value=len(df) - 1, step=1)
        selected = df.iloc[row_index]

        renter_name = st.text_input("Renter Name", selected.get("Name", ""))
        email = st.text_input("Email", selected.get("Email", ""))
        phone = st.text_input("Phone", selected.get("Phone", ""))
        address = st.text_input("Address", selected.get("Address", ""))
        city = st.text_input("City", selected.get("City", ""))
        state = st.text_input("State", selected.get("State", ""))
        zip_code = st.text_input("Zip", selected.get("Zip", ""))

        amount_owed = st.number_input("Amount Owed", value=float(selected.get("Amount Owed", 0.0)), step=10.0)
        amount_received = st.number_input("Amount Received", value=float(selected.get("Amount Received", 0.0)), step=10.0)
        balance = round(amount_owed - amount_received, 2)
        st.write(f"💰 Balance: **${balance:.2f}**")

        current_status = selected.get("Status", STATUS_OPTIONS[1])
        status_index = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 1
        status = st.selectbox("Status", STATUS_OPTIONS, index=status_index)

        notes = st.text_area("Notes", selected.get("Notes", ""))

        submitted = st.form_submit_button("Update Entry")
        if submitted:
            updated_row = selected.to_dict()
            updated_row.update({
                "Name": renter_name,
                "Email": email,
                "Phone": phone,
                "Address": address,
                "City": city,
                "State": state,
                "Zip": zip_code,
                "Amount Owed": amount_owed,
                "Amount Received": amount_received,
                "Balance": balance,
                "Status": status,
                "Notes": notes
            })

            try:
                update_row_in_sheet(SHEET_ID, sheet_name, row_index + 2, updated_row)
                st.success("✅ Entry updated. Refresh to view changes.")
            except Exception as e:
                st.error(f"❌ Failed to update entry: {e}")
