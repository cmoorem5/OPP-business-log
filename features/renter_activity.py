import streamlit as st
import pandas as pd
from datetime import datetime
from utils.google_sheets import load_sheet_as_df, update_row_in_sheet
import re

def extract_start_date(rental_str):
    if not isinstance(rental_str, str):
        return pd.NaT
    match = re.search(r"\d{1,2}/\d{1,2}/\d{4}", rental_str)
    if match:
        return pd.to_datetime(match.group(0), errors="coerce")
    return pd.NaT

def show():
    st.header("🧾 Renter Activity")

    year = st.selectbox("Select Year", ["2025", "2026"], index=0)
    sheet_name = f"{year} OPP Income"
    df = load_sheet_as_df(sheet_name)

    if "Rental Dates" not in df.columns or "Name" not in df.columns:
        st.error("Missing 'Rental Dates' or 'Name' column in the sheet.")
        return

    # Normalize dates and amounts
    df["Start Date"] = df["Rental Dates"].apply(extract_start_date)
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df["Amount Owed"] = pd.to_numeric(df.get("Amount Owed", 0), errors="coerce").fillna(0.0)
    df["Amount Received"] = pd.to_numeric(df.get("Amount Received", 0), errors="coerce").fillna(0.0)
    df["Balance"] = df["Amount Owed"] - df["Amount Received"]

    # Filter to rows with valid renters
    df = df[
        (df["Name"].notna()) &
        (df["Rental Dates"].notna())
    ].copy()

    df["Property"] = df.get("Property", "Unspecified")
    df["Status"] = df.get("Status", "PMT due").fillna("PMT due")

    # Filter UI
    st.subheader("Filter Renters")
    all_properties = sorted(df["Property"].dropna().unique())
    selected_properties = st.multiselect("Filter by Property", all_properties, default=all_properties)

    all_statuses = ["Paid", "PMT due", "Downpayment received"]
    selected_statuses = st.multiselect("Filter by Status", all_statuses, default=all_statuses)

    filtered_df = df[
        (df["Property"].isin(selected_properties)) &
        (df["Status"].isin(selected_statuses))
    ].copy()

    if filtered_df.empty:
        st.info("No renters match the selected filters.")
        return

    # Dropdown label
    filtered_df["Label"] = filtered_df.apply(
        lambda row: f"{row['Name']} — {row['Property']} ({row['Rental Dates']}) — Balance: ${row['Balance']:,.2f}",
        axis=1
    )

    selected_label = st.selectbox("Choose Renter to Edit", filtered_df["Label"])
    selected_row = filtered_df[filtered_df["Label"] == selected_label].iloc[0]
    selected_index = selected_row.name

    st.subheader("Edit Renter Info")

    with st.form("edit_renter_form"):
        name = st.text_input("Name", value=selected_row["Name"])
        email = st.text_input("Email", value=selected_row.get("Email", ""))
        phone = st.text_input("Phone", value=selected_row.get("Phone", ""))
        address = st.text_input("Address", value=selected_row.get("Address", ""))
        city = st.text_input("City", value=selected_row.get("City", ""))
        state = st.text_input("State", value=selected_row.get("State", ""))
        zip_code = st.text_input("Zip", value=selected_row.get("Zip", ""))
        amount_owed = st.number_input("Amount Owed", min_value=0.0, step=10.0, value=float(selected_row["Amount Owed"]))
        amount_received = st.number_input("Amount Received", min_value=0.0, step=10.0, value=float(selected_row["Amount Received"]))
        balance = amount_owed - amount_received

        status_options = ["Paid", "PMT due", "Downpayment received"]
        current_status = selected_row.get("Status", "PMT due")
        status_index = status_options.index(current_status) if current_status in status_options else 1
        status = st.selectbox("Status", status_options, index=status_index)

        if balance <= 0:
            status = "Paid"

        notes = st.text_area("Notes", value=selected_row.get("Notes", ""))
        submitted = st.form_submit_button("Update Renter Info")

    if submitted:
        updated_data = {
            "Name": name,
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
        }
        update_row_in_sheet(sheet_name, selected_index + 2, updated_data)
        st.success("Renter info updated successfully.")
        st.experimental_rerun()
