# Financial Data Extraction from 10-K Filings

## Overview

This workflow uses a **master table approach** for better data management:

1. **Extract** → Save all raw data to `master_financial_data.csv` (single source of truth)
2. **Populate** → Generate individual comparison tables from master
3. **Format** → Convert to LaTeX tables for the document

This approach makes it easy to:
- Audit all data in one place
- Regenerate comparison tables without re-extracting
- Add new metrics or modify calculations
- Track historical data

## Quick Start

### 1. Install Dependencies

```bash
# Option 1: Using pip (if allowed)
pip3 install beautifulsoup4

# Option 2: Using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Option 3: Using --user flag
pip3 install --user beautifulsoup4
```

### 2. Extract Data from 10-Ks

```bash
python3 scripts/extract_10k_data.py
```

This script:
- Processes all 10-K HTML files in `data/` subdirectories
- Extracts financial metrics using XBRL data and HTML parsing
- Saves all data to `tables/csv/master_financial_data.csv`

### 3. Generate Comparison Tables

```bash
python3 scripts/populate_comparison_tables.py
```

This script:
- Reads from `master_financial_data.csv`
- Generates individual comparison tables in `tables/csv/comps/`
- Formats data appropriately for each table type

### 4. Add Market Data & Complete

1. **Open** `tables/csv/master_financial_data.csv`
2. **Add columns** for Market Cap and Enterprise Value (or add them manually)
3. **Re-run** `populate_comparison_tables.py` to update comparison tables
4. **Generate LaTeX**: `python3 scripts/csv_to_latex.py --all`

## How It Works

The script uses two extraction methods:

1. **XBRL Inline Data** (Primary): Extracts structured financial data from `<ix:nonFraction>` tags
   - More accurate and reliable
   - Uses standardized US-GAAP tags
   - Handles scaling automatically

2. **HTML Table Parsing** (Fallback): Parses HTML tables if XBRL data is incomplete
   - Searches for financial statement tables
   - Extracts key line items

## Extracted Metrics

- Revenue
- EBITDA / EBIT
- Net Income
- Cash & Cash Equivalents
- Total Debt
- R&D Expenses
- SG&A Expenses
- Gross Profit
- Operating Cash Flow
- Capital Expenditures
- Shares Outstanding

## Derived Metrics (Calculated)

- Gross Margin %
- R&D as % of Revenue
- Net Margin %
- Operating Margin %
- Net Debt
- Free Cash Flow

## Master Table Structure

The master table (`master_financial_data.csv`) contains all extracted metrics:

**Income Statement:**
- Revenue, Cost of Revenue, Gross Profit, Gross Margin %
- R&D Expense, R&D % of Revenue
- SG&A Expense
- EBIT, EBITDA, EBITDA Margin %
- Operating Margin %, Net Income, Net Margin %

**Balance Sheet:**
- Cash, Total Debt, Net Debt, Total Equity
- Shares Outstanding

**Cash Flow:**
- Operating Cash Flow, Capital Expenditures, Free Cash Flow

**Metadata:**
- Filing Date, Fiscal Year

## Manual Steps Required

Some data must be added manually (not in 10-K filings):

1. **Add Market Data to Master Table:**
   - Open `tables/csv/master_financial_data.csv`
   - Add columns: `Market_Cap`, `Enterprise_Value` (or add manually to comparison tables)
   - Get data from Yahoo Finance, Bloomberg, etc.

2. **Re-run Comparison Tables:**
   ```bash
   python3 scripts/populate_comparison_tables.py
   ```
   This will recalculate valuation multiples with the new market data.

3. **Add Historical Data** (for growth metrics):
   - Add previous years' data to master table
   - Or manually fill growth metrics in comparison tables

4. **Generate LaTeX Tables:**
   ```bash
   python3 scripts/csv_to_latex.py --all
   ```

## Troubleshooting

### "ModuleNotFoundError: No module named 'bs4'"
- Install BeautifulSoup4: `pip3 install beautifulsoup4` or use virtual environment

### "No HTML files found"
- Make sure 10-K files are saved as `.html` or `.htm` in company subdirectories
- Check file names match expected patterns

### Missing or incorrect data
- Some companies format 10-Ks differently
- Check the HTML file manually to verify data exists
- You may need to manually fill in missing values

## Workflow Summary

```
10-K HTML Files
    ↓
extract_10k_data.py
    ↓
master_financial_data.csv  ← Single source of truth
    ↓
populate_comparison_tables.py
    ↓
Individual Comparison Tables (revenue_profitability.csv, etc.)
    ↓
csv_to_latex.py
    ↓
LaTeX Tables for Document
```

## Benefits of Master Table Approach

✅ **Single Source of Truth**: All data in one place  
✅ **Easy Auditing**: Verify numbers in master table  
✅ **Regenerate Tables**: Change formatting without re-extracting  
✅ **Add Metrics**: Add new columns to master, regenerate tables  
✅ **Historical Tracking**: Keep multiple periods in master  
✅ **Less Duplication**: No repeated extraction logic

## Alternative: Manual Extraction

If the script doesn't work or you prefer manual control:

1. Open the 10-K HTML file in a browser
2. Navigate to "Consolidated Statements of Operations" (usually Item 8)
3. Copy key financial figures
4. Manually update `master_financial_data.csv`
5. Run `populate_comparison_tables.py` to generate comparison tables

The script is designed to save time, but manual entry is always an option!

