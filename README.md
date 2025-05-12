# OPP Finance App

A polished and modular Streamlit application to track income, expenses, upload receipts, and view profit/loss for your investment properties, with enhanced filtering, theming, caching, and version history.

## Key Features

- **Income & Expense Logging**  
- **Receipt Uploads**  
- **Dashboard** with monthly profit/loss charts  
- **View Entries** page with:  
  - Property, date‑range, status, and category filters  
  - Clickable receipt links  
- **In‑page Search & Filters** for slicing data on-the-fly  
- **Custom Theming** via injected CSS for branded fonts, colors, and shadows  
- **Persistent Footer** showing company name, app version, and “last updated” timestamp  
- **CSV Export** of any filtered view

## Prerequisites

- **Streamlit Secrets**:  
  Ensure your Google service‑account JSON is stored under `gdrive_credentials` in `secrets.toml`.  
- **Sheet & Tab Names**:  
  Verify the `sheet_name` and `tab_name` values in `utils/google_sheets.py` match your actual Google Sheets.

## Installation

```bash
pip install -r requirements.txt
