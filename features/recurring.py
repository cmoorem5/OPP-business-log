from utils.google_sheets import load_sheet_as_df, append_row_to_sheet
import pandas as pd


def inject_recurring_expenses(year="2025"):
    try:
        recurring_df = load_sheet_as_df(f"{year} Recurring Expenses")
        target_df = load_sheet_as_df(f"{year} OPP Expenses")

        # Format dates
        recurring_df["Date"] = pd.to_datetime(recurring_df["Date"], errors="coerce")
        target_df["Date"] = pd.to_datetime(target_df["Date"], errors="coerce")

        # Clean columns
        recurring_df = recurring_df.dropna(subset=["Date", "Description"])
        target_df = target_df.dropna(subset=["Date", "Description"])

        # Detect duplicates by Date + Description
        existing = set(
            target_df.apply(lambda row: f"{row['Date'].date()}|{row['Description']}", axis=1)
        )
        new_entries = recurring_df[
            ~recurring_df.apply(lambda row: f"{row['Date'].date()}|{row['Description']}", axis=1).isin(existing)
        ]

        # Append new entries
        inserted_count = 0
        for _, row in new_entries.iterrows():
            append_row_to_sheet(f"{year} OPP Expenses", row.to_dict())
            inserted_count += 1

        return inserted_count

    except Exception as e:
        print(f"Error injecting recurring expenses: {e}")
        return 0
