import streamlit as st
import pandas as pd
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("🔍 Debug: 2025 OPP Expenses")

    try:
        df = load_sheet_as_df("2025 OPP Expenses")
        st.success(f"✅ Loaded {len(df)} rows")

        st.markdown("### 🧾 Columns Detected")
        st.write(df.columns.tolist())

        if "Category" in df.columns:
            st.markdown("### 📂 Unique Categories")
            st.write(sorted(df["Category"].dropna().unique()))

        if "Item" in df.columns:
            st.markdown("### 🏷 Matching: Mortgage, HELOC, Insurance, Utilities")
            keywords = ["mortgage", "heloc", "insurance", "utilities"]
            filtered = df[df["Item"].str.lower().fillna("").str.contains("|".join(keywords))]
            st.dataframe(filtered)

            st.markdown(f"**🧮 Found {len(filtered)} rows with matching keywords**")

        else:
            st.warning("⚠️ Column 'Item' not found in sheet.")

    except Exception as e:
        st.error(f"❌ Failed to load or parse sheet: {e}")
