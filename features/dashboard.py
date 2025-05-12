import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from utils.google_sheets import load_sheet_as_df

def show():
    """Dashboard Overview: Monthly income, expense, and profit by property."""
    st.title("📊 Dashboard Overview")

    sheet_name = "OPP Finance Tracker"
    # ─── Load data with a spinner ─────────────────────────────────────────────
    with st.spinner("Fetching income and expense data..."):
        income_df = (
            load_sheet_as_df(sheet_name, "2025 OPP Income")
            .rename(columns={"Income Amount": "Income"})
        )
        expense_df = (
            load_sheet_as_df(sheet_name, "2025 OPP Expenses")
            .rename(columns={"Amount": "Expense"})
        )

    # ─── Aggregate & clean ─────────────────────────────────────────────────
    income_monthly = (
        income_df.groupby(["Property", "Month"], as_index=False)["Income"].sum()
    )
    expense_monthly = (
        expense_df.groupby(["Property", "Month"], as_index=False)["Expense"].sum()
    )

    df = pd.merge(
        income_monthly, expense_monthly,
        on=["Property", "Month"], how="outer"
    ).fillna(0)

    # Coerce to numeric and compute Profit
    df["Income"]  = pd.to_numeric(df["Income"], errors="coerce").fillna(0)
    df["Expense"] = pd.to_numeric(df["Expense"], errors="coerce").fillna(0)
    df["Profit"]  = df["Income"] - df["Expense"]

    # Ensure months sort correctly
    MONTHS = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    df["Month"] = pd.Categorical(df["Month"], categories=MONTHS, ordered=True)

    # ─── Totals summary ────────────────────────────────────────────────────
    st.subheader("🏠 Totals by Property")
    totals = (
        df.groupby("Property", as_index=False)
          .agg({"Income": "sum", "Expense": "sum", "Profit": "sum"})
          .rename(columns={
              "Income": "Total Income",
              "Expense": "Total Expense",
              "Profit": "Total Profit"
          })
    )
    for col in ["Total Income", "Total Expense", "Total Profit"]:
        totals[col] = totals[col].apply(lambda x: f"${x:,.2f}")
    st.dataframe(totals, use_container_width=True)

    # ─── Build and render plot ─────────────────────────────────────────────
    with st.spinner("Rendering chart..."):
        properties = df["Property"].unique()
        cols = len(properties)
        fig = make_subplots(
            rows=1, cols=cols,
            subplot_titles=list(properties),
            shared_yaxes=True
        )

        for i, prop in enumerate(properties, start=1):
            prop_df = df[df["Property"] == prop].sort_values("Month")

            fig.add_trace(
                go.Bar(x=prop_df["Month"], y=prop_df["Income"], name="Income"),
                row=1, col=i
            )
            fig.add_trace(
                go.Bar(x=prop_df["Month"], y=prop_df["Expense"], name="Expense"),
                row=1, col=i
            )
            fig.add_trace(
                go.Scatter(
                    x=prop_df["Month"],
                    y=prop_df["Profit"],
                    name="Profit",
                    mode="lines+markers"
                ),
                row=1, col=i
            )
            fig.update_xaxes(
                categoryorder="array",
                categoryarray=MONTHS,
                row=1, col=i
            )

        fig.update_layout(
            title="Monthly Income, Expense, and Profit by Property",
            barmode="group",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            legend_title="Metric",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    # ─── Custom footer ─────────────────────────────────────────────────────
    st.markdown("---")
    last_updated = datetime.now().strftime("%B %d, %Y %I:%M %p")
    footer_md = f"""
    <div style="text-align:center; font-size:0.85em; color:gray;">
      Oceanview Property Partners • v1.3.0 • Last updated: {last_updated}
    </div>
    """
    st.markdown(footer_md, unsafe_allow_html=True)
