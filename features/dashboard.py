import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from utils.google_sheets import load_sheet_as_df
from io import StringIO

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def extract_first_valid_date(date_str):
    if not isinstance(date_str, str):
        return None
    date_str = date_str.replace("–", "-").replace("--", "-").strip()
    patterns = [
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{2}/\d{2}",
    ]
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            date = match.group(0)
            if len(date) == 5:
                date += f"/{pd.Timestamp.now().year}"
            return pd.to_datetime(date, errors='coerce')
    return None

def show_property_chart(property_name, income_df, expense_df, container, totals_list):
    income = income_df[income_df["Property"] == property_name].copy()
    expense = expense_df[expense_df["Property"] == property_name].copy()

    income_summary = income.groupby("Rental Month")["Income Amount"].sum().reindex(MONTH_ORDER).fillna(0)
    expense_summary = expense.groupby("Expense Month")["Expense Amount"].sum().reindex(MONTH_ORDER).fillna(0)
    profit = income_summary - expense_summary

    total_income = income_summary.sum()
    total_expense = expense_summary.sum()
    total_profit = total_income - total_expense

    # Save to list for export
    totals_list.append({
        "Property": property_name,
        "Total Income": total_income,
        "Total Expenses": total_expense,
        "Total Profit": total_profit
    })

    with container:
        # Chart
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(income_summary.index, income_summary.values, label="Income", color="skyblue")
        ax.bar(expense_summary.index, expense_summary.values, label="Expenses", color="lightcoral", alpha=0.7)
        ax.plot(profit.index, profit.values, label="Profit", color="green", marker="o", linewidth=2)

        ax.set_title(f"{property_name} – Monthly Income, Expenses & Profit")
        ax.set_ylabel("USD")
        ax.set_xlabel("Month")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Totals
        st.markdown(f"""
        **💼 Totals for {property_name}**
        - 💰 Income: **${total_income:,.2f}**
        - 💸 Expenses: **${total_expense:,.2f}**
        - 📈 Profit: **${total_profit:,.2f}**
        """)

def show():
    st.title("📊 Dashboard: Income, Expenses & Profit")

    selected_year = st.selectbox("Select Year", ["2025", "2026"], index=0)
    income_tab = f"{selected_year} OPP Income"
    expense_tab = f"{selected_year} OPP Expenses"

    try:
        income_df = load_sheet_as_df(income_tab)
        expense_df = load_sheet_as_df(expense_tab)

        if income_df.empty or expense_df.empty:
            st.warning("One or more sheets are empty.")
            return

        # Parse income
        if "Rental Dates" not in income_df.columns:
            st.error("Missing 'Rental Dates' in income sheet.")
            return
        income_df["Rental Start Date"] = income_df["Rental Dates"].apply(extract_first_valid_date)
        income_df = income_df.dropna(subset=["Rental Start Date"])
        income_df["Rental Month"] = income_df["Rental Start Date"].dt.strftime("%B")
        income_df["Rental Year"] = income_df["Rental Start Date"].dt.year
        income_df = income_df[income_df["Rental Year"] == int(selected_year)]
        income_df["Income Amount"] = pd.to_numeric(income_df["Income Amount"], errors="coerce")

        # Parse expenses
        if "Date" not in expense_df.columns:
            st.error("Missing 'Date' in expense sheet.")
            return
        expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors="coerce")
        expense_df = expense_df.dropna(subset=["Date"])
        expense_df["Expense Month"] = expense_df["Date"].dt.strftime("%B")
        expense_df["Expense Year"] = expense_df["Date"].dt.year
        expense_df = expense_df[expense_df["Expense Year"] == int(selected_year)]
        expense_df["Expense Amount"] = pd.to_numeric(expense_df["Amount"], errors="coerce")

        properties = sorted(set(income_df["Property"].dropna()) | set(expense_df["Property"].dropna()))
        totals_data = []

        for prop in properties:
            with st.expander(f"📍 {prop} Summary"):
                show_property_chart(prop, income_df, expense_df, st.container(), totals_data)

        # Convert totals to DataFrame
        totals_df = pd.DataFrame(totals_data)

        # CSV download
        if not totals_df.empty:
            st.markdown("---")
            st.subheader("📥 Download Totals Summary")
            csv = totals_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                file_name=f"{selected_year.lower()}_property_totals.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Failed to load dashboard: {e}")
