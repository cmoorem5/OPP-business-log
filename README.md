# Investment Property Financial Management App

## Overview
This Streamlit app manages and visualizes financial data for your investment property.

## Features
- Log income and expenses
- Upload and store receipt files
- Dashboard with charts for profit/loss
- Export financial data to CSV

## Setup Instructions
1. Install requirements:
   ```
   pip install streamlit pandas matplotlib openpyxl
   ```
2. Place your Excel file in a `data/` folder:
   - File: `LLC Income and Expense Tracker.xlsx`

3. Run the app:
   ```
   streamlit run app.py
   ```

## Notes
- Data is currently not saved back to Excel.
- Uploaded receipts are stored in the `/receipts` folder.
