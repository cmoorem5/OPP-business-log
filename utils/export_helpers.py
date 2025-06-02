import pandas as pd
import io

from utils.google_sheets import load_sheet_as_df
from utils.config import SHEET_ID


def load_and_process_data(year: str):
    income_tab = f"{year} OPP Income"
    expense_tab = f"{year} OPP Expenses"

    income_df = load_sheet_as_df(SHEET_ID, income_tab)
    expense_df = load_sheet_as_df(SHEET_ID, expense_tab)

    income_df = clean_amount_column(income_df, "Amount Received")
    expense_df = clean_amount_column(expense_df, "Amount")

    return income_df, expense_df


def clean_amount_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.replace(r"[\$,]", "", regex=True),
        errors="coerce"
    ).fillna(0)
    return df


def generate_summary(income_df: pd.DataFrame, expense_df: pd.DataFrame) -> pd.DataFrame:
    total_income = income_df["Amount Received"].sum() if not income_df.empty else 0
    total_expense = expense_df["Amount"].sum() if not expense_df.empty else 0
    profit = total_income - total_expense

    return pd.DataFrame({
        "Category": ["Total Income", "Total Expenses", "Profit"],
        "Amount": [total_income, total_expense, profit]
    })


def generate_excel_export(income_df, expense_df, summary_df=None):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        if not income_df.empty:
            income_df.to_excel(writer, sheet_name="Income", index=False)
        if not expense_df.empty:
            expense_df.to_excel(writer, sheet_name="Expenses", index=False)
        if summary_df is not None:
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
    output.seek(0)
    return output
