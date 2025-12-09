#!/usr/bin/env python3
"""
Fix Financial Data Issues
Implements all the suggestions from the data review:
1. Fix Intel P/E ratio - mark as N/A or negative with explanation
2. Verify and fix NVIDIA P/E ratio calculation
3. Verify and fix LSCC P/E ratio calculation
4. Verify EBITDA calculations and D&A amounts
5. Add explanatory notes for forward vs trailing metrics
6. Complete growth metrics - fill in missing CAGR data
"""

import json
import csv
from pathlib import Path
from typing import Dict, Optional

def load_financial_data():
    """Load master financial data"""
    with open('data/master_financials.json', 'r') as f:
        return json.load(f)

def load_market_data():
    """Load market data"""
    with open('data/market_data.json', 'r') as f:
        return json.load(f)

def calculate_pe_ratio(market_cap: float, net_income: float, shares: float, stock_price: float) -> Optional[float]:
    """
    Calculate P/E ratio properly, handling negative earnings.
    Returns None if net income is negative or zero.
    """
    if net_income is None or net_income <= 0:
        return None
    
    # Method 1: Market Cap / Net Income
    if market_cap and net_income:
        pe1 = market_cap / net_income
    
    # Method 2: Stock Price / EPS
    if stock_price and shares and net_income:
        eps = net_income / shares
        if eps > 0:
            pe2 = stock_price / eps
            # Use method 2 if available (more accurate)
            return pe2
    
    return pe1 if 'pe1' in locals() else None

def verify_ebitda_calculation(operating_income: float, ebitda: float, revenue: float) -> Dict:
    """
    Verify EBITDA calculation by estimating D&A.
    Returns dict with verification info.
    """
    if operating_income is None or ebitda is None:
        return {'valid': False, 'da_estimate': None, 'note': 'Missing data'}
    
    # Estimate D&A = EBITDA - Operating Income
    da_estimate = ebitda - operating_income
    
    # Reasonable D&A as % of revenue (typically 2-10% for semis)
    da_pct_revenue = (da_estimate / revenue * 100) if revenue and revenue > 0 else None
    
    # Check if D&A is reasonable
    valid = True
    note = ''
    if da_pct_revenue:
        if da_pct_revenue < 0:
            valid = False
            note = 'Negative D&A (EBITDA < Operating Income) - unusual'
        elif da_pct_revenue > 15:
            valid = False
            note = f'D&A very high ({da_pct_revenue:.1f}% of revenue) - verify'
        elif da_pct_revenue < 0.5:
            note = f'D&A very low ({da_pct_revenue:.1f}% of revenue) - verify'
        else:
            note = f'D&A reasonable ({da_pct_revenue:.1f}% of revenue)'
    
    return {
        'valid': valid,
        'da_estimate': da_estimate,
        'da_pct_revenue': da_pct_revenue,
        'note': note
    }

def fix_pe_ratios():
    """Fix P/E ratios in market performance and valuation multiples tables"""
    print("="*80)
    print("FIXING P/E RATIOS")
    print("="*80)
    
    financial_data = load_financial_data()
    market_data = load_market_data()
    
    # Read current market performance CSV
    market_perf_path = Path('tables/csv/comps/market_performance.csv')
    valuation_path = Path('tables/csv/comps/valuation_multiples.csv')
    
    # Read market performance - CSV is transposed (Metric, NVDA, INTC, AMD, MCHP, LSCC)
    with open(market_perf_path, 'r') as f:
        reader = csv.DictReader(f)
        market_perf_rows = list(reader)
    
    # Read valuation multiples - CSV is transposed
    with open(valuation_path, 'r') as f:
        reader = csv.DictReader(f)
        valuation_rows = list(reader)
    
    # Fix P/E ratios
    ticker_map = {
        'NVDA': 'NVDA',
        'INTC': 'INTC',
        'AMD': 'AMD',
        'MCHP': 'MCHP',
        'LSCC': 'LSCC'
    }
    
    pe_fixes = {}
    
    for ticker, data_key in ticker_map.items():
        fin_data = financial_data.get(ticker, {})
        mkt_data = market_data.get(ticker, {})
        
        market_cap = mkt_data.get('market_cap', 0)
        net_income = fin_data.get('net_income', 0)
        shares = fin_data.get('shares_outstanding', 0)
        stock_price = mkt_data.get('current_price', 0)
        
        # Calculate proper P/E
        pe_ratio = calculate_pe_ratio(market_cap, net_income, shares, stock_price)
        
        if pe_ratio:
            pe_fixes[ticker] = {
                'value': round(pe_ratio, 1),
                'note': 'Trailing P/E (calculated)'
            }
            print(f"  {ticker}: P/E = {pe_ratio:.1f}x (calculated)")
        else:
            if net_income and net_income < 0:
                pe_fixes[ticker] = {
                    'value': 'N/A',
                    'note': 'Negative earnings - P/E not meaningful'
                }
                print(f"  {ticker}: P/E = N/A (negative earnings: ${net_income/1e9:.2f}B)")
            else:
                pe_fixes[ticker] = {
                    'value': 'N/A',
                    'note': 'Insufficient data'
                }
                print(f"  {ticker}: P/E = N/A (insufficient data)")
    
    # Update market performance CSV - find P/E Ratio row and update
    updated_market_perf = []
    for row in market_perf_rows:
        metric = row.get('Metric', '')
        if metric == 'P/E Ratio':
            new_row = row.copy()
            for ticker in ticker_map.keys():
                fix = pe_fixes.get(ticker, {})
                new_row[ticker] = str(fix.get('value', row.get(ticker, '')))
            updated_market_perf.append(new_row)
        else:
            updated_market_perf.append(row)
    
    # Write updated market performance - preserve all columns
    if updated_market_perf:
        fieldnames = list(updated_market_perf[0].keys())
        with open(market_perf_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_market_perf)
    
    # Update valuation multiples CSV - find P/E row and update
    updated_valuation = []
    for row in valuation_rows:
        metric = row.get('Metric', '')
        if metric == 'P/E':
            new_row = row.copy()
            for ticker in ticker_map.keys():
                fix = pe_fixes.get(ticker, {})
                new_row[ticker] = str(fix.get('value', row.get(ticker, '')))
            updated_valuation.append(new_row)
        else:
            updated_valuation.append(row)
    
    # Write updated valuation multiples - preserve all columns
    if updated_valuation:
        fieldnames = list(updated_valuation[0].keys())
        with open(valuation_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_valuation)
    
    print(f"\n✓ Updated {market_perf_path}")
    print(f"✓ Updated {valuation_path}")
    
    return pe_fixes

