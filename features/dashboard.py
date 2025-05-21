import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df
from features.recurring import inject_recurring_expenses
import re
import matplotlib.pyplot as plt
import seaborn as sns


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[:, df.columns.str.strip() != ""]
    counts, new_cols = {}, []
    for col in df.columns:
        counts[col] = counts.get(col, 0)
        new_cols.append(col if counts[col] == 0 else f"{col}_{counts[col]}")
        counts[col] += 1
    df.columns = new_cols
    return df


def extract_first_valid_date(date_str):
    if not isinstance(date_str, str):
        return None
    date_str = date_str.replace("–", "-").replace("--", "-").strip()
    patterns = [r"\d{4}-\d{2}-\d{2}", r"\d{2}/\d{2}/\d{4}", r"\d{2}-\d{2}-\d{4}", r"\d{2}/\d{2}"]
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            date = match.group(0)
            if len(date) == 5:
                date += f"/{pd.Timestamp.now().year}"
            return pd.to_datetime(date, errors='coerce')
    return None


def show():
    st.title("📊 Dashboard")

    year = st.radio("Select Year", ["2025", "2026"], horizontal=True)
    income_df = _clean_df(load_sheet_as_df(f"{year} OPP Income"))
    expense_df = _clean_df(load_sheet_as_df(f"{year} OPP Expenses"))

    income_df["Rental Start Date"] = income_df["Rental Dates"].apply(extract_first_valid_date)
    income_df = income_df.dropna(subset=["Rental Start Date"])
    income_df["Month"] = income_df["Rental Start Date"].dt.strftime("%B")
    income_df["Year"] = income_df["Rental Start Date"].dt.year

    expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors="coerce")
    expense_df = expense_df.dropna(subset=["Date"])
    expense_df["Month"] = expense_df["Date"].dt.strftime("%B")
    expense_df["Year"] = expense_df["Date"].dt.year

    properties = sorted(set(income_df["Property"].dropna().unique()) | set(expense_df["Property"].dropna().unique()))

    for prop in properties:
        st.markdown(f"### 🏡 {prop}")
        col1, col2 = st.columns(2)

        inc = income_df[income_df["Property"] == prop]
        exp = expense_df[expense_df["Property"] == prop]

        total_income = inc["Amount"].sum() if "Amount" in inc else 0
        total_expense = exp["Amount"].sum() if "Amount" in exp else 0
        profit = total_income - total_expense

        col1.metric("Total Income", f"${total_income:,.2f}")
        col2.metric("Total Expenses", f"${total_expense:,.2f}")
        st.metric("Profit / Loss", f"${profit:,.2f}", delta_color="inverse")

        with st.expander("📈 Monthly Breakdown"):
            monthly = pd.DataFrame({
                "Income": inc.groupby("Month")["Amount"].sum(),
                "Expenses": exp.groupby("Month")["Amount"].sum()
            }).fillna(0)
            monthly = monthly.loc[monthly.index.intersection(pd.date_range(f"{year}-01-01", f"{year}-12-31").strftime("%B").unique())]

            st.bar_chart(monthly)
            csv = monthly.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, f"{prop}_{year}_summary.csv", "text/csv")

        with st.expander("📍 Pie Charts"):
            pie_data = pd.Series({"Income": total_income, "Expenses": total_expense})
            fig, ax = plt.subplots()
            ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

    with st.expander("🌡️ Heatmap - Monthly Totals by Property"):
        inc_pivot = income_df.pivot_table(index="Month", columns="Property", values="Amount", aggfunc="sum", fill_value=0)
        exp_pivot = expense_df.pivot_table(index="Month", columns="Property", values="Amount", aggfunc="sum", fill_value=0)

        st.markdown("**Income Heatmap**")
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        sns.heatmap(inc_pivot, annot=True, fmt=".0f", cmap="Greens", ax=ax1)
        st.pyplot(fig1)

        st.markdown("**Expense Heatmap**")
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        sns.heatmap(exp_pivot, annot=True, fmt=".0f", cmap="Reds", ax=ax2)
        st.pyplot(fig2)

    st.markdown("---")
    with st.expander("📂 View Logged Entries"):
        view_choice = st.radio("Select Type", ["Income", "Expense"], horizontal=True)
        if view_choice == "Income":
            df = income_df.copy()
            st.dataframe(df, use_container_width=True)
        else:
            df = expense_df.copy()
            if "Receipt Link" in df.columns:
                df["Receipt Link"] = df["Receipt Link"].apply(
                    lambda url: f'<a href="{url}" target="_blank">View Receipt</a>' if isinstance(url, str) and url else "")
                st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.dataframe(df, use_container_width=True)

    st.markdown("---")
    with st.expander("🔁 Inject Recurring Expenses"):
        if st.button("📥 Inject Recurring Rows"):
            inserted = inject_recurring_expenses()
            if inserted:
                st.success(f"{inserted} recurring expense(s) injected into {year} OPP Expenses.")
            else:
                st.info("No new rows injected. Possible duplicates skipped.")
