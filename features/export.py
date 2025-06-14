import streamlit as st
from utils.export_helpers import (
    load_and_process_data,
    generate_summary,
    generate_excel_export,
    generate_zip_export
)

def show():
    st.title("📁 Export Financial Data")
    st.caption("Download income, expenses, and summary for your accountant or tax records.")

    year = st.radio("Select Year", ["2025", "2026"], horizontal=True)

    try:
        income_df, expense_df = load_and_process_data(year)
        if income_df.empty and expense_df.empty:
            st.warning("No financial data found.")
            return

        summary_df = generate_summary(income_df, expense_df)
        excel_file = generate_excel_export(income_df, expense_df, summary_df)

        st.download_button(
            label="📥 Download Excel Export",
            data=excel_file,
            file_name=f"{year}_financial_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        with st.expander("📦 Need individual CSV files?"):
            zip_file = generate_zip_export(income_df, expense_df, summary_df, year)
            st.download_button(
                label="Download ZIP of CSVs",
                data=zip_file,
                file_name=f"{year}_financial_export.zip",
                mime="application/zip"
            )

        with st.expander("📊 Preview Summary"):
            st.dataframe(summary_df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to load or export data: {e}")
