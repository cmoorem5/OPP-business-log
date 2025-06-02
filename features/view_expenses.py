import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

from utils.google_sheets import load_sheet_as_df
from utils.config import SHEET_ID, PROPERTIES

def show():
    st.title("💸 View Monthly Expenses & Income")

    year = st.selectbox("Select Year", ["2025", "2026"], index=0)
    expense_sheet = f"{year} OPP Expenses"
    income_sheet = f"{year} OPP Income"

    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    try:
        df_exp = load_sheet_as_df(SHEET_ID, expense_sheet)
        df_inc = load_sheet_as_df(SHEET_ID, income_sheet)

        df_exp["Amount"] = pd.to_numeric(df_exp["Amount"], errors="coerce").fillna(0)
        df_exp["Month"] = df_exp["Month"].astype(str).str.strip()
        df_exp["Category"] = df_exp["Category"].astype(str).str.strip()
        df_exp["Property"] = df_exp["Property"].astype(str).str.strip()

        df_inc["Amount Received"] = pd.to_numeric(df_inc["Amount Received"], errors="coerce").fillna(0)
        df_inc["Income Source"] = df_inc["Income Source"].astype(str).str.strip()
        df_inc["Property"] = df_inc["Property"].astype(str).str.strip()

        for prop in PROPERTIES:
            st.header(f"🏠 {prop}")

            # --- Expenses Chart ---
            df_prop_exp = df_exp[df_exp["Property"] == prop]
            exp_summary = df_prop_exp.groupby(["Month", "Category"])["Amount"].sum().reset_index()
            pivot = exp_summary.pivot(index="Month", columns="Category", values="Amount").fillna(0)
            pivot = pivot.loc[[m for m in month_order if m in pivot.index]]

            st.markdown("#### 📊 Monthly Expenses by Category")
            if not pivot.empty:
                fig, ax = plt.subplots(figsize=(10, 4))
                pivot.plot(kind="bar", stacked=True, ax=ax)
                ax.set_ylabel("Amount ($)")
                ax.set_title(f"{prop} – Expenses by Category")
                ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
                ax.legend(title="Category", bbox_to_anchor=(1.05, 1), loc="upper left")
                st.pyplot(fig)
            else:
                st.info("No expense data for this property.")

            # --- Income Chart ---
            df_prop_inc = df_inc[df_inc["Property"] == prop]
            income_summary = (
                df_prop_inc.groupby("Income Source")["Amount Received"]
                .sum()
                .reset_index()
                .sort_values(by="Amount Received", ascending=False)
            )

            st.markdown("#### 💰 Income by Source")
            if not income_summary.empty:
                fig2, ax2 = plt.subplots()
                ax2.barh(income_summary["Income Source"], income_summary["Amount Received"], color="#4CAF50")
                ax2.set_xlabel("Amount ($)")
                ax2.set_title(f"{prop} – Income by Source")
                ax2.xaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
                st.pyplot(fig2)
                st.dataframe(income_summary, use_container_width=True)
            else:
                st.info("No income data for this property.")

            st.markdown("---")

    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
