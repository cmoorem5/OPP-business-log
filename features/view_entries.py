import streamlit as st
import pandas as pd
from datetime import date
import re
from utils.google_sheets import load_sheet_as_df, get_worksheet


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
    patterns = [
        r"\d{4}-\d{2}-\d{2}", r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}", r"\d{2}/\d{2}"
    ]
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            date = match.group(0)
            if len(date) == 5:
                date += f"/{pd.Timestamp.now().year}"
            return pd.to_datetime(date, errors='coerce')
    return None


def inject_recurring_expenses(template_sheet="2025 Recurring Expenses", target_sheet="2025 OPP Expenses"):
    try:
        df = load_sheet_as_df(template_sheet)
        required = ["Date", "Expense", "Purchaser", "Property", "Category", "Amount"]
        for col in required:
            if col not in df.columns:
                st.error(f"Missing required column: '{col}' in {template_sheet}")
                return 0

        df = df.dropna(subset=required)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df["Month"] = df["Date"].dt.strftime("%B")

        ws = get_worksheet(target_sheet)
        headers = ws.row_values(1)

        existing_df = load_sheet_as_df(target_sheet)
        existing_df["Date"] = pd.to_datetime(existing_df["Date"], errors="coerce")
        existing_df["Item/Description"] = existing_df["Item/Description"].astype(str)

        existing_pairs = set(
            zip(existing_df["Date"].dt.strftime("%Y-%m-%d"), existing_df["Item/Description"])
        )

        count, skipped = 0, 0
        for _, row in df.iterrows():
            date_str = row["Date"].strftime("%Y-%m-%d")
            description = str(row["Expense"]).strip()
            if (date_str, description) in existing_pairs:
                skipped += 1
                continue

            base_comment = str(row.get("Comments", "")).strip()
            final_comment = f"{base_comment} (Recurring)" if base_comment else "Recurring"

            row_data = {
                "Month": row["Month"],
                "Date": date_str,
                "Purchaser": row["Purchaser"],
                "Item/Description": description,
                "Property": row["Property"],
                "Category": row["Category"],
                "Amount": row["Amount"],
                "Comments": final_comment,
                "Receipt Link": ""
            }
            ws.append_row([row_data.get(h, "") for h in headers], value_input_option="USER_ENTERED")
            count += 1

        if skipped:
            st.info(f"{skipped} duplicate row(s) skipped.")
        return count
    except Exception as e:
        st.error(f"Recurring expense injection failed: {e}")
        return 0


def show():
    st.title("📂 View Logged Entries")

    if st.button("🔄 Refresh Data"):
        load_sheet_as_df.clear()
        try:
            st.experimental_rerun()
        except AttributeError:
            st.warning("Cache cleared. Please reload the page (F5) to see updated data.")
            return

    income_df = _clean_df(load_sheet_as_df("2025 OPP Income"))
    expense_df = _clean_df(load_sheet_as_df("2025 OPP Expenses"))

    choice = st.radio("View", ["Income", "Expense"], key="view_option")
    if choice == "Income":
        st.subheader("💰 Income Entries")
        income_df["Rental Start Date"] = income_df["Rental Dates"].apply(extract_first_valid_date)
        skipped = income_df[income_df["Rental Start Date"].isna()]
        df = income_df.dropna(subset=["Rental Start Date"]).copy()

        df["Rental Month"] = df["Rental Start Date"].dt.strftime("%B")
        df["Rental Year"] = df["Rental Start Date"].dt.year

        props = st.multiselect("Property", df["Property"].dropna().unique().tolist(), default=df["Property"].dropna().unique().tolist())
        today = date.today()
        date_range = st.date_input("Rental Start Date Range", [today.replace(day=1), today], key="date_range_income")

        mask = df["Property"].isin(props)
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        mask &= df["Rental Start Date"].between(start, end)

        filtered = df.loc[mask]
        st.dataframe(filtered, use_container_width=True)

        if not skipped.empty:
            st.warning(f"{len(skipped)} row(s) skipped due to unreadable rental dates.")
            with st.expander("🔍 View Skipped Rows"):
                st.dataframe(skipped[["Rental Dates"]])

    else:
        st.subheader("💸 Expense Entries")
        df = expense_df.copy()

        if "Receipt Link" in df.columns:
            df["Receipt Link"] = df["Receipt Link"].apply(
                lambda url: f'<a href="{url}" target="_blank">View Receipt</a>' if isinstance(url, str) and url else ""
            )

        props = st.multiselect("Property", df["Property"].dropna().unique().tolist(), default=df["Property"].dropna().unique().tolist())
        statuses = df["Complete"].dropna().unique().tolist() if "Complete" in df.columns else []
        selected_statuses = st.multiselect("Status", statuses, default=statuses) if statuses else None
        categories = df["Category"].dropna().unique().tolist() if "Category" in df.columns else []
        selected_categories = st.multiselect("Category", categories, default=categories) if categories else None

        date_range = st.date_input("Expense Date Range", [date.today().replace(day=1), date.today()], key="date_range_expense")

        mask = df["Property"].isin(props)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            mask &= df["Date"].between(start, end)
        if selected_statuses and "Complete" in df.columns:
            mask &= df["Complete"].isin(selected_statuses)
        if selected_categories and "Category" in df.columns:
            mask &= df["Category"].isin(selected_categories)

        filtered = df.loc[mask]

        if "Receipt Link" in filtered.columns:
            st.markdown(filtered.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.dataframe(filtered, use_container_width=True)

        st.markdown("---")
        if st.button("📥 Inject Recurring Expenses"):
            inserted = inject_recurring_expenses()
            if inserted:
                st.success(f"{inserted} recurring expense(s) injected into 2025 OPP Expenses.")
            else:
                st.warning("No new rows injected (duplicates may have been skipped).")
