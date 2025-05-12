import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_loader import load_excel_data

def show():
    """Export filtered Income or Expense data as CSV."""
    st.title("📤 Export Data")

    # 1️⃣ Choose dataset
    view = st.radio("Select Data to Export", ["Income", "Expense"], key="export_view")

    # 2️⃣ Load data with spinner
    with st.spinner("Loading data..."):
        if view == "Income":
            df = (
                load_excel_data("2025 OPP Income")
                .rename(columns={"Income Amount": "Income"})
            )
        else:
            df = (
                load_excel_data("2025 OPP Expenses")
                .rename(columns={"Amount": "Expense"})
            )

    # 3️⃣ Build a base mask of True, then apply filters only if the column exists
    mask = pd.Series(True, index=df.index)

    # Property filter
    if "Property" in df.columns:
        props = df["Property"].dropna().unique().tolist()
        selected_props = st.multiselect("Filter by Property", props, default=props)
        mask &= df["Property"].isin(selected_props)

    if view == "Income":
        # Payment Status filter
        if "Payment Status" in df.columns:
            statuses = df["Payment Status"].dropna().unique().tolist()
            selected_statuses = st.multiselect(
                "Filter by Payment Status", statuses, default=statuses
            )
            mask &= df["Payment Status"].isin(selected_statuses)

    else:
        # Date range filter
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            min_date, max_date = df["Date"].min(), df["Date"].max()
            start_date, end_date = st.date_input(
                "Date Range", value=(min_date, max_date), key="export_date_range"
            )
            mask &= (df["Date"] >= pd.to_datetime(start_date)) & \
                    (df["Date"] <= pd.to_datetime(end_date))

        # Category filter
        if "Category" in df.columns:
            cats = df["Category"].dropna().unique().tolist()
            selected_cats = st.multiselect(
                "Filter by Category", cats, default=cats
            )
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

    # 6️⃣ Footer
    st.markdown("---")
    last_updated = datetime.now().strftime("%B %d, %Y %I:%M %p")
    footer = f"""
    <div style="text-align:center; font-size:0.85em; color:gray;">
      Oceanview Property Partners • v1.3.0 • Last updated: {last_updated}
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)
