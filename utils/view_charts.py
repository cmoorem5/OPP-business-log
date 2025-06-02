import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def show_summary_charts(filtered, view_type, date_col):
    with st.expander("📊 Summary Charts", expanded=False):
        if "Amount" not in filtered.columns:
            st.warning("No 'Amount' column found in data.")
            return

        filtered["Amount (raw)"] = pd.to_numeric(
            filtered["Amount"].replace(r'[\$,]', '', regex=True),
            errors="coerce"
        )

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

        # --- Property Totals ---
        if "Property" in filtered.columns:
            prop_totals = (
                filtered.groupby("Property")["Amount (raw)"]
                .sum()
                .sort_values(ascending=False)
            )
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            ax2.bar(prop_totals.index, prop_totals.values)
            ax2.set_title("Total by Property")
            ax2.set_ylabel("Amount ($)")
            for i, v in enumerate(prop_totals.values):
                ax2.text(i, v, f"${v:,.0f}", ha='center', va='bottom', fontsize=8)
            plt.xticks(rotation=30)
            plt.tight_layout()
            st.pyplot(fig2)

        # --- Category Pie Chart ---
        if "Category" in filtered.columns:
            cat_totals = (
                filtered.groupby("Category")["Amount (raw)"]
                .sum()
                .sort_values(ascending=False)
            )
            if len(cat_totals) > 6:
                top = cat_totals[:6]
                other_sum = cat_totals[6:].sum()
                cat_totals = pd.concat([top, pd.Series({"Other": other_sum})])

            fig3, ax3 = plt.subplots()
            wedges, texts, autotexts = ax3.pie(
                cat_totals.values,
                labels=cat_totals.index,
                autopct=lambda p: f"${p * cat_totals.sum() / 100:,.0f}",
                startangle=90,
                wedgeprops=dict(width=0.4, edgecolor='w')
            )
            for text in texts + autotexts:
                text.set_fontsize(8)
            ax3.set_title("Category Breakdown")
            ax3.axis("equal")
            plt.tight_layout()
            st.pyplot(fig3)

