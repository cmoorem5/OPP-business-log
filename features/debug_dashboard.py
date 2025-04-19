import streamlit as st
import pandas as pd
from utils.google_sheets import get_worksheet

def show():
    st.title("🧪 Dashboard Debug: Income Sheet")

    sheet_name = "OPP Finance Tracker"
    tab_name = "2025 OPP Income"

    try:
        ws = get_worksheet(sheet_name, tab_name)
        df = pd.DataFrame(ws.get_all_records())

        st.markdown("### 🔍 Raw Data Preview")
        st.dataframe(df)

        st.markdown("### 📋 Column Names Detected")
        st.write(list(df.columns))

        st.markdown("### 🔎 Trying to parse 'Income Amount' to numeric...")
        if "Income Amount" in df.columns:
            cleaned = pd.to_numeric(df["Income Amount"], errors="coerce")
            st.write("Sample Parsed Values:")
            st.write(cleaned.head())
            st.write("✅ Total Income:", cleaned.sum())
        else:
            st.warning("'Income Amount' column not found!")

    except Exception as e:
        st.error(f"Error loading or parsing sheet: {e}")
