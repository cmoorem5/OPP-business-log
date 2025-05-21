# 📘 CHANGELOG – OPP Finance Tracker

All notable changes to this project will be documented in this file.

---

## [v1.3.0] – 2025-05-21
### ✨ New Features
- Added year selector to Rental Entry form (2025 or 2026)
- Dynamically routes income entries to the correct Google Sheet tab (e.g., `2026 OPP Income`)

### 🧠 Logic Improvements
- Dashboard now summarizes income based on **rental start date** (from “Rental Dates”) instead of the booking date
- Ensures income reporting aligns with when the property is actually rented

### 🔒 Dashboard Limitations (by design)
- Currently locked to `2025 OPP Income` only
- 2026 income is tracked but excluded from graphs and summaries until end-of-year transition

---

## [v1.2.0-dev]
- Added internal debugging tools and formatting enhancements
- Introduced consistent dropdown data loading from Google Sheets

## [v1.1.0-dev]
- Google Sheets and Drive integration completed
- Uploads receipts and saves viewable links to entries

## [v1.0.0]
- Initial release of modular Streamlit app for expense/income tracking
- Includes Dashboard, Entry Forms, and Google Sheet sync

