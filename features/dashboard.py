import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📊 Finance Dashboard")

    # --- Year Selection ---
    years = st.secrets["years"]
    current_year = datetime.now().year
    default_index = years.index(str(current_year)) if str(current_year) in years else 0
    selected_year = st.selectbox("Select Year", years, index=default_index)

    sheet_id = st.secrets["gsheet_id"]
    income_tab = f"{selected_year} OPP Income"
    expense_tab = f"{selected_year} OPP Expenses"

    df_income = load_sheet_as_df(sheet_id, income_tab)
    df_expense = load_sheet_as_df(sheet_id, expense_tab)

    if df_income.empty or df_expense.empty:
        st.warning("One or more data sheets are empty.")
        return

    # --- Check required columns ---
    required_income_cols = {"Amount Received", "Check-in", "Property"}
    required_expense_cols = {"Amount", "Date", "Property"}

    if not required_income_cols.issubset(df_income.columns):
        st.error(f"Missing columns in income sheet: {required_income_cols - set(df_income.columns)}")
        return
    if not required_expense_cols.issubset(df_expense.columns):
        st.error(f"Missing columns in expense sheet: {required_expense_cols - set(df_expense.columns)}")
        return

    # --- Preprocessing ---
    def to_amount(col):
        return pd.to_numeric(col.replace('[\$,]', '', regex=True), errors="coerce")

    df_income["Amount Received"] = to_amount(df_income["Amount Received"])
    df_expense["Amount"] = to_amount(df_expense["Amount"])

    df_income["Month"] = pd.to_datetime(df_income["Check-in"], errors="coerce").dt.strftime("%B")
    df_expense["Month"] = pd.to_datetime(df_expense["Date"], errors="coerce").dt.strftime("%B")

    df_income = df_income.dropna(subset=["Amount Received", "Month", "Property"])
    df_expense = df_expense.dropna(subset=["Amount", "Month", "Property"])

    # --- Grouping ---
    def summarize(df, value_col, label):
        return (
            df.groupby(["Property", "Month"])[value_col]
            .sum()
            .reset_index()
            .rename(columns={value_col: label})
        )

    income_summary = summarize(df_income, "Amount Received", "Income")
    expense_summary = summarize(df_expense, "Amount", "Expenses")

    # --- Merge ---
    merged = pd.merge(income_summary, expense_summary, how="outer", on=["Property", "Month"]).fillna(0)
    merged["Profit"] = merged["Income"] - merged["Expenses"]

    # --- CSV Download ---
    csv = merged.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Summary CSV", data=csv, file_name=f"{selected_year}_summary.csv", mime="text/csv")

    # --- Per Property Charts ---
    months_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    properties = merged["Property"].unique()
    for prop in properties:
        with st.expander(f"📈 {prop}"):
            prop_data = merged[merged["Property"] == prop].copy()
            prop_data["Month"] = pd.Categorical(prop_data["Month"], categories=months_order, ordered=True)
            prop_data = prop_data.sort_values("Month")

            fig, ax = plt.subplots()
            ax.bar(prop_data["Month"], prop_data["Income"], label="Income")
            ax.bar(prop_data["Month"], prop_data["Expenses"], bottom=0, label="Expenses")
            ax.plot(prop_data["Month"], prop_data["Profit"], color="green", marker="o", label="Profit")

            ax.set_title(f"{prop} - Monthly Finance Overview")
            ax.set_ylabel("Amount ($)")
            ax.legend()
            st.pyplot(fig)
