import streamlit as st
import plotly.express as px
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📊 Dashboard Overview")

    sheet = "OPP Finance Tracker"
    income_df  = load_sheet_as_df(sheet, "2025 OPP Income")
    expense_df = load_sheet_as_df(sheet, "2025 OPP Expenses")

    # Standardize column names
    income_df = income_df.rename(columns={"Income Amount": "Income"})
    expense_df = expense_df.rename(columns={"Amount": "Expense"})
    # Merge on Month & Property
    df = income_df.merge(
        expense_df,
        on=["Month", "Property"],
        how="outer",
        suffixes=("_inc", "_exp")
    )
    df["Income"] = df["Income"].fillna(0)
    df["Expense"] = df["Expense"].fillna(0)
    df["Profit"] = df["Income"] - df["Expense"]

    # Melt for plotting
    df_melt = df.melt(
        id_vars=["Month", "Property"],
        value_vars=["Income", "Expense", "Profit"],
        var_name="Metric",
        value_name="Amount"
    )

    fig = px.bar(
        df_melt,
        x="Month",
        y="Amount",
        color="Metric",
        facet_col="Property",
        barmode="group",
        title="Monthly Income, Expense, and Profit by Property",
        category_orders={"Month": [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]},
    )
    st.plotly_chart(fig, use_container_width=True)
