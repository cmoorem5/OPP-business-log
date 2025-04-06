import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

# --- Helper Functions ---
@st.cache_data
def load_excel_data(sheet_name):
    file_path = "data/LLC Income and Expense Tracker.xlsx"
    return pd.read_excel(file_path, sheet_name=sheet_name)

def save_uploaded_file(uploaded_file, folder="receipts"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# --- Load Data ---
income_df = load_excel_data("2025 OPP Income")
expenses_df = load_excel_data("2025 OPP Expenses")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Log Entry", "View Entries", "Receipts", "Data Export"])

# --- Dashboard Page ---
if page == "Dashboard":
    st.title("Dashboard")
    total_income = income_df["Income Amount"].sum()
    total_expenses = expenses_df["Amount"].sum()
    net_profit = total_income - total_expenses

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${total_income:,.2f}")
    col2.metric("Total Expenses", f"${total_expenses:,.2f}")
    col3.metric("Net Profit", f"${net_profit:,.2f}")

    st.subheader("Monthly Income vs. Expenses")
    income_group = income_df.groupby("Month")["Income Amount"].sum()
    expense_group = expenses_df.groupby("Month")["Amount"].sum()
    months = sorted(set(income_df["Month"].dropna().unique()) | set(expenses_df["Month"].dropna().unique()))
    income_plot = [income_group.get(month, 0) for month in months]
    expense_plot = [expense_group.get(month, 0) for month in months]

    fig, ax = plt.subplots()
    ax.plot(months, income_plot, label="Income", marker="o")
    ax.plot(months, expense_plot, label="Expenses", marker="o")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.set_title("Monthly Income and Expenses")
    ax.legend()
    st.pyplot(fig)

elif page == "Log Entry":
    st.title("Log New Entry")
    entry_type = st.selectbox("Select Entry Type", ["Income", "Expense"])
    date = st.date_input("Date", datetime.date.today())
    amount = st.number_input("Amount", min_value=0.0, value=0.0, step=1.0)
    description = st.text_input("Description/Invoice")

    if entry_type == "Income":
        income_source = st.text_input("Income Source")
        rental_dates = st.text_input("Rental Dates (if applicable)")
    else:
        purchaser = st.text_input("Purchaser")
        item = st.text_input("Item Description")
        categories = expenses_df["Category"].dropna().unique() if "Category" in expenses_df.columns else ["General"]
        category = st.selectbox("Category", categories)
        comments = st.text_area("Comments")

    if st.button("Submit Entry"):
        if entry_type == "Income":
            new_entry = {
                "Month": date.strftime("%B"),
                "Rental Dates": rental_dates,
                "Income Source": income_source,
                "Description/Invoice No.": description,
                "Income Amount": amount,
                "Complete": "Pending"
            }
            income_df = income_df.append(new_entry, ignore_index=True)
            st.success("Income entry added!")
        else:
            new_entry = {
                "Month": date.strftime("%B"),
                "Purchase Date": date,
                "Purchaser": purchaser,
                "Item": item,
                "Category": category,
                "Amount": amount,
                "Comments": comments
            }
            expenses_df = expenses_df.append(new_entry, ignore_index=True)
            st.success("Expense entry added!")
        st.info("Note: For this demo, changes are stored in memory only.")

elif page == "View Entries":
    st.title("View Entries")
    view_option = st.radio("Select Data to View", ["Income", "Expenses"])
    st.dataframe(income_df if view_option == "Income" else expenses_df)

elif page == "Receipts":
    st.title("Receipts Upload")
    uploaded_file = st.file_uploader("Choose a receipt file", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        st.success(f"Receipt uploaded and saved at: {file_path}")

elif page == "Data Export":
    st.title("Data Export")
    csv_income = income_df.to_csv(index=False)
    csv_expenses = expenses_df.to_csv(index=False)
    st.download_button("Download Income Data", csv_income, "income_data.csv", "text/csv")
    st.download_button("Download Expense Data", csv_expenses, "expenses_data.csv", "text/csv")
