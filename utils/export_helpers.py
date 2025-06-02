import pandas as pd
import io
import zipfile

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
        workbook = writer.book
        bold = workbook.add_format({"bold": True})
        currency = workbook.add_format({"num_format": "$#,##0.00"})
        total = workbook.add_format({"bold": True, "num_format": "$#,##0.00"})

        def write_df(df, sheet, currency_cols=None, add_total=False):
            if df.empty:
                return
            df_out = df.copy()

            # Append totals row if requested
            if add_total and currency_cols:
                totals = {
                    col: df_out[col].sum() if col in currency_cols else "Total"
                    for col in df_out.columns
                }
                df_out.loc[len(df_out)] = totals

            df_out.to_excel(writer, sheet_name=sheet, index=False)
            ws = writer.sheets[sheet]

            for i, col in enumerate(df_out.columns):
                col_width = max(len(str(col)), *(df_out[col].astype(str).str.len())) + 2
                fmt = currency if currency_cols and col in currency_cols else None
                ws.set_column(i, i, col_width, fmt)
                ws.write(0, i, col, bold)

        write_df(income_df, "Income", currency_cols=["Amount Received"])
        write_df(expense_df, "Expenses", currency_cols=["Amount"])
        if summary_df is not None:
            write_df(summary_df, "Summary", currency_cols=["Amount"])

        if "Income Source" in income_df.columns:
            income_summary = (
                income_df.groupby("Income Source")["Amount Received"]
                .sum()
                .reset_index()
                .sort_values(by="Amount Received", ascending=False)
            )
            write_df(income_summary, "Income by Source", currency_cols=["Amount Received"], add_total=True)

        if "Category" in expense_df.columns:
            expense_summary = (
                expense_df.groupby("Category")["Amount"]
                .sum()
                .reset_index()
                .sort_values(by="Amount", ascending=False)
            )
            write_df(expense_summary, "Expenses by Category", currency_cols=["Amount"], add_total=True)

    output.seek(0)
    return output


def generate_zip_export(income_df, expense_df, summary_df, year):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        if not income_df.empty:
            zip_file.writestr(f"{year}_Income.csv", income_df.to_csv(index=False))
        if not expense_df.empty:
            zip_file.writestr(f"{year}_Expenses.csv", expense_df.to_csv(index=False))
        if summary_df is not None:
            zip_file.writestr(f"{year}_Summary.csv", summary_df.to_csv(index=False))

        if "Income Source" in income_df.columns:
            income_summary = (
                income_df.groupby("Income Source")["Amount Received"]
                .sum()
                .reset_index()
                .sort_values(by="Amount Received", ascending=False)
            )
            income_summary.loc[len(income_summary)] = [
                "Total",
                income_summary["Amount Received"].sum()
            ]
            zip_file.writestr(f"{year}_Income_by_Source.csv", income_summary.to_csv(index=False))

        if "Category" in expense_df.columns:
            expense_summary = (
                expense_df.groupby("Category")["Amount"]
                .sum()
                .reset_index()
                .sort_values(by="Amount", ascending=False)
            )
            expense_summary.loc[len(expense_summary)] = [
                "Total",
                expense_summary["Amount"].sum()
            ]
            zip_file.writestr(f"{year}_Expenses_by_Category.csv", expense_summary.to_csv(index=False))

    buffer.seek(0)
    return buffer
