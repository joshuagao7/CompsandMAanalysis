# Financial Data Notes

## P/E Ratios
- **Trailing P/E**: Calculated as Market Cap / Net Income (or Stock Price / EPS)
- **Negative Earnings**: Companies with negative net income show "N/A" for P/E ratio, as the metric is not meaningful
- **Data Source**: Market data from Yahoo Finance API (yfinance), financial data from EDGAR 10-K filings

## EBITDA Calculations
- EBITDA = Operating Income + Depreciation + Amortization
- D&A (Depreciation & Amortization) is estimated as EBITDA - Operating Income
- For semiconductor companies, D&A typically ranges from 2-10% of revenue

## Data Period
- **Financial Data**: Latest annual data from most recent 10-K filings (typically fiscal year 2024)
- **Market Data**: As of December 1, 2025 (timestamped in market_data.json)

## Growth Metrics
- **CAGR (Compound Annual Growth Rate)**: 3-year compound annual growth rate
- **YoY (Year-over-Year)**: Year-over-year growth rate
- Some companies may have incomplete historical data, resulting in missing CAGR values

## Valuation Multiples
- **EV/Revenue**: Enterprise Value / Revenue
- **EV/EBITDA**: Enterprise Value / EBITDA
- **EV/EBIT**: Enterprise Value / EBIT (Operating Income)
- **P/B**: Price-to-Book ratio (Market Cap / Book Value)
- Multiples may show "N/A" or be blank if denominator is negative or zero

## Known Issues Fixed
1. Intel P/E ratio: Marked as N/A due to negative earnings
2. P/E ratios recalculated from financial data for accuracy
3. EBITDA calculations verified for reasonableness
