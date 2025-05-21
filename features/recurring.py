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

        # Clean and unify string keys
        recurring_df["Item/Description"] = recurring_df["Item/Description"].astype(str).str.strip().str.lower()
        target_df["Item/Description"] = target_df["Item/Description"].astype(str).str.strip().str.lower()

        recurring_df["Key"] = recurring_df["Date"].dt.strftime("%Y-%m-%d") + "|" + recurring_df["Item/Description"]
        target_df["Key"] = target_df["Date"].dt.strftime("%Y-%m-%d") + "|" + target_df["Item/Description"]

        existing_keys = set(target_df["Key"])
        new_rows = recurring_df[~recurring_df["Key"].isin(existing_keys)]

        print(f"🔍 Total recurring entries: {len(recurring_df)}")
        print(f"📄 Already in sheet: {len(existing_keys)} keys")
        print(f"🆕 New unique rows to inject: {len(new_rows)}")
        print("🗝 Sample keys to inject:", new_rows['Key'].head(10).tolist())

        inserted_count = 0
        for _, row in new_rows.iterrows():
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
