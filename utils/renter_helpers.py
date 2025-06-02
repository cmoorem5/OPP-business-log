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
    st.subheader("✏️ Inline Edit Renter Entries")

    # Show editable table
    edited_df = st.data_editor(
        df[REQUIRED_COLUMNS],
        use_container_width=True,
        num_rows="dynamic",
        disabled=[],
        key="renter_edit"
    )

    # Compare changes
    if st.button("✅ Apply Changes"):
        changes = 0
        for i in range(len(edited_df)):
            original = df.loc[i, REQUIRED_COLUMNS]
            updated = edited_df.loc[i, REQUIRED_COLUMNS]
            if not original.equals(updated):
                updates = updated.to_dict()
                try:
                    update_row_in_sheet(SHEET_ID, sheet_name, i, updates)
                    changes += 1
                except Exception as e:
                    st.error(f"❌ Row {i + 2} update failed: {e}")
        if changes:
            st.success(f"✅ {changes} row(s) updated.")
            st.experimental_rerun()
        else:
            st.info("No changes to apply.")
