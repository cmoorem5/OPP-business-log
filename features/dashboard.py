import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📊 Dashboard Overview")

    sheet = "OPP Finance Tracker"
    # Load raw data
    income_df  = load_sheet_as_df(sheet, "2025 OPP Income").rename(columns={"Income Amount": "Income"})
    expense_df = load_sheet_as_df(sheet, "2025 OPP Expenses").rename(columns={"Amount": "Expense"})

    # ── AGGREGATE MONTHLY DATA ───────────────────────────────────────────────────
    # Sum Income and Expense per Property & Month to avoid Cartesian duplication
    income_monthly = (
        income_df
        .groupby(["Property", "Month"], as_index=False)["Income"]
        .sum()
    )
    expense_monthly = (
        expense_df
        .groupby(["Property", "Month"], as_index=False)["Expense"]
        .sum()
    )
    df = pd.merge(
        income_monthly,
        expense_monthly,
        on=["Property", "Month"],
        how="outer"
    ).fillna(0)
    df["Profit"] = df["Income"] - df["Expense"]

    # Ensure correct month order
    MONTHS = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    df["Month"] = pd.Categorical(df["Month"], categories=MONTHS, ordered=True)
    df = df.sort_values(["Property", "Month"])

    # ── TOTALS SUMMARY ───────────────────────────────────────────────────────────
    st.subheader("🏠 Totals by Property")
    totals = df.groupby("Property", as_index=False).agg({
        "Income": "sum",
        "Expense": "sum",
        "Profit": "sum"
    })
    totals = totals.rename(columns={
        "Income": "Total Income",
        "Expense": "Total Expense",
        "Profit": "Total Profit"
    })
    # Format as currency
    for col in ["Total Income", "Total Expense", "Total Profit"]:
        totals[col] = totals[col].apply(lambda x: f"${x:,.2f}")
    st.dataframe(totals, use_container_width=True)

    # ── PLOTS PER PROPERTY ───────────────────────────────────────────────────────
    for prop in df["Property"].unique():
        prop_df = df[df["Property"] == prop]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=prop_df["Month"],
            y=prop_df["Income"],
            name="Income"
        ))
        fig.add_trace(go.Bar(
            x=prop_df["Month"],
            y=prop_df["Expense"],
            name="Expense"
        ))
        fig.add_trace(go.Scatter(
            x=prop_df["Month"],
            y=prop_df["Profit"],
            name="Profit",
            mode="lines+markers"
        ))

        fig.update_layout(
            title=f"{prop} – Monthly Summary",
            barmode="group",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            legend_title="Metric",
            xaxis=dict(
                categoryorder="array",
                categoryarray=MONTHS
            )
        )
        st.plotly_chart(fig, use_container_width=True)
