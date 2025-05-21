import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
from utils.google_sheets import load_sheet_as_df


def extract_start_date(date_range_str):
    if not isinstance(date_range_str, str):
        return None
    date_range_str = date_range_str.replace("–", "-").replace("--", "-").strip()
    patterns = [
        r"\d{4}-\d{2}-\d{2}", r"\d{2}/\d{2}/\d{4}", r"\d{2}-\d{2}-\d{4}", r"\d{2}/\d{2}"
    ]
    for pattern in patterns:
        match = re.search(pattern, date_range_str)
        if match:
            date = match.group(0)
            if len(date) == 5:
                date += f"/{pd.Timestamp.now().year}"
            return pd.to_datetime(date, errors='coerce')
    return None


def show():
    st.title("📊 Dashboard (2025 Overview)")

    try:
        income_df = load_sheet_as_df("2025 OPP Income")
        expense_df = load_sheet_as_df("2025 OPP Expenses")

        # Clean Income Data
        income_df["Income Amount"] = pd.to_numeric(income_df["Income Amount"], errors="coerce")
        income_df = income_df.dropna(subset=["Income Amount"])
        income_df["Rental Start Date"] = income_df["Rental Dates"].apply(extract_start_date)
        income_df = income_df.dropna(subset=["Rental Start Date"])
        income_df["Month"] = income_df["Rental Start Date"].dt.strftime("%B")
        income_df["Property"] = income_df["Property"].fillna("Unknown").str.strip()

        # Clean Expense Data
        expense_df["Amount"] = pd.to_numeric(expense_df["Amount"], errors="coerce")
        expense_df = expense_df.dropna(subset=["Amount"])
        expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors="coerce")
        expense_df = expense_df.dropna(subset=["Date"])
        expense_df["Month"] = expense_df["Date"].dt.strftime("%B")
        expense_df["Property"] = expense_df["Property"].fillna("Unknown").str.strip()

        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # Show what properties and months were detected
        st.markdown("### 🛠️ Debug Info")
        st.markdown(f"**Detected Income Properties:** {sorted(income_df['Property'].unique().tolist())}")
        st.markdown(f"**Detected Expense Properties:** {sorted(expense_df['Property'].unique().tolist())}")

        properties = sorted(set(income_df["Property"]).union(set(expense_df["Property"])))

        for prop in properties:
            st.subheader(f"🏠 {prop} Summary")
            inc = income_df[income_df["Property"] == prop]
            exp = expense_df[expense_df["Property"] == prop]

            income_summary = inc.groupby("Month")["Income Amount"].sum().reindex(month_order, fill_value=0)
            expense_summary = exp.groupby("Month")["Amount"].sum().reindex(month_order, fill_value=0)
            profit_summary = income_summary - expense_summary

            # Show debug output for grouped values
            with st.expander(f"🔍 Debug Data for {prop}"):
                st.write("Income Summary:")
                st.write(income_summary)
                st.write("Expense Summary:")
                st.write(expense_summary)
                st.write("Profit Summary:")
                st.write(profit_summary)

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(income_summary.index, income_summary.values, label="Income", alpha=0.7)
            ax.bar(expense_summary.index, expense_summary.values, label="Expenses", alpha=0.7)
            ax.plot(profit_summary.index, profit_summary.values, label="Profit", color="green", linewidth=2)
            ax.set_title(f"{prop} – Monthly Overview")
            ax.set_ylabel("USD")
            ax.legend()
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

            st.markdown(f"**YTD Income:** ${income_summary.sum():,.2f}  ")
            st.markdown(f"**YTD Expenses:** ${expense_summary.sum():,.2f}  ")
            st.markdown(f"**YTD Profit:** ${profit_summary.sum():,.2f}")

        with st.expander("📄 View Cleaned Income/Expense Data"):
            show_data = st.checkbox("Show raw tables", key="show_raw_data")
            if show_data:
                st.markdown("### Income Data")
                st.dataframe(income_df, use_container_width=True)
                st.markdown("### Expense Data")
                st.dataframe(expense_df, use_container_width=True)

    except Exception as e:
        st.error(f"Dashboard failed to load: {e}")
