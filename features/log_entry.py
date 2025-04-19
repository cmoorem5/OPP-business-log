import streamlit as st
from datetime import date
from utils.data_loader import load_excel_data
from utils.google_sheets import append_row
from utils.google_drive import upload_file_to_drive
import os
import tempfile

monthly_folders_2025 = {
    "April": "1wPerZFB-9FufTZOGfFXf2xMVg4VlGtdC",
    "May": "1e12yCfo8WZS8gnYuSPbxeHiZ1aVWbbJe",
    "June": "1WRSSZUGPHgGvd1cSUNDEjpTGq2FmrqcZ",
    "July": "10nWoAibOWzVeWx0Qn3TC8Z6g-UXkToPd",
    "August": "1xvT2NA9rPpXX0SQ1CKE9NeTbc9mvrgxK",
    "September": "160isZV8ja5Kgw7sKx88f969tIUZR6Jfo",
    "October": "1XbP4T78e71CYA5s-1ksPYK6bujmo-UQn",
    "November": "1zxxtG1cwvpcckQ3nvB3zKHStxDBfRFF6",
    "December": "1iJwfC3siEudH8uzdZGwlid6ufhFG5AMb"
}

def show():
    st.markdown("## 📝 Log New Entry")

    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])
    entry_date = st.date_input("Date", date.today())
    amount = st.number_input("Amount", min_value=0.0, value=0.0, step=1.0)

    if entry_type == "Income":
        source = st.text_input("Income Source")
        rental_dates = st.date_input("Rental Date Range", value=(date.today(), date.today()))

        st.markdown("### 👤 Renter Details")
        renter_name = st.text_input("Renter Name")
        renter_email = st.text_input("Email Address")
        renter_location = st.text_input("Where are they from?")
        property_location = st.selectbox("Property", ["Florida", "Maine"])
        payment_status = st.selectbox("Payment Status", ["Paid", "PMT due", "Downpayment received"])
    else:
        purchasers_df = load_excel_data("Purchasers")
        purchaser_list = purchasers_df["Purchaser"].dropna().unique().tolist()
        purchaser = st.selectbox("Purchaser", purchaser_list + ["Other"])
        if purchaser == "Other":
            purchaser = st.text_input("Enter Purchaser Name")

        item = st.text_input("Item")
        property_location = st.selectbox("Property", ["Florida", "Maine"])

        expenses_df = load_excel_data("2025 OPP Expenses")
        categories = expenses_df["Category"].dropna().unique() if "Category" in expenses_df.columns else []
        category = st.selectbox("Category", categories if len(categories) else ["General"])
        comments = st.text_area("Comments")

        st.markdown("### 📎 Upload Receipt (optional)")
        uploaded_file = st.file_uploader("Upload Receipt File", type=["pdf", "png", "jpg", "jpeg"])
        receipt_link = ""

        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_file_path = tmp_file.name

            try:
                month_name = entry_date.strftime("%B")
                folder_id = monthly_folders_2025.get(month_name)
                if folder_id:
                    file_id = upload_file_to_drive(
                        file_path=tmp_file_path,
                        file_name=uploaded_file.name,
                        folder_id=folder_id
                    )
                    receipt_link = f"https://drive.google.com/file/d/{file_id}/view"
                else:
                    st.warning("No folder configured for {} 2025.".format(month_name))
            except Exception as e:
                st.warning(f"Receipt upload failed: {e}")
            finally:
                os.remove(tmp_file_path)

    if st.button("Submit Entry"):
        try:
            sheet_name = "OPP Finance Tracker"

            if entry_type == "Income":
                tab_name = "2025 OPP Income"
                month = entry_date.strftime("%B")
                rental_range = f"{rental_dates[0]} - {rental_dates[1]}"
                row = [
                    month, rental_range, source, "",  # Description/Invoice No. left blank
                    amount, payment_status, "",       # Notes left blank
                    renter_name, "",                  # Address left blank
                    renter_location, "", "",          # City, State, Zip
                    renter_email
                ]
            else:
                tab_name = "2025 OPP Expenses"
                month = entry_date.strftime("%B")
                row = [
                    month, str(entry_date), purchaser, item,
                    property_location, category, amount, comments, receipt_link
                ]

            response = append_row(sheet_name, tab_name, row)
            if response is None or (hasattr(response, "status_code") and response.status_code == 200):
                st.success(f"{entry_type} entry submitted and saved to Google Sheets!")
            else:
                st.warning(f"Entry submitted but returned: {response}")
        except Exception as e:
            st.error(f"Failed to save entry: {e}")
