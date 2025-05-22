import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from utils.google_sheets import load_sheet_as_df


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
            return pd.to_datetime(date, errors="coerce")
    return None


def show():
    st.title("📊 Income & Expense Dashboard")

    year = st.radio("Select Year", ["2025", "2026"], horizontal=True)

    income_df = _clean_df(load_sheet_as_df(f"{year} OPP Income"))
    income_df.columns = income_df.columns.str.strip().str.title()

    required_cols = [
        "Month", "Name", "Property", "Rental Dates",
        "Amount Owed", "Amount Received", "Balance", "Status"
    ]
    missing_cols = [col for col in required_cols if col not in income_df.columns]
    if missing_cols:
        st.error(f"🚫 Missing column(s) in income sheet: {', '.join(missing_cols)}")
        st.stop()

    if "Income Amount" in income_df.columns:
        income_df.rename(columns={"Income Amount": "Amount Owed"}, inplace=True)

    for col in ["Amount Owed", "Amount Received", "Balance"]:
        income_df[col] = pd.to_numeric(income_df[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)

    income_df["Property"] = income_df["Property"].astype(str).str.strip().str.title()
    income_df["Rental Start Date"] = income_df["Rental Dates"].apply(extract_first_valid_date)
    income_df = income_df.dropna(subset=["Rental Start Date"])
    income_df["Month"] = income_df["Rental Start Date"].dt.strftime("%B")
    income_df["Year"] = income_df["Rental Start Date"].dt.year

    expense_df = _clean_df(load_sheet_as_df(f"{year} OPP Expenses"))
    expense_df.columns = expense_df.columns.str.strip().str.title()
    expense_df["Property"] = expense_df["Property"].astype(str).str.strip().str.title()
    expense_df["Amount"] = pd.to_numeric(expense_df["Amount"].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
    expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors="coerce")
    expense_df = expense_df.dropna(subset=["Date"])
    expense_df["Month"] = expense_df["Date"].dt.strftime("%B")
    expense_df["Year"] = expense_df["Date"].dt.year

    properties = sorted(set(income_df["Property"].dropna().unique()) | set(expense_df["Property"].dropna().unique()))
    month_order = list(pd.date_range("2025-01-01", "2025-12-31", freq="MS").strftime("%B").unique())

    for prop in properties:
        st.markdown(f"## 🏠 {prop} Summary")

        col1, col2 = st.columns(2)
        inc = income_df[income_df["Property"].str.lower() == prop.lower()]
        exp = expense_df[expense_df["Property"].str.lower() == prop.lower()]

        total_income = inc["Amount Owed"].sum()
        total_expense = exp["Amount"].sum()
        profit = total_income - total_expense

        col1.metric("Total Income (Owed)", f"${total_income:,.2f}")
        col2.metric("Total Expenses", f"${total_expense:,.2f}")
        st.metric("Profit / Loss", f"${profit:,.2f}", delta_color="inverse")

        import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from utils.google_sheets import load_sheet_as_df


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
            return pd.to_datetime(date, errors="coerce")
    return None


def show():
    st.title("📊 Income & Expense Dashboard")

    year = st.radio("Select Year", ["2025", "2026"], horizontal=True)

    income_df = _clean_df(load_sheet_as_df(f"{year} OPP Income"))
    income_df.columns = income_df.columns.str.strip().str.title()

    required_cols = [
        "Month", "Name", "Property", "Rental Dates",
        "Amount Owed", "Amount Received", "Balance", "Status"
    ]
    missing_cols = [col for col in required_cols if col not in income_df.columns]
    if missing_cols:
        st.error(f"🚫 Missing column(s) in income sheet: {', '.join(missing_cols)}")
        st.stop()

    if "Income Amount" in income_df.columns:
        income_df.rename(columns={"Income Amount": "Amount Owed"}, inplace=True)

    for col in ["Amount Owed", "Amount Received", "Balance"]:
        income_df[col] = pd.to_numeric(income_df[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)

    income_df["Property"] = income_df["Property"].astype(str).str.strip().str.title()
    income_df["Rental Start Date"] = income_df["Rental Dates"].apply(extract_first_valid_date)
    income_df = income_df.dropna(subset=["Rental Start Date"])
    income_df["Month"] = income_df["Rental Start Date"].dt.strftime("%B")
    income_df["Year"] = income_df["Rental Start Date"].dt.year

    expense_df = _clean_df(load_sheet_as_df(f"{year} OPP Expenses"))
    expense_df.columns = expense_df.columns.str.strip().str.title()
    expense_df["Property"] = expense_df["Property"].astype(str).str.strip().str.title()
    expense_df["Amount"] = pd.to_numeric(expense_df["Amount"].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
    expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors="coerce")
    expense_df = expense_df.dropna(subset=["Date"])
    expense_df["Month"] = expense_df["Date"].dt.strftime("%B")
    expense_df["Year"] = expense_df["Date"].dt.year

    properties = sorted(set(income_df["Property"].dropna().unique()) | set(expense_df["Property"].dropna().unique()))
    month_order = list(pd.date_range("2025-01-01", "2025-12-31", freq="MS").strftime("%B").unique())

    for prop in properties:
        st.markdown(f"## 🏠 {prop} Summary")

        col1, col2 = st.columns(2)
        inc = income_df[income_df["Property"].str.lower() == prop.lower()]
        exp = expense_df[expense_df["Property"].str.lower() == prop.lower()]

        total_income = inc["Amount Owed"].sum()
        total_expense = exp["Amount"].sum()
        profit = total_income - total_expense

        col1.metric("Total Income (Owed)", f"${total_income:,.2f}")
        col2.metric("Total Expenses", f"${total_expense:,.2f}")
        st.metric("Profit / Loss", f"${profit:,.2f}", delta_color="inverse")

        with st.expander("📈 Monthly Breakdown + Category Filter", expanded=True):
            available_categories = exp["Category"].dropna().unique().tolist()
            selected_categories = st.multiselect(
                "Filter by Category (optional)",
                available_categories,
                default=available_categories,
                key=f"{prop}_category_filter"
            )

            filtered_exp = exp[exp["Category"].isin(selected_categories)]

            monthly = pd.DataFrame({
                "Income (Owed)": inc.groupby("Month")["Amount Owed"].sum(),
                "Expenses": filtered_exp.groupby("Month")["Amount"].sum()
            }).reindex(month_order).fillna(0)
            monthly["Profit"] = monthly["Income (Owed)"] - monthly["Expenses"]

            x = range(len(monthly))
            width = 0.4

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar([i - width / 2 for i in x], monthly["Income (Owed)"], width=width, label="Income", color="#2ecc71")
            ax.bar([i + width / 2 for i in x], monthly["Expenses"], width=width, label="Expenses", color="#e74c3c", alpha=0.8)
            ax.plot(x, monthly["Profit"], color="black", marker="o", linewidth=2, label="Profit")

            ax.set_xticks(x)
            ax.set_xticklabels(monthly.index, rotation=45)
            ax.set_ylabel("Amount ($)")
            ax.set_title(f"{prop} – Monthly Financials")
            ax.legend(title="Legend")
            ax.grid(True, axis="y", linestyle="--", alpha=0.3)

            st.pyplot(fig)

            csv = monthly.reset_index().to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV",
                csv,
                file_name=f"{prop}_{year}_summary.csv",
                mime="text/csv",
                key=f"{prop}_{year}_summary_btn"
            )

        with st.expander("📍 Pie Charts", expanded=False):
            pie_data = pd.Series({
                "Income (Owed)": total_income,
                "Expenses": total_expense
            })
            fig, ax = plt.subplots()
            ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

        with st.expander("🚨 Payments Due", expanded=True):
            due_df = inc[inc["Balance"] > 0].copy()
            due_df["Rental Start Date"] = due_df["Rental Dates"].apply(extract_first_valid_date)
            today = pd.Timestamp.now().normalize()

            if due_df.empty:
                st.success("✅ All bookings are paid in full!")
            else:
                due_df["Alert"] = due_df.apply(
                    lambda row: "🔴 **Overdue**" if row["Rental Start Date"] and row["Rental Start Date"] < today
                    else "🟡 **Pending**", axis=1
                )

                display_cols = [
                    "Month", "Name", "Property", "Rental Dates",
                    "Amount Owed", "Amount Received", "Balance", "Status", "Alert"
                ]
                display_cols = [col for col in display_cols if col in due_df.columns]

                due_df = due_df[display_cols].sort_values(by="Balance", ascending=False)
                st.warning(f"{len(due_df)} outstanding payment(s) found:")
                st.dataframe(due_df, use_container_width=True)

                csv = due_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download Outstanding Payments CSV",
                    csv,
                    file_name=f"{prop}_{year}_payments_due.csv",
                    mime="text/csv",
                    key=f"{prop}_{year}_payments_due_btn"
                )

    st.markdown("---")
    with st.expander("📂 View Logged Entries", expanded=False):
        view_choice = st.radio("Select Type", ["Income", "Expense"], horizontal=True)
        df = income_df if view_choice == "Income" else expense_df

        if view_choice == "Expense" and "Receipt Link" in df.columns:
            df["Receipt Link"] = df["Receipt Link"].apply(
                lambda url: f'<a href="{url}" target="_blank">View Receipt</a>' if isinstance(url, str) and url else "")
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.dataframe(df, use_container_width=True)
