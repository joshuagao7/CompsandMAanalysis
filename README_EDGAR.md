# EDGAR Data Extraction Setup

This directory contains tools to extract SEC filing data for semiconductor companies (NVIDIA, MCHP, AMD, and Lattice Semiconductor) using edgartools.

## Setup Complete ✅

The following has been set up for you:

### 1. Environment Setup
- **Python Environment**: Python 3.13.3 detected
- **edgartools Installation**: Installed via pipx for isolated environment management
- **SEC API Access**: Configured with proper User-Agent identity

### 2. Available Scripts

#### `edgar_data_extraction.py` - Basic Company Data
Extracts basic company information and metadata:
```bash
python3 edgar_data_extraction.py
```

**Output**: `edgar_semiconductor_data.json` containing:
- Company names, CIK numbers, SIC codes
- Basic company information for NVDA, MCHP, AMD, LSCC

#### `edgar_financial_data.py` - Financial Data Access
Demonstrates access to financial statements and XBRL facts:
```bash
python3 edgar_financial_data.py
```

**Output**: `edgar_financial_data.json` containing:
- Latest 10-K and 10-Q filing dates
- Availability of Income Statement, Balance Sheet, Cash Flow
- Company facts (XBRL data) with counts

## Current Status

### ✅ Working Features
- Company information extraction (name, CIK, SIC)
- Latest 10-K and 10-Q filing dates
- Access to financial statements (Income Statement, Balance Sheet, Cash Flow)
- Company facts/XBRL data (thousands of data points per company)

### ⚠️ Known Issues
- Filing lists may require different API approach due to PyArrow compatibility
- Some filing attributes need alternative access methods

### 📊 Sample Results (Last Run)

| Company | CIK     | Latest 10-K | Latest 10-Q | Facts Count |
|---------|---------|-------------|-------------|-------------|
| NVDA    | 1045810 | 2025-02-26  | 2025-11-19  | 26,034      |
| MCHP    | 827054  | 2025-05-23  | 2025-11-06  | 27,394      |
| AMD     | 2488    | 2025-02-05  | 2025-11-05  | 22,562      |
| LSCC    | 855658  | 2025-02-14  | 2025-11-03  | 19,089      |

## How to Use

### Basic Usage
1. Run the extraction scripts to get current data:
   ```bash
   python3 edgar_data_extraction.py
   python3 edgar_financial_data.py
   ```

2. Check the generated JSON files for extracted data:
   - `edgar_semiconductor_data.json` - Basic company data
   - `edgar_financial_data.json` - Financial data access info

### Accessing Financial Statements

The edgartools library provides direct access to financial statements:

```python
from edgar import Company, set_identity

# Set identity (required for SEC API)
set_identity("Your Name your.email@domain.com")

# Get company
company = Company("NVDA")

# Access financial statements
income_statement = company.income_statement
balance_sheet = company.balance_sheet 
cash_flow = company.cash_flow

# Get facts (XBRL data)
facts = company.get_facts()
```

### Available Company Methods
Each company object provides these useful methods:
- `latest_tenk` - Latest 10-K filing
- `latest_tenq` - Latest 10-Q filing  
- `income_statement` - Income statement data
- `balance_sheet` - Balance sheet data
- `cash_flow` - Cash flow statement data
- `get_facts()` - All XBRL facts
- `get_financials()` - Financial data
- `get_filings()` - All filings

## Next Steps

### For Analysis
1. **Financial Metrics**: Extract specific metrics from the facts data
2. **Time Series**: Build historical financial data over time
3. **Comparisons**: Compare metrics across the four companies
4. **Ratios**: Calculate financial ratios and performance indicators

### For Development
1. **Enhanced Filing Access**: Resolve PyArrow compatibility for full filing lists
2. **Caching**: Add data caching for better performance
3. **Automation**: Set up scheduled data updates
4. **Visualization**: Add charts and graphs for financial data

## File Structure
```
CompsandMAanalysis/
├── README_EDGAR.md                    # This guide
├── edgar_data_extraction.py           # Basic data extraction
├── edgar_financial_data.py            # Financial data access
├── edgar_semiconductor_data.json      # Basic company data output
├── edgar_financial_data.json          # Financial data output
└── edgar_env/                         # Virtual environment (if using)
```

## Dependencies
- **edgartools**: SEC filing data access
- **Python 3.13+**: Runtime environment
- **pipx**: Package management (recommended)

## Support
- edgartools documentation: https://github.com/dgunning/edgartools
- SEC EDGAR database: https://www.sec.gov/edgar

---
*Setup completed on 2025-12-01*