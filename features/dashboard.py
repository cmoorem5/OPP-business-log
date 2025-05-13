# features/dashboard.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📊 Dashboard Overview")

    # Load and rename
    income_df = (
        load_sheet_as_df("2025 OPP Income")
        .rename(columns={"Income Amount": "Income"})
    )
    expense_df = (
        load_sheet_as_df("2025 OPP Expenses")
        .rename(columns={"Amount": "Expense"})
    )

    # Coerce to numeric (remove any stray strings), fill NaNs with 0
    income_df["Income"] = pd.to_numeric(income_df["Income"], errors="coerce").fillna(0)
    expense_df["Expense"] = pd.to_numeric(expense_df["Expense"], errors="coerce").fillna(0)

    # Aggregate by Property & Month
    income_monthly = (
        income_df.groupby(["Property", "Month"], as_index=False)["Income"].sum()
    )
    expense_monthly = (
        expense_df.groupby(["Property", "Month"], as_index=False)["Expense"].sum()
    )

    # Merge & compute profit
    df = pd.merge(
        income_monthly,
        expense_monthly,
        on=["Property", "Month"],
        how="outer"
    ).fillna(0)
    df["Profit"] = df["Income"] - df["Expense"]

    # Ensure calendar ordering of months
    MONTHS = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    df["Month"] = pd.Categorical(df["Month"], categories=MONTHS, ordered=True)
    df = df.sort_values("Month")

    # Build the Plotly figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for prop in df["Property"].unique():
        prop_df = df[df["Property"] == prop]
        fig.add_trace(
            go.Bar(x=prop_df["Month"], y=prop_df["Income"], name=f"{prop} Income"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Bar(x=prop_df["Month"], y=prop_df["Expense"], name=f"{prop} Expense"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Line(x=prop_df["Month"], y=prop_df["Profit"], name=f"{prop} Profit"),
            secondary_y=True,
        )

    fig.update_layout(
        barmode="group",
        xaxis_title="Month",
        yaxis_title="Income / Expense ($)",
        legend_title="Property Metrics"
    )
    fig.update_yaxes(title_text="Profit ($)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

