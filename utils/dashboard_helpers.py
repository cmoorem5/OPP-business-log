import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from utils.google_sheets import load_sheet_as_df

def load_dashboard_data():
    current_year = str(datetime.now().year)
    income_sheet = f"{current_year} OPP Income"
    expense_sheet = f"{current_year} OPP Expenses"

    df_income = load_sheet_as_df(income_sheet)
    df_income["Amount Owed"] = pd.to_numeric(df_income["Amount Owed"], errors="coerce").fillna(0)
    df_income["Amount Received"] = pd.to_numeric(df_income["Amount Received"], errors="coerce").fillna(0)
    df_income["Month"] = df_income["Month"].str.strip()
    df_income = df_income.dropna(subset=["Month", "Property"])

    df_expense = load_sheet_as_df(expense_sheet)
    df_expense["Amount"] = pd.to_numeric(df_expense["Amount"], errors="coerce").fillna(0)
    df_expense["Month"] = df_expense["Month"].str.strip()
    df_expense = df_expense.dropna(subset=["Month", "Property"])

    return df_income, df_expense

def build_financial_summary(df_income, df_expense):
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    income_grouped = df_income.groupby(["Property", "Month"]).agg({
        "Amount Received": "sum",
        "Amount Owed": "sum"
    }).reset_index()

    expense_grouped = df_expense.groupby(["Property", "Month"])["Amount"].sum().reset_index()

    summary = pd.merge(income_grouped, expense_grouped, how="outer", on=["Property", "Month"])
    summary["Amount Received"] = summary["Amount Received"].fillna(0)
    summary["Amount Owed"] = summary["Amount Owed"].fillna(0)
    summary["Amount"] = summary["Amount"].fillna(0)
    summary["Profit"] = summary["Amount Received"] - summary["Amount"]
    summary["Due"] = summary["Amount Owed"] - summary["Amount Received"]
    summary["Month Num"] = summary["Month"].map(month_order)

    return summary.sort_values(["Property", "Month Num"])

def render_property_charts(summary):
    properties = sorted(summary["Property"].dropna().unique())

    for prop in properties:
        prop_data = summary[summary["Property"] == prop].copy()
        available_months = list(prop_data["Month"].unique())
        selected_months = st.multiselect(
            f"📅 Filter months for {prop}", options=available_months, default=available_months
        )
        filtered_data = prop_data[prop_data["Month"].isin(selected_months)]

        # Totals
        total_income = filtered_data["Amount Received"].sum()
        total_expense = filtered_data["Amount"].sum()
        total_due = filtered_data["Due"].sum()
        total_profit = total_income - total_expense

        st.markdown(f"### 🏡 {prop}")
        st.markdown(f"""
        **Total Income Received:** ${total_income:,.2f}  
        **Total Income Due:** ${total_due:,.2f}  
        **Total Expenses:** ${total_expense:,.2f}  
        **Total Profit:** ${total_profit:,.2f}
        """)

        # Alerts
        overdue_rows = filtered_data[filtered_data["Due"] > 0]
        if not overdue_rows.empty:
            with st.expander("🔴 Overdue Bookings", expanded=True):
                st.error(f"{len(overdue_rows)} month(s) with outstanding balances.")
                for _, row in overdue_rows.iterrows():
                    st.markdown(
                        f"- **{row['Month']}** — ${row['Due']:.2f} due on ${row['Amount Owed']:.2f} owed"
                    )

        # Chart: side-by-side income/expense bars + profit line
        fig, ax = plt.subplots()
        bar_width = 0.35
        x = range(len(filtered_data))

        ax.bar(x, filtered_data["Amount Received"], width=bar_width, label="Income", color="#4CAF50")
        ax.bar([i + bar_width for i in x], filtered_data["Amount"], width=bar_width, label="Expenses", color="#F44336")

        ax.plot(
            [i + bar_width / 2 for i in x],
            filtered_data["Profit"],
            label="Profit",
            color="#2196F3",
            marker="o",
            linewidth=2
        )

        ax.set_xticks([i + bar_width / 2 for i in x])
        ax.set_xticklabels(filtered_data["Month"], rotation=45)
        ax.set_ylabel("Amount ($)")
        ax.set_title(f"{prop} – Monthly Financials")
        ax.legend()
        st.pyplot(fig)
        st.markdown("---")
