import streamlit as st
from datetime import date
from utils.google_sheets import append_row_to_sheet
from utils.google_drive import upload_file_to_drive
from utils.config import get_drive_folder_id


def show():
    st.title("📝 Log New Entry")
    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])

    # --- INCOME ENTRY ---
    if entry_type == "Income":
        with st.form("income_form", clear_on_submit=True):
            year = st.selectbox("Log Income To:", ["2025", "2026"], key="income_year")
            sheet_name = f"{year} OPP Income"

            booking_date = st.date_input("Booking Date", date.today())
            rental_dates = st.date_input("Rental Date Range", (date.today(), date.today()))
            check_in, check_out = rental_dates

            amount = st.number_input("Amount Received", min_value=0.0, step=10.0)
            payment_type = st.selectbox("Payment Type", ["Zelle", "Check", "Cash", "Venmo", "Other"])
            status = st.selectbox("Payment Status", ["Paid", "PMT due", "Downpayment received"])

            renter_name = st.text_input("Renter Name")
            email = st.text_input("Renter Email")
            origin = st.text_input("Where are they from?")
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Log Income"):
                row = [
                    booking_date.strftime("%B"),
                    booking_date.strftime("%Y-%m-%d"),
                    renter_name,
                    f"Rental {check_in} to {check_out}",
                    "Islamorada",  # Static property
                    payment_type,
                    amount,
                    notes,
                    "",  # Receipt Link placeholder
                    email,
                    origin,
                    check_in.strftime("%Y-%m-%d"),
                    check_out.strftime("%Y-%m-%d"),
                    status,
                    amount,
                    amount,
                    0.0
                ]
                append_row_to_sheet(sheet_name, row)
                st.success("✅ Income logged successfully.")

    # --- EXPENSE ENTRY ---
    elif entry_type == "Expense":
        with st.form("expense_form", clear_on_submit=True):
            year = st.selectbox("Log Expense To:", ["2025", "2026"], key="expense_year")
            sheet_name = f"{year} OPP Expenses"

            expense_date = st.date_input("Expense Date", date.today())
            month = expense_date.strftime("%B")  # Used for Drive folder & row

            purchaser = st.selectbox("Purchaser", [
                "Cash", "Debit C6270", "JB C6443B", "JB J5062B", "JB C1112",
                "JB J0186", "JB J7698", "Jordans", "OPP Checking",
                "OPP JetBlue", "Return", "TJ MAXX Card"
            ])

            item = st.text_input("Item/Description")
            property_selected = st.selectbox("Property", ["Islamorada", "Standish", "Other"])
            category = st.selectbox("Category", [
                "Property Expense", "Furnishings & Supplies", "Guest & Operational Expenses",
                "Travel & Transportation", "Legal & Professional Services", "Food & Beverage",
                "Taxes & Compliance", "Business Expansion & Improvements", "Misc & Other"
            ])
            amount = st.number_input("Amount", min_value=0.0, step=10.0)
            comments = st.text_area("Comments (optional)")
            receipt_file = st.file_uploader("Upload Receipt", type=["jpg", "jpeg", "png", "pdf"])

            if st.form_submit_button("Log Expense"):
                drive_url = ""

                if receipt_file:
                    try:
                        folder_id = get_drive_folder_id(month)  # ✅ Fixed for your setup
                        drive_url = upload_file_to_drive(receipt_file, folder_id)
                    except Exception as e:
                        st.error(f"❌ Upload failed: {e}")
                        return

                row = [
                    month,
                    expense_date.strftime("%Y-%m-%d"),
                    purchaser,
                    item,
                    property_selected,
                    category,
                    amount,
                    comments,
                    drive_url
                ]
                append_row_to_sheet(sheet_name, row)
                st.success("✅ Expense logged successfully.")
