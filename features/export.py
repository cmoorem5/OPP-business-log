import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_loader import load_excel_data

def show():
    """Export filtered Income or Expense data as CSV."""
    st.title("📤 Export Data")

    # ─── Select which dataset ────────────────────────────────────────────
    view = st.radio("Select Data to Export", ["Income", "Expense"], key="export_view")

    # ─── Load data ────────────────────────────────────────────────────────
    with st.spinner("Loading data..."):
        if view == "Income":
            df = load_excel_data("2025 OPP Income").rename(columns={"Income Amount": "Income"})
        else:
            df = load_excel_data("2025 OPP Expenses").rename(columns={"Amount": "Expense"})

    # ─── Apply filters ────────────────────────────────────────────────────
    # Property filter (both)
    props = df["Property"].dropna().unique().tolist()
    selected_props = st.multiselect("Filter by Property", props, default=props)

    if view == "Income":
        # Payment Status filter
        statuses = df["Payment Status"].dropna().unique().tolist()
        selected_statuses = st.multiselect("Filter by Payment Status", statuses, default=statuses)

        mask = (
            df["Property"].isin(selected_props) &
            df["Payment Status"].isin(selected_statuses)
        )
    else:
        # Date range filter
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            min_date, max_date = df["Date"].min(), df["Date"].max()
            start_date, end_date = st.date_input(
                "Date Range", value=(min_date, max_date), key="export_date_range"
            )
            date_mask = (df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))
        else:
            date_mask = pd.Series(True, index=df.index)

        # Category filter
        cats = df["Category"].dropna().unique().tolist()
        selected_cats = st.multiselect("Filter by Category", cats, default=cats)

        mask = (
            df["Property"].isin(selected_props) &
            date_mask &
            df["Category"].isin(selected_cats)
        )

    filtered = df[mask].reset_index(drop=True)

    # ─── Show preview ─────────────────────────────────────────────────────
    st.subheader(f"Preview: {view} Entries ({len(filtered)} rows)")
    st.dataframe(filtered, use_container_width=True)

    # ─── Download button ──────────────────────────────────────────────────
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

    # ─── Custom footer ─────────────────────────────────────────────────────
    st.markdown("---")
    last_updated = datetime.now().strftime("%B %d, %Y %I:%M %p")
    footer = f"""
    <div style="text-align:center; font-size:0.85em; color:gray;">
      Oceanview Property Partners • v1.3.0 • Last updated: {last_updated}
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)