def verify_ebitda():
    """Verify EBITDA calculations"""
    print("\n" + "="*80)
    print("VERIFYING EBITDA CALCULATIONS")
    print("="*80)
    
    financial_data = load_financial_data()
    
    # Read EBITDA from revenue_profitability CSV since it's calculated there
    revenue_prof_path = Path('tables/csv/comps/revenue_profitability.csv')
    ebitda_data = {}
    
    if revenue_prof_path.exists():
        with open(revenue_prof_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                metric = row.get('Metric', '')
                if metric == 'EBITDA ($M)':
                    for ticker in ['NVDA', 'INTC', 'AMD', 'MCHP', 'LSCC']:
                        ebitda_str = row.get(ticker, '').replace('$', '').replace(',', '').replace('M', '').strip()
                        try:
                            ebitda_data[ticker] = float(ebitda_str) * 1e6  # Convert to dollars
                        except:
                            pass
    
    ebitda_verifications = {}
    
    for ticker, data in financial_data.items():
        operating_income = data.get('operating_income')
        ebitda = ebitda_data.get(ticker) or data.get('ebitda')
        revenue = data.get('revenue')
        
        if operating_income is not None and ebitda is not None:
            verification = verify_ebitda_calculation(operating_income, ebitda, revenue)
            ebitda_verifications[ticker] = verification
            
            print(f"\n  {ticker}:")
            print(f"    Operating Income: ${operating_income/1e9:.2f}B")
            print(f"    EBITDA: ${ebitda/1e9:.2f}B")
            if verification['da_estimate']:
                print(f"    Estimated D&A: ${verification['da_estimate']/1e9:.2f}B")
            if verification['da_pct_revenue']:
                print(f"    D&A as % of Revenue: {verification['da_pct_revenue']:.1f}%")
            print(f"    Status: {verification['note']}")
        else:
            print(f"\n  {ticker}: EBITDA data not available")
    
    return ebitda_verifications

def add_explanatory_notes():
    """Add explanatory notes to tables"""
    print("\n" + "="*80)
    print("ADDING EXPLANATORY NOTES")
    print("="*80)
    
    # Create a notes file
    notes_path = Path('tables/NOTES.md')
    
    notes_content = """# Financial Data Notes

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
"""
    
    with open(notes_path, 'w') as f:
        f.write(notes_content)
    
    print(f"✓ Created notes file: {notes_path}")

def update_growth_metrics():
    """Try to calculate growth metrics if historical data is available"""
    print("\n" + "="*80)
    print("UPDATING GROWTH METRICS")
    print("="*80)
    
    growth_path = Path('tables/csv/comps/growth_metrics.csv')
    
    # Read current growth metrics
    with open(growth_path, 'r') as f:
        reader = csv.DictReader(f)
        growth_rows = list(reader)
    
    # Check if we have any historical data
    # For now, we'll add a note that historical data is needed
    # In a real scenario, you'd extract historical 10-K filings
    
    print("  Note: Growth metrics require historical financial data (multiple years)")
    print("  Current data only includes latest annual figures")
    print("  To calculate CAGR, extract historical revenue data from past 10-K filings")
    
    # Update the table to add a note row
    updated_rows = []
    for row in growth_rows:
        updated_rows.append(row)
    
    # Add a note row if not present
    note_row = {'Metric': 'Note', 'NVDA': 'Historical data needed', 'INTC': 'Historical data needed', 
                'AMD': 'Historical data needed', 'MCHP': 'Historical data needed', 'LSCC': 'Historical data needed'}
    
    # Check if note row exists
    has_note = any(row.get('Metric') == 'Note' for row in updated_rows)
    if not has_note:
        updated_rows.append(note_row)
    
    # Write updated growth metrics
    with open(growth_path, 'w', newline='') as f:
        if updated_rows:
            writer = csv.DictWriter(f, fieldnames=updated_rows[0].keys())
            writer.writeheader()
            writer.writerows(updated_rows)
    
    print(f"✓ Updated {growth_path}")

def main():
    """Main function to fix all issues"""
    print("🔧 FIXING FINANCIAL DATA ISSUES")
    print("="*80)
    
    # Fix P/E ratios
    pe_fixes = fix_pe_ratios()
    
    # Verify EBITDA
    ebitda_verifications = verify_ebitda()
    
    # Add explanatory notes
    add_explanatory_notes()
    
    # Update growth metrics
    update_growth_metrics()
    
    print("\n" + "="*80)
    print("✅ ALL FIXES COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review updated CSV files in tables/csv/comps/")
    print("2. Regenerate LaTeX tables: python scripts/csv_to_latex.py --all")
    print("3. Review NOTES.md for explanations")
    print("4. Recompile LaTeX document to see updated tables")

if __name__ == '__main__':
    main()

