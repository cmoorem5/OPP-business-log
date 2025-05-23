import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from utils.google_sheets import load_sheet_as_df
from utils.google_drive import make_clickable_link


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


def filter_df(df, props, cats, stats, date_col, date_range):
    mask = df["Property"].isin(props)
    if cats and "Category" in df.columns:
        mask &= df["Category"].isin(cats)
    if stats and "Complete" in df.columns:
        mask &= df["Complete"].isin(stats)
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        if date_range:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            mask &= df[date_col].between(start, end)
    return df.loc[mask]


def show():
    st.title("📂 View Logged Entries")

    if st.button("🔄 Refresh Data"):
        load_sheet_as_df.clear()
        st.experimental_rerun()

    view_type = st.radio("Select Entry Type", ["Income", "Expense"], horizontal=True)
    year = st.selectbox("Year", ["2025", "2026"], index=0)

    if view_type == "Income":
        st.subheader("💰 Income Entries")
        df = _clean_df(load_sheet_as_df(f"{year} OPP Income"))
        if "Income Amount" in df.columns:
            df.rename(columns={"Income Amount": "Amount"}, inplace=True)
        df["Rental Start Date"] = df["Rental Dates"].apply(extract_first_valid_date)
        skipped = df[df["Rental Start Date"].isna()]
        df = df.dropna(subset=["Rental Start Date"]).copy()
        df["Rental Month"] = pd.Categorical(
            df["Rental Start Date"].dt.strftime("%B"),
            categories=[
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ],
            ordered=True
        )
        df["Rental Year"] = df["Rental Start Date"].dt.year
        date_col = "Rental Start Date"
    else:
        st.subheader("💸 Expense Entries")
        df = _clean_df(load_sheet_as_df(f"{year} OPP Expenses"))
        skipped = pd.DataFrame()
        date_col = "Date"

    props = st.multiselect("Property", df["Property"].dropna().unique().tolist(), default=df["Property"].dropna().unique().tolist())
    cats = st.multiselect("Category", df["Category"].dropna().unique().tolist(), default=df["Category"].dropna().unique().tolist()) if "Category" in df.columns else []
    stats = st.multiselect("Status", df["Complete"].dropna().unique().tolist(), default=df["Complete"].dropna().unique().tolist()) if "Complete" in df.columns else []

    default_start = pd.to_datetime(f"{year}-01-01")
    default_end = pd.Timestamp.now()
    date_range = st.date_input("Date Range", [default_start, default_end], key=f"date_range_{view_type.lower()}")

    filtered = filter_df(df.copy(), props, cats, stats, date_col, date_range)

    if "Receipt Link" in filtered.columns:
        filtered["Receipt Link"] = filtered["Receipt Link"].apply(make_clickable_link)

    st.markdown(f"**{len(filtered)} entries found**")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv, file_name=f"{view_type.lower()}_{year}_filtered.csv", mime="text/csv")

    if view_type == "Income" and not skipped.empty:
        st.warning(f"{len(skipped)} row(s) skipped due to unreadable rental dates.")
        with st.expander("🔍 View Skipped Rows"):
            st.dataframe(skipped[["Rental Dates"]])

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

            # Bar: Total by Month
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

            # Bar: Total by Property
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

            # Pie: Category Breakdown
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
