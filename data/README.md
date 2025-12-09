# 📊 Data Directory

## Structure

```
data/
├── master_financials.json    # ⭐ MASTER DATA - Single source of truth
├── master_comps.csv          # ⭐ MASTER TABLE - Summary comps
├── processed/                # Timestamped extraction outputs
├── raw/                      # Raw EDGAR extractions (historical)
└── [nvda|amd|mchp|lattice]/ # Company-specific HTML files (10-K filings)
```

## Master Files

### `master_financials.json`
**Single source of truth** for all financial data. Contains:
- Company info (ticker, name, CIK, SIC, industry)
- Income statement metrics (revenue, net income)
- Balance sheet metrics (assets, equity, current assets/liabilities)
- Calculated ratios (ROE, ROA, margins, etc.)
- Extraction timestamp

**Updated by**: `scripts/extract_data.py`

### `master_comps.csv`
Summary table of all companies for quick reference. Contains:
- Ticker, Company name
- Revenue, Net Income, Assets, Equity
- Key ratios (Net Margin, ROE, ROA, Current Ratio)

**Updated by**: `scripts/extract_data.py`

## Processed Files

Files in `processed/` are timestamped outputs from data extraction runs:
- `IB_Semiconductor_Comps_YYYYMMDD_HHMMSS.csv` - Comps table
- `IB_Detailed_Financials_YYYYMMDD_HHMMSS.json` - Detailed metrics

These are kept for historical reference but `master_financials.json` is always the current version.

## Raw Data

Files in `raw/` are historical raw extractions from EDGAR exploration. Can be ignored for normal workflow.

## Company Directories

HTML files from 10-K filings stored by company ticker. Used for reference but not required for analysis.
