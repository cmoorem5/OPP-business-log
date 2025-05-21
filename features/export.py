import streamlit as st
import pandas as pd
from datetime import datetime
import re
from utils.data_loader import load_excel_data

def extract_first_valid_date(date_str):
    """Extract first valid date from a string with fallback to current year."""
    if not isinstance(date_str, str):
        return None
    date_str = date_str.replace("–", "-").replace("--", "-").strip()

    patterns = [
        r"\d{4}-\d{2}-\d{2}",     # 2025-08-01
        r"\d{2}/\d{2}/\d{4}",     # 08/01/2025
        r"\d{2}-\d{2}-\d{4}",     # 08-01-2025
        r"\d{2}/\d{2}",           # 08/01 (assume current year)
    ]

    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            date = match.group(0)
            if len(date) == 5:
                date += f"/{pd.Timestamp.now().year}"
            return pd.to_datetime(date, errors='coerce')
    return None

def show():
    """Export filtered Income or Expense data as CSV."""
    st.title("📤 Export Data")

    # 1️⃣ Choose dataset
    view = st.radio("Select Data to Export", ["Income", "Expense"], key="export_view")

    # 2️⃣ Load data
    with st.spinner("Loading data..."):
        if view == "Income":
            df = load_excel_data("2025 OPP Income").rename(columns={"Income Amount": "Income"})
            df["Rental Start Date"] = df["Rental Dates"].apply(extract_first_valid_date)
            skipped = df[df["Rental Start Date"].isna()]
            df = df.dropna(subset=["Rental Start Date"]).copy()
        else:
            df = load_excel_data("2025 OPP Expenses").rename(columns={"Amount": "Expense"})
            skipped = pd.DataFrame()  # No skipped logic for expense

    # 3️⃣ Filters
    mask = pd.Series(True, index=df.index)

    # Property filter
    if "Property" in df.columns:
        props = df["Property"].dropna().unique().tolist()
        selected_props = st.multiselect("Filter by Property", props, default=props)
        mask &= df["Property"].isin(selected_props)

    if view == "Income":
        # Status filter
        if "Complete" in df.columns:
            statuses = df["Complete"].dropna().unique().tolist()
            selected_statuses = st.multiselect("Filter by Payment Status", statuses, default=statuses)
            mask &= df["Complete"].isin(selected_statuses)

        # Date filter on Rental Start Date
        start_date = df["Rental Start Date"].min()
        end_date = df["Rental Start Date"].max()
        dr = st.date_input("Rental Start Date Range", (start_date, end_date), key="rental_date_range")
        mask &= df["Rental Start Date"].between(pd.to_datetime(dr[0]), pd.to_datetime(dr[1]))

    else:
        # Date filter on Expense Date
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            min_date, max_date = df["Date"].min(), df["Date"].max()
            dr = st.date_input("Expense Date Range", (min_date, max_date), key="expense_date_range")
            mask &= df["Date"].between(pd.to_datetime(dr[0]), pd.to_datetime(dr[1]))

        # Category filter
        if "Category" in df.columns:
            cats = df["Category"].dropna().unique().tolist()
            selected_cats = st.multiselect("Filter by Category", cats, default=cats)
            mask &= df["Category"].isin(selected_cats)

    # 4️⃣ Apply mask and show preview
    filtered = df[mask].reset_index(drop=True)
    st.subheader(f"Preview: {view} Entries ({len(filtered)} rows)")
    st.dataframe(filtered, use_container_width=True)

    # 5️⃣ Download button
    csv_data = filtered.to_csv(index=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{view.lower()}_data_{timestamp}.csv"
    st.download_button(
        f"📥 Download {view} Data as CSV",
        csv_data,
        filename,
        mime="text/csv",
        key="download_button"
    )

    # 6️⃣ Skipped rows notice
    if not skipped.empty:
        st.warning(f"{len(skipped)} row(s) skipped due to unreadable rental start dates.")
        with st.expander("🔍 View Skipped Rows"):
            st.dataframe(skipped[["Rental Dates"]])

    # 7️⃣ Footer
    st.markdown("---")
    last_updated = datetime.now().strftime("%B %d, %Y %I:%M %p")
    st.markdown(
        f"""
        <div style="text-align:center; font-size:0.85em; color:gray;">
            Oceanview Property Partners • v1.3.0 • Last updated: {last_updated}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(footer, unsafe_allow_html=True)
