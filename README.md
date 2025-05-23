OPP Finance App
A polished, mobile-optimized Streamlit app to track rental income, log expenses, upload receipts, and visualize profit/loss by property. Built for modularity, speed, and seamless Google Sheets + Drive integration.

🔑 Key Features
Income & Expense Logging
Categorize and tag all income and expense entries by property

Support for tracking payment status and rental periods

Receipt Uploads
Upload images or PDFs with each entry

Files are automatically routed to Google Drive by month

Interactive Dashboard
Monthly income, expense, and profit/loss breakdowns

Separate bar charts per property + CSV download

Expanders to reduce visual clutter

Future-year toggle support (e.g., 2026)

View Entries
Filter by property, date range, status, and category

In-page search and real-time slicing

Clickable Drive links for receipts

CSV export of any filtered view

Custom Theming & Branding
Injected CSS for fonts, color palette, shadows

Mobile-ready UI design with compact elements

Persistent Footer
Displays business name, app version, and last-updated timestamp



## Prerequisites

- **Streamlit Secrets**:  
  Ensure your Google service‑account JSON is stored under `gdrive_credentials` in `secrets.toml`.  
- **Sheet & Tab Names**:  
  Verify the `sheet_name` and `tab_name` values in `utils/google_sheets.py` match your actual Google Sheets.

## Installation

```bash
pip install -r requirements.txt
