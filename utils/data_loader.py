import pandas as pd
import streamlit as st

@st.cache_data(ttl=600, show_spinner=False)
def load_excel_data(sheet, path="data/LLC Income and Expense Tracker.xlsx"):
    df = pd.read_excel(path, sheet_name=sheet)
    if "Income Amount" in df.columns:
        df["Income Amount"] = pd.to_numeric(df["Income Amount"], errors="coerce")
        df = df.dropna(subset=["Income Amount"])
    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df = df.dropna(subset=["Amount"])
    return df
