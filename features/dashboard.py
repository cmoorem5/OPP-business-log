import streamlit as st
import pandas as pd
from utils.google_sheets import get_worksheet
import plotly.graph_objects as go

def show():
    st.title("📊 Dashboard Overview")

    sheet_name   = "OPP Finance Tracker"
    income_ws    = get_worksheet(sheet_name, "2025 OPP Income")
    expense_ws   = get_worksheet(sheet_name, "2025 OPP Expenses")

    income_df    = pd.DataFrame(income_ws.get_all_records())
    expense_df   = pd.DataFrame(expense_ws.get_all_records())

    # --- PARSE RENTAL START MONTH (fallback to Month column) ---
    rental_col = next((c for c in income_df.columns if "rental" in c.lower()), None)
    if rental_col:
        starts = income_df[rental_col].astype(str).str.split(" - ").str[0]
        start_dates = pd.to_datetime(starts, errors="coerce")
        income_df["Month"] = (
            start_dates.dt.strftime("%B")
            .fillna(income_df.get("Month", "").str.strip().str.capitalize())
        )
    else:
        income_df["Month"] = income_df.get("Month", "").str.strip().str.capitalize()

    # --- CLEAN & PARSE FIELDS ---
    income_df["Income Amount"] = pd.to_numeric(income_df["Income Amount"], errors="coerce")
    income_df["Property"]      = income_df.get("Property", "").fillna("").replace("", "Unknown")

    expense_df["Amount"]       = pd.to_numeric(expense_df["Amount"], errors="coerce")
    expense_df["Property"]     = expense_df.get("Property", "").fillna("").replace("", "Unknown")
    expense_df["Month"]        = expense_df.get("Month", "").astype(str).str.strip().str.capitalize()

    # --- COMPUTE MONTHLY TOTALS ---
    monthly_income = (
        income_df
        .groupby(["Month", "Property"])["Income Amount"]
        .sum()
        .reset_index()
    )
    monthly_expense = (
        expense_df
        .groupby(["Month", "Property"])["Amount"]
        .sum()
        .reset_index()
    )

    # --- MERGE & CALCULATE PROFIT ---
    summary = pd.merge(
        monthly_income,
        monthly_expense,
        on=["Month", "Property"],
        how="outer"
    ).fillna(0)
    summary["Profit"] = summary["Income Amount"] - summary["Amount"]

    # --- SORT MONTHS IN CALENDAR ORDER ---
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    summary["Month"] = pd.Categorical(summary["Month"], categories=month_order, ordered=True)
    summary = summary.sort_values(by=["Month", "Property"])

    # --- PER-PROPERTY TOTAL METRICS ---
    props = summary["Property"].unique()
    cols = st.columns(len(props))
    for col, prop in zip(cols, props):
        total_inc  = income_df.loc[income_df["Property"] == prop, "Income Amount"].sum()
        total_exp  = expense_df.loc[expense_df["Property"] == prop, "Amount"].sum()
        total_prof = total_inc - total_exp
        with col:
            st.subheader(f"{prop} Totals")
            st.metric("Income",   f"${total_inc:,.2f}")
            st.metric("Expenses", f"${total_exp:,.2f}")
            st.metric("Profit",   f"${total_prof:,.2f}")

    # --- PLOT PER PROPERTY ---
    for prop in summary["Property"].unique():
        prop_df = summary[summary["Property"] == prop]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=prop_df["Month"], y=prop_df["Income Amount"], name="Income"))
        fig.add_trace(go.Bar(x=prop_df["Month"], y=prop_df["Amount"], name="Expenses"))
        fig.add_trace(
            go.Scatter(
                x=prop_df["Month"],
                y=prop_df["Profit"],
                name="Profit",
                mode="lines+markers"
            )
        )
        fig.update_layout(
            title=f"{prop} – Monthly Summary",
            barmode="group",
            xaxis_title="Month",
            yaxis_title="Amount ($)"
        )
        st.plotly_chart(fig, use_container_width=True)
