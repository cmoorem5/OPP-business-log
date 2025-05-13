import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.google_sheets import load_sheet_as_df


def show():
    st.title("📊 Dashboard Overview")

    # Load and aggregate data
    income_df = (
        load_sheet_as_df("2025 OPP Income")
        .rename(columns={"Income Amount": "Income"})
    )
    expense_df = (
        load_sheet_as_df("2025 OPP Expenses")
        .rename(columns={"Amount": "Expense"})
    )

    # Coerce to numeric
    income_df["Income"] = pd.to_numeric(income_df["Income"], errors="coerce").fillna(0)
    expense_df["Expense"] = pd.to_numeric(expense_df["Expense"], errors="coerce").fillna(0)

    # Monthly aggregation
    income_monthly = (
        income_df.groupby(["Property", "Month"], as_index=False)["Income"].sum()
    )
    expense_monthly = (
        expense_df.groupby(["Property", "Month"], as_index=False)["Expense"].sum()
    )

    # Merge and compute profit
    df = (
        pd.merge(
            income_monthly,
            expense_monthly,
            on=["Property", "Month"],
            how="outer"
        )
        .fillna(0)
    )
    df["Profit"] = df["Income"] - df["Expense"]

    # Define full month order
    MONTHS = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Create a full months DataFrame for reindexing
    month_df = pd.DataFrame({"Month": MONTHS})

    # Time-series bar/line plot with all months
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for prop in df["Property"].unique():
        prop_data = df[df["Property"] == prop][["Month", "Income", "Expense", "Profit"]]
        prop_df = month_df.merge(prop_data, on="Month", how="left").fillna(0)

        fig.add_trace(
            go.Bar(
                x=prop_df["Month"],
                y=prop_df["Income"],
                name=f"{prop} Income"
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Bar(
                x=prop_df["Month"],
                y=prop_df["Expense"],
                name=f"{prop} Expense"
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Line(
                x=prop_df["Month"],
                y=prop_df["Profit"],
                name=f"{prop} Profit"
            ),
            secondary_y=True,
        )

    # Ensure x-axis shows all months in correct order
    fig.update_xaxes(
        type='category',
        categoryorder='array',
        categoryarray=MONTHS
    )

    fig.update_layout(
        barmode="group",
        xaxis_title="Month",
        yaxis_title="Income / Expense ($)",
        legend_title="Metrics",
        title_text="Monthly Income, Expense, and Profit"
    )
    fig.update_yaxes(title_text="Profit ($)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    # Pie charts per property totals
    st.markdown("---")
    st.markdown("## Totals by Property (Income vs Expense)")
    totals = df.groupby("Property")[['Income', 'Expense']].sum().reset_index()
    for _, row in totals.iterrows():
        prop = row['Property']
        inc = row['Income']
        exp = row['Expense']
        st.subheader(prop)
        pie = go.Figure(
            go.Pie(
                labels=["Income", "Expense"],
                values=[inc, exp],
                hole=0.4
            )
        )
        pie.update_layout(
            title_text=f"${inc:,.2f} Income vs ${exp:,.2f} Expense"
        )
        st.plotly_chart(pie, use_container_width=True)
