import streamlit as st
import pandas as pd
from datetime import datetime
from utils.google_sheets import load_sheet_as_df, update_row_in_sheet

def show():
    st.header("🧾 Renter Activity")

    year = st.selectbox("Select Year", ["2025", "2026"], index=0)
    sheet_name = f"{year} OPP Income"
    df = load_sheet_as_df(sheet_name)

    st.subheader("Select Renter to Edit")

    # DEBUG: show columns in case of mismatch
    st.write("Columns found:", df.columns.tolist())

    if "Rental Start" not in df.columns or "Rental End" not in df.columns:
        st.error("Missing 'Rental Start' or 'Rental End' column in the sheet.")
        return

    df["Rental Start"] = pd.to_datetime(df["Rental Start"], errors="coerce")
    df["Rental End"] = pd.to_datetime(df["Rental End"], errors="coerce")
    today = pd.Timestamp.today()

    active_df = df[
        (df["Rental End"] >= today) &
        (df["Renter Name"].notna())
    ].copy()

    if active_df.empty:
        st.info("No active or upcoming renters to edit.")
        return

    active_df["Label"] = active_df.apply(
        lambda row: f"{row['Renter Name']} — {row['Property']} ({row['Rental Start'].strftime('%b %d')} to {row['Rental End'].strftime('%b %d')})",
        axis=1
    )

    selected_label = st.selectbox("Choose Renter", active_df["Label"])
    selected_row = active_df[active_df["Label"] == selected_label].iloc[0]
    selected_index = selected_row.name  # original index for update

    st.subheader("Edit Renter Info")

    with st.form("edit_renter_form"):
        renter_name = st.text_input("Renter Name", value=selected_row["Renter Name"])
        email = st.text_input("Email Address", value=selected_row.get("Email", ""))
        origin = st.text_input("Location (City, State)", value=selected_row.get("Location", ""))
        amount = st.number_input("Payment Amount", min_value=0.0, step=10.0, value=float(selected_row["Amount"]))
        payment_status = st.selectbox("Payment Status", ["Paid", "PMT due", "Downpayment received"],
                                      index=["Paid", "PMT due", "Downpayment received"].index(selected_row["Complete"]))
        notes = st.text_area("Notes", value=selected_row.get("Notes", ""))
        submitted = st.form_submit_button("Update Renter Info")

    if submitted:
        updated_data = {
            "Renter Name": renter_name,
            "Email": email,
            "Location": origin,
            "Amount": amount,
            "Complete": payment_status,
            "Notes": notes,
        }
        update_row_in_sheet(sheet_name, selected_index + 2, updated_data)
        st.success("Renter info updated successfully.")
        st.experimental_rerun()
