from utils.google_sheets import load_sheet_as_df, append_row_to_sheet
import pandas as pd

def inject_recurring_expenses(year="2025"):
    try:
        recurring_df = load_sheet_as_df(f"{year} Recurring Expenses")
        target_df = load_sheet_as_df(f"{year} OPP Expenses")

        # Ensure columns exist
        if "Date" not in recurring_df.columns or "Item/Description" not in recurring_df.columns:
            print("Missing required columns in recurring sheet.")
            return 0

        # Parse dates
        recurring_df["Date"] = pd.to_datetime(recurring_df["Date"], errors="coerce")
        target_df["Date"] = pd.to_datetime(target_df["Date"], errors="coerce")

        # Drop rows without key info
        recurring_df = recurring_df.dropna(subset=["Date", "Item/Description"])
        target_df = target_df.dropna(subset=["Date", "Item/Description"])

        # Detect duplicates based on Date + Item/Description
        recurring_df["dupe_key"] = recurring_df["Date"].dt.date.astype(str) + "|" + recurring_df["Item/Description"].astype(str)
        target_df["dupe_key"] = target_df["Date"].dt.date.astype(str) + "|" + target_df["Item/Description"].astype(str)

        existing = set(target_df["dupe_key"])
        new_entries = recurring_df[~recurring_df["dupe_key"].isin(existing)].copy()

        # Append new rows
        inserted = 0
        for _, row in new_entries.iterrows():
            append_row_to_sheet(f"{year} OPP Expenses", row.drop(labels=["dupe_key"]).to_dict())
            inserted += 1

        return inserted

    except Exception as e:
        print(f"Error injecting recurring expenses: {e}")
        return 0
