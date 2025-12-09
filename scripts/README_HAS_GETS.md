# Has/Gets Analysis Calculation Scripts

## Overview
These scripts calculate all pro forma financial metrics for the Has/Gets analysis table in the NVIDIA-Lattice Semiconductor acquisition.

## Scripts

### 1. `calculate_has_gets.py`
**Purpose**: Calculate all Has/Gets metrics and display detailed output

**Usage**:
```bash
python3 scripts/calculate_has_gets.py
```

**Output**: 
- Detailed calculation breakdown
- Transaction parameters
- Seller Gets metrics
- Buyer Gets (pro forma) metrics
- Formatted values ready for CSV

### 2. `update_has_gets_table.py`
**Purpose**: Calculate metrics and automatically update the CSV file

**Usage**:
```bash
python3 scripts/update_has_gets_table.py
```

**Output**: 
- Updates `tables/csv/ma/has_gets_analysis.csv` with calculated values
- Prints summary of key updates

## Key Calculations

### Transaction Parameters
- **Offer Price**: Current Lattice price × (1 + 30% premium) = $89.19
- **Transaction Value**: Offer Price × Shares Outstanding = $12.20B
- **Goodwill**: Transaction Value - Lattice Book Value = $11.49B

### Seller Gets (Lattice)
- **Share Price**: $89.19 (30% premium)
- **PE Ratio**: N/A (receiving cash, not equity)
- **Total Consideration**: $12.20B

### Buyer Gets (NVIDIA Pro Forma)

#### Combined Financials
- **Pro Forma Net Income**: NVDA + Lattice + After-Tax Synergies = $73.04B
- **Pro Forma EBITDA**: NVDA + Lattice + Synergies = $88.85B
- **Pro Forma Debt**: NVDA + Lattice = $32.41B
- **Pro Forma Cash**: NVDA Cash + Lattice Cash - Purchase Price = $48.53B
- **Pro Forma Equity**: NVDA Equity - Purchase Price + Goodwill = $78.62B

#### Key Ratios
- **P/E Ratio**: 60.08x (Market Cap / Pro Forma Net Income)
- **Debt/EBITDA**: 0.36x
- **EBITDA/Interest**: 68.54x
- **Debt/Capitalization**: 29.19%
- **Net Debt/Capitalization**: -14.52% (negative = net cash position)

## Assumptions

1. **Tax Rate**: 21% (corporate tax rate)
2. **Interest Rate**: 4% (on outstanding debt)
3. **D&A as % of Revenue**:
   - NVIDIA: 2%
   - Lattice: 3%
4. **Premium**: 30% (strategic acquisition typical range: 25-40%)
5. **Synergies**: $123.2M annual (from synergy_estimates.csv)
6. **Deal Structure**: 100% cash (no stock consideration)

## Data Sources

- **Financial Data**: `data/master_financials.json`
- **Market Data**: `data/market_data.json`
- **Synergies**: `tables/csv/ma/synergy_estimates.csv`

## Output Files

- **CSV Table**: `tables/csv/ma/has_gets_analysis.csv`
- **LaTeX Table**: `tables/tex/ma/has_gets_analysis.tex` (needs manual update or separate script)

## Notes

- All calculations assume immediate realization of synergies
- Goodwill is calculated as purchase price minus book value
- Pro forma metrics combine standalone metrics and adjust for transaction effects
- Negative net debt indicates net cash position (strong balance sheet)

## Troubleshooting

If calculations seem off:
1. Verify data files are up to date
2. Check that financial data matches latest 10-K filings
3. Review market data timestamp
4. Adjust assumptions (tax rate, interest rate, D&A %) if needed

