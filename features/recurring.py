from utils.google_sheets import load_sheet_as_df, append_row_to_sheet
import pandas as pd

def inject_recurring_expenses(year="2025"):
    try:
        recurring_df = load_sheet_as_df(f"{year} Recurring Expenses")
        target_df = load_sheet_as_df(f"{year} OPP Expenses")

        # Normalize and clean
        recurring_df = recurring_df.dropna(subset=["Date", "Item/Description"])
        target_df = target_df.dropna(subset=["Date", "Item/Description"])

        recurring_df["Date"] = pd.to_datetime(recurring_df["Date"], errors="coerce")
        target_df["Date"] = pd.to_datetime(target_df["Date"], errors="coerce")

        # Clean string values
        recurring_df["Item/Description"] = recurring_df["Item/Description"].astype(str).str.strip()
        target_df["Item/Description"] = target_df["Item/Description"].astype(str).str.strip()

        # Detect duplicates
        recurring_df["Key"] = recurring_df["Date"].dt.date.astype(str) + "|" + recurring_df["Item/Description"]
        target_df["Key"] = target_df["Date"].dt.date.astype(str) + "|" + target_df["Item/Description"]
        existing_keys = set(target_df["Key"])

        new_rows = recurring_df[~recurring_df["Key"].isin(existing_keys)]
        inserted_count = 0

        for _, row in new_rows.iterrows():
            # Create dictionary to match target headers
            row_dict = {
                "Month": row["Date"].strftime("%B"),
                "Date": row["Date"].strftime("%Y-%m-%d"),
                "Purchaser": row.get("Purchaser", ""),
                "Item/Description": row["Item/Description"],
                "Property": row.get("Property", ""),
                "Category": row.get("Category", ""),
                "Amount": str(row.get("Amount", "")).replace(",", ""),
                "Comments": row.get("Comments", ""),
                "Receipt Link": ""
            }
            append_row_to_sheet(f"{year} OPP Expenses", row_dict)
            inserted_count += 1

        return inserted_count

    except Exception as e:
        print(f"[Recurring Injection Error] {e}")
        return 0
