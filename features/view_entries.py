import streamlit as st
from utils.google_sheets import load_sheet_as_df

def show():
    st.title("📂 View Logged Entries")

    sheet = "OPP Finance Tracker"
    income_df  = load_sheet_as_df(sheet, "2025 OPP Income")
    expense_df = load_sheet_as_df(sheet, "2025 OPP Expenses")

    view_option = st.radio("View", ["Income", "Expense"], key="view_option")
    if view_option == "Income":
        st.subheader("💰 Income Entries")
        st.dataframe(income_df, use_container_width=True)
    else:
        st.subheader("💸 Expense Entries")
        if "Receipt Link" in expense_df.columns:
            expense_df["Receipt Link"] = expense_df["Receipt Link"].apply(
                lambda url: f"[View Receipt]({url})" if isinstance(url, str) else ""
            )
        st.markdown("### Expense Log with Clickable Receipt Links")
        st.markdown(expense_df.to_markdown(index=False), unsafe_allow_html=True)
