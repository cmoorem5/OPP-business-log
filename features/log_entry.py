import streamlit as st
from datetime import date
from utils.data_loader import load_excel_data
from utils.google_sheets import append_row

def show():
    st.markdown("## 📝 Log New Entry")

    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])
    entry_date = st.date_input("Date", date.today())
    amount = st.number_input("Amount", min_value=0.0, value=0.0, step=1.0)
    description = st.text_input("Description")

    if entry_type == "Income":
        source = st.text_input("Income Source")
        rental_dates = st.date_input("Rental Date Range", value=(date.today(), date.today()))

        st.markdown("### 👤 Renter Details")
        renter_name = st.text_input("Renter Name")
        renter_email = st.text_input("Email Address")
        renter_location = st.text_input("Where are they from?")
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

    if st.button("Submit Entry"):
        try:
            json_key_path = "opp-rental-tracker-f7fe7e5ad486.json"
            sheet_name = "OPP Finance Tracker"

            if entry_type == "Income":
                tab_name = "2025 OPP Income"
                row = [
                    str(entry_date), amount, description, source,
                    str(rental_dates[0]), str(rental_dates[1]),
                    renter_name, renter_email, renter_location
                ]
            else:
                tab_name = "2025 OPP Expenses"
                month = entry_date.strftime("%B")
                row = [
                    month, str(entry_date), purchaser, item,
                    property_location, category, amount, comments
                ]

            append_row(json_key_path, sheet_name, tab_name, row)
            st.success(f"{entry_type} entry submitted and saved to Google Sheets!")
        except Exception as e:
            st.error(f"Failed to save entry: {e}")
