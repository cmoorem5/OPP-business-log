import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
from utils.google_sheets import load_sheet_as_df


def extract_start_date(date_range_str):
    if not isinstance(date_range_str, str):
        return None
    date_range_str = date_range_str.replace("–", "-").replace("--", "-").strip()
    patterns = [
        r"\d{4}-\d{2}-\d{2}", r"\d{2}/\d{2}/\d{4}", r"\d{2}-\d{2}-\d{4}", r"\d{2}/\d{2}"
    ]
    for pattern in patterns:
        match = re.search(pattern, date_range_str)
        if match:
            date = match.group(0)
            if len(date) == 5:
                date += f"/{pd.Timestamp.now().year}"
            return pd.to_datetime(date, errors='coerce')
    return None


def inject_recurring_expenses(template_sheet="2025 Recurring Expenses", target_sheet="2025 OPP Expenses"):
    try:
        df = load_sheet_as_df(template_sheet)
        required = ["Date", "Item/Description", "Purchaser", "Property", "Category", "Amount"]
        for col in required:
            if col not in df.columns:
                st.error(f"Missing required column: '{col}' in {template_sheet}")
                return 0

        df = df.dropna(subset=required)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df["Month"] = df["Date"].dt.strftime("%B")

        from utils.google_sheets import get_worksheet
        ws = get_worksheet(target_sheet)
        headers = ws.row_values(1)

        existing_df = load_sheet_as_df(target_sheet)
        existing_df["Date"] = pd.to_datetime(existing_df["Date"], errors="coerce")
        existing_df["Item/Description"] = existing_df["Item/Description"].astype(str)

        existing_pairs = set(
            zip(existing_df["Date"].dt.strftime("%Y-%m-%d"), existing_df["Item/Description"])
        )

        count, skipped = 0, 0
        for _, row in df.iterrows():
            date_str = row["Date"].strftime("%Y-%m-%d")
            description = str(row["Item/Description"]).strip()
            if (date_str, description) in existing_pairs:
                skipped += 1
                continue

            base_comment = str(row.get("Comments", "")).strip()
            final_comment = f"{base_comment} (Recurring)" if base_comment else "Recurring"

            row_data = {
                "Month": row["Month"],
                "Date": date_str,
                "Purchaser": row["Purchaser"],
                "Item/Description": description,
                "Property": row["Property"],
                "Category": row["Category"],
                "Amount": row["Amount"],
                "Comments": final_comment,
                "Receipt Link": ""
            }
            ws.append_row([row_data.get(h, "") for h in headers], value_input_option="USER_ENTERED")
            count += 1

        if skipped:
            st.info(f"{skipped} duplicate row(s) skipped.")
        return count

    except Exception as e:
        st.error(f"Recurring expense injection failed: {e}")
        return 0
