import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd


def show_summary_charts(df: pd.DataFrame, view_type: str, date_col: str):
    st.markdown("## 📊 Summary Charts")

    if df.empty or "Amount" not in df.columns:
        st.warning("⚠️ No valid numeric data available to display charts.")
        return

    try:
        df["Amount (raw)"] = pd.to_numeric(df["Amount"].astype(str).str.replace(r"[\$,]", "", regex=True), errors="coerce")
        parsed_count = df["Amount (raw)"].notna().sum()
        st.caption(f"Amount (raw) column preview:\n\nParsed count: {parsed_count}")
    except Exception as e:
        st.error(f"❌ Failed to parse amount: {e}")
        return

    if parsed_count == 0:
        st.warning("⚠️ No valid numeric data available to display charts.")
        return

    # Monthly chart
    if "Rental Month" in df.columns:
        month_chart = df.groupby("Rental Month")["Amount (raw)"].sum()
    elif "Date" in df.columns:
        df["Month"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%B")
        month_chart = df.groupby("Month")["Amount (raw)"].sum()
    else:
        st.warning("⚠️ No valid month or date data for charting.")
        return

    if month_chart.empty:
        st.warning("⚠️ No data available to chart.")
        return

    fig, ax = plt.subplots()
    month_chart.plot(kind="bar", ax=ax, color="#4CAF50")
    ax.set_title("Total Amount by Month")
    ax.set_ylabel("Amount ($)")
    ax.set_xlabel("Month")
    st.pyplot(fig)

    # Category chart
    category_col = "Income Source" if view_type == "Income" else "Category"
    if category_col in df.columns:
        cat_chart = df.groupby(category_col)["Amount (raw)"].sum().sort_values(ascending=False)
        fig2, ax2 = plt.subplots()
        cat_chart.plot(kind="bar", ax=ax2, color="#2196F3")
        ax2.set_title(f"Total Amount by {category_col}")
        ax2.set_ylabel("Amount ($)")
        ax2.set_xlabel(category_col)
        st.pyplot(fig2)
