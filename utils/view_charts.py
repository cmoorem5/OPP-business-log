import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_summary_charts(filtered, view_type, date_col):
    with st.expander("📊 Summary Charts", expanded=False):
        if "Amount" not in filtered.columns:
            st.warning("No 'Amount' column found in data.")
            return

        # Clean and parse Amount field
        filtered["Amount (raw)"] = (
            filtered["Amount"]
            .astype(str)
            .str.replace(r"[^\d\.\-]", "", regex=True)
            .str.strip()
            .replace({"": pd.NA, "-": pd.NA})
            .astype(float)
        )

        # Debug output
        st.write("Amount (raw) column preview:", filtered["Amount (raw)"].head(5))
        st.write("Parsed count:", filtered["Amount (raw)"].notna().sum())

        if filtered["Amount (raw)"].dropna().empty:
            st.warning("⚠️ No valid numeric data available to display charts.")
            return

        # Month parsing
        if view_type == "Income":
            if "Check-in" not in filtered.columns:
                st.warning("⚠️ 'Check-in' column not found.")
                return
            filtered["Month"] = pd.to_datetime(filtered["Check-in"], errors="coerce").dt.strftime("%B")
        else:
            filtered["Month"] = pd.to_datetime(filtered[date_col], errors="coerce").dt.strftime("%B")

        filtered["Month"] = pd.Categorical(
            filtered["Month"],
            categories=[
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ],
            ordered=True
        )

        # --- Monthly Totals ---
        month_totals = (
            filtered.groupby("Month")["Amount (raw)"]
            .sum()
            .dropna()
        )
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        ax1.bar(month_totals.index, month_totals.values)
        ax1.set_title("Total by Month")
        ax1.set_ylabel("Amount ($)")
        for i, v in enumerate(month_totals.values):
            ax1.text(i, v, f"${v:,.0f}", ha='center', va='bottom', fontsize=8)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig1)
