import pandas as pd
from utils.google_sheets import load_sheet_as_df

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def load_and_process_expenses(year: str) -> pd.DataFrame:
    df = load_sheet_as_df(f"{year} OPP Expenses")

    if "Amount" not in df.columns:
        raise ValueError("'Amount' column missing in sheet.")

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Amount"])

    df["Type"] = df["Comments"].fillna("").apply(
        lambda x: "Recurring" if "recurring" in x.lower() else "One-Time"
    )
    df["Month"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%B")
    df = df.dropna(subset=["Month"])
    return df

def generate_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)
    return summary.reindex(MONTH_ORDER, fill_value=0)

def generate_type_totals(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Type")["Amount"].sum()
