import streamlit as st
from datetime import date, datetime
import tempfile
import os

from utils.google_sheets import load_sheet_as_df, append_row
from utils.google_drive import upload_file_to_drive
from utils.config import get_drive_folder_id

def show():
    """Log a new income or expense entry with optional receipt upload."""
    st.title("📝 Log New Entry")

    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])

    if entry_type == "Income":
        # ─── INCOME FORM ───────────────────────────────────────────────
        with st.form("income_form", clear_on_submit=True):
            entry_date = st.date_input("Date", date.today(), key="income_date")
            amount = st.number_input("Amount", min_value=0.0, step=0.01, key="income_amount")
            source = st.text_input("Income Source")
            rental_dates = st.date_input("Rental Date Range", (date.today(), date.today()), key="rental_dates")
            property_location = st.selectbox("Property", ["Florida", "Maine"], key="income_property")
            payment_status = st.selectbox(
                "Payment Status",
                ["Paid", "Cancelled", "PMT Due", "Downpayment Received"],
                key="payment_status"
            )

            st.markdown("#### 👤 Renter Contact Info (Optional)")
            renter_name = st.text_input("Renter Name", key="renter_name")
            renter_email = st.text_input("Renter Email", key="renter_email")
            renter_address = st.text_input("Address", key="renter_address")
            renter_city = st.text_input("City", key="renter_city")
            renter_state = st.text_input("State", key="renter_state")
            renter_zip = st.text_input("Zip Code", key="renter_zip")

            submitted = st.form_submit_button("Submit Income Entry")

        if submitted:
            errors = []
            if entry_date > date.today():
                errors.append("❗ Date cannot be in the future.")
            if amount <= 0:
                errors.append("❗ Amount must be greater than zero.")
            if errors:
                for err in errors:
                    st.error(err)
            else:
                month = entry_date.strftime("%B")
                rental_range = f"{rental_dates[0]} - {rental_dates[1]}"
                row = [
                    month, property_location, rental_range, source, "", amount,
                    payment_status, "", renter_name, renter_address,
                    renter_city, renter_state, renter_zip, renter_email
                ]
                with st.spinner("Submitting income entry..."):
                    append_row("OPP Finance Tracker", "2025 OPP Income", row)
                st.success("✅ Income entry submitted!")

    else:
        # ─── EXPENSE FORM ───────────────────────────────────────────────
        with st.spinner("Loading dropdown data..."):
            purchasers_df = load_sheet_as_df("OPP Finance Tracker", "Purchasers")
            purchaser_list = sorted(purchasers_df["Purchaser"].dropna().unique().tolist())
            purchaser_list.append("Other")

            expenses_df = load_sheet_as_df("OPP Finance Tracker", "2025 OPP Expenses")
            category_list = sorted(expenses_df.get("Category", []).dropna().unique().tolist())
            category_list.append("Other")

        with st.form("expense_form", clear_on_submit=True):
            entry_date = st.date_input("Date", date.today(), key="expense_date")
            amount = st.number_input("Amount", min_value=0.0, step=0.01, key="expense_amount")

            purchaser = st.selectbox("Purchaser", purchaser_list, key="purchaser")
            if purchaser == "Other":
                purchaser = st.text_input("Enter Purchaser Name", key="purchaser_other")

            item = st.text_input("Item/Description", key="item")
            property_location = st.selectbox("Property", ["Florida", "Maine"], key="expense_property")

            category = st.selectbox("Category", category_list, key="category")
            if category == "Other":
                category = st.text_input("Enter Category", key="category_other")

            comments = st.text_area("Comments", key="comments")
            uploaded_file = st.file_uploader(
                "Upload Receipt File", type=["pdf", "png", "jpg", "jpeg"], key="receipt_uploader"
            )

            submitted = st.form_submit_button("Submit Expense Entry")

        if submitted:
            errors = []
            if entry_date > date.today():
                errors.append("❗ Date cannot be in the future.")
            if amount <= 0:
                errors.append("❗ Amount must be greater than zero.")
            if errors:
                for err in errors:
                    st.error(err)
            else:
                receipt_link = ""
                if uploaded_file:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        tmp_path = tmp.name
                    try:
                        with st.spinner("Uploading receipt to Drive..."):
                            folder_id = get_drive_folder_id(entry_date)
                            if folder_id:
                                file_id = upload_file_to_drive(tmp_path, uploaded_file.name, folder_id)
                                receipt_link = f"https://drive.google.com/file/d/{file_id}/view"
                            else:
                                st.warning(
                                    f"No folder configured for {entry_date.year} "
                                    f"{entry_date.strftime('%B')} — receipt not uploaded."
                                )
                    finally:
                        os.remove(tmp_path)

                row = [
                    entry_date.strftime("%B"), str(entry_date), purchaser, item,
                    property_location, category, amount, comments, receipt_link
                ]
                with st.spinner("Submitting expense entry..."):
                    append_row("OPP Finance Tracker", "2025 OPP Expenses", row)
                st.success("✅ Expense entry submitted!")

    # ─── Custom footer ─────────────────────────────────────────────────────
    st.markdown("---")
    last_updated = datetime.now().strftime("%B %d, %Y %I:%M %p")
    footer = f"""
    <div style="text-align:center; font-size:0.85em; color:gray;">
      Oceanview Property Partners • v1.3.0 • Last updated: {last_updated}
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)
