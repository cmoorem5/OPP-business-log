import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_summary_charts(filtered: pd.DataFrame, view_type: str, date_col: str):
    with st.expander("📊 Summary Charts", expanded=False):
        amount_col = "Amount Received" if view_type == "Income" else "Amount"
        if amount_col not in filtered.columns:
            st.error(f"❌ '{amount_col}' column not found.")
            return

        # Convert to numeric
        filtered["Amount (raw)"] = pd.to_numeric(
            filtered[amount_col]
            .astype(str)
            .str.replace(r"[^\d\.\-]", "", regex=True)
            .str.strip(),
            errors="coerce"
        )

        if filtered["Amount (raw)"].dropna().empty:
            st.warning("⚠️ No valid numeric data available to display charts.")
            return

        # Month extraction
        filtered["Month"] = pd.to_datetime(filtered[date_col], errors="coerce").dt.strftime("%B")
        filtered["Month"] = pd.Categorical(
            filtered["Month"],
            categories=[
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ],
            ordered=True
        )

        # Monthly totals
        monthly_totals = (
            filtered.groupby("Month")["Amount (raw)"]
            .sum()
            .dropna()
        )

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(monthly_totals.index, monthly_totals.values)
        ax.set_title("Total by Month")
        ax.set_ylabel("Amount ($)")
        for i, v in enumerate(monthly_totals.values):
            ax.text(i, v, f"${v:,.0f}", ha='center', va='bottom', fontsize=8)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
