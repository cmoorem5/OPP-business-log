import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def show_summary_charts(filtered, view_type, date_col):
    with st.expander("📊 Summary Charts", expanded=False):
        if "Amount" in filtered.columns:
            filtered["Amount (raw)"] = filtered["Amount"].replace('[\$,]', '', regex=True).astype(float)

            if view_type == "Income":
                month_key = "Rental Month"
            else:
                filtered["Month"] = pd.Categorical(
                    filtered[date_col].dt.strftime("%B"),
                    categories=[
                        "January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"
                    ],
                    ordered=True
                )
                month_key = "Month"

            month_totals = (
                filtered.groupby(month_key)["Amount (raw)"]
                .sum()
                .reindex([
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ])
                .dropna()
            )
            fig1, ax1 = plt.subplots()
            ax1.bar(month_totals.index, month_totals.values)
            ax1.set_title("Total by Month")
            ax1.set_ylabel("Amount ($)")
            for i, v in enumerate(month_totals.values):
                ax1.text(i, v, f"${v:,.0f}", ha='center', va='bottom')
            st.pyplot(fig1)

            prop_totals = (
                filtered.groupby("Property")["Amount (raw)"]
                .sum()
                .sort_values(ascending=False)
            )
            fig2, ax2 = plt.subplots()
            ax2.bar(prop_totals.index, prop_totals.values)
            ax2.set_title("Total by Property")
            ax2.set_ylabel("Amount ($)")
            for i, v in enumerate(prop_totals.values):
                ax2.text(i, v, f"${v:,.0f}", ha='center', va='bottom')
            st.pyplot(fig2)

            if "Category" in filtered.columns:
                cat_totals = (
                    filtered.groupby("Category")["Amount (raw)"]
                    .sum()
                    .sort_values(ascending=False)
                )
                fig3, ax3 = plt.subplots()
                ax3.pie(
                    cat_totals.values,
                    labels=cat_totals.index,
                    autopct=lambda p: f"${p * cat_totals.sum() / 100:,.0f}",
                    startangle=90
                )
                ax3.set_title("Category Breakdown")
                ax3.axis("equal")
                st.pyplot(fig3)
