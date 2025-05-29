import streamlit as st
import pandas as pd
from datetime import datetime
from utils.google_sheets import load_sheet_as_df, update_row_in_sheet

def show():
    st.header("🧾 Renter Activity")

    year = st.selectbox("Select Year", ["2025", "2026"], index=0)
    sheet_name = f"{year} OPP Income"
    df = load_sheet_as_df(sheet_name)

    required_cols = ["Name", "Check-in", "Check-out", "Amount Owed", "Amount Received", "Status"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing columns: {', '.join(missing_cols)}")
        return

    df["Check-in"] = pd.to_datetime(df["Check-in"], errors="coerce")
    df_filtered = df.dropna(subset=["Name", "Check-in"]).copy()
    df_filtered["Renter ID"] = df_filtered["Name"] + " | " + df_filtered["Check-in"].dt.strftime("%Y-%m-%d")

    renter_id_list = df_filtered["Renter ID"].tolist()
    selected_id = st.selectbox("Select renter to update", renter_id_list)

    if selected_id:
        row_index = df_filtered[df_filtered["Renter ID"] == selected_id].index[0]
        selected = df_filtered.loc[row_index]

        with st.form("update_renter_form"):
            email = st.text_input("Email", value=selected.get("Email", ""))
            phone = st.text_input("Phone", value=selected.get("Phone", ""))
            amount_owed = st.number_input("Amount Owed", min_value=0.0, step=10.0, value=float(selected.get("Amount Owed", 0)))
            amount_received = st.number_input("Amount Received", min_value=0.0, step=10.0, value=float(selected.get("Amount Received", 0)))
            status = st.selectbox("Status", ["Paid", "PMT Due", "Downpayment Received"], 
                                  index=["Paid", "PMT Due", "Downpayment Received"].index(selected.get("Status", "PMT Due")))
            notes = st.text_area("Notes", value=selected.get("Notes", ""))
            submitted = st.form_submit_button("Update Renter Info")

        if submitted:
            balance = round(amount_owed - amount_received, 2)
            updates = {
                "Email": email,
                "Phone": phone,
                "Amount Owed": amount_owed,
                "Amount Received": amount_received,
                "Balance": balance,
                "Status": status,
                "Notes": notes
            }
            update_row_in_sheet(sheet_name, row_index, updates)
            st.success("✅ Renter information updated successfully.")
