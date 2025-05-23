import streamlit as st
import pandas as pd
from datetime import datetime
from utils.google_sheets import load_sheet_as_df, update_row_in_sheet

def show():
    st.header("Log Payment to Existing Booking")

    df = load_sheet_as_df("2025 OPP Income")  # Add year toggle if needed
    df = df.dropna(subset=["Name", "Rental Dates", "Amount Owed"])
    df["Amount Received"] = pd.to_numeric(df["Amount Received"], errors="coerce").fillna(0)
    df["Amount Owed"] = pd.to_numeric(df["Amount Owed"], errors="coerce")

    display_df = df[["Name", "Rental Dates", "Amount Owed", "Amount Received", "Status"]]
    selected = st.selectbox(
        "Select Booking",
        display_df.index,
        format_func=lambda i: f"{display_df.at[i, 'Name']} — {display_df.at[i, 'Rental Dates']} — {display_df.at[i, 'Status']}"
    )

    if selected is not None:
        row = df.loc[selected]
        st.write(f"**Total Owed:** ${row['Amount Owed']:.2f}")
        st.write(f"**Previously Received:** ${row['Amount Received']:.2f}")

        new_payment = st.number_input("New Payment Amount", min_value=0.0, step=50.0)
        note = st.text_input("Payment Note", placeholder="e.g., $1000 deposit on 5/15")

        if st.button("Apply Payment"):
            updated_received = float(row["Amount Received"]) + new_payment
            new_balance = float(row["Amount Owed"]) - updated_received

            # Determine new status
            if updated_received >= row["Amount Owed"]:
                new_status = "Paid"
            elif updated_received > 0:
                new_status = "Partial / Deposit"
            else:
                new_status = "PMT due"

            # Update Notes
            prev_notes = str(row["Notes"]) if pd.notna(row["Notes"]) else ""
            timestamp = datetime.now().strftime("%Y-%m-%d")
            updated_notes = f"{prev_notes} | {timestamp}: {note}" if note else prev_notes

            update_row_in_sheet("2025 OPP Income", selected, {
                "Amount Received": updated_received,
                "Balance": new_balance,
                "Status": new_status,
                "Notes": updated_notes.strip(" |")
            })

            st.success("Payment recorded successfully.")
