#!/usr/bin/env python3
"""
Populate Comps Tables from Master Financial Data

This script reads from master_financials.json and market_data.json
and generates all comparison tables for the comps analysis.
"""

import json
import csv
from pathlib import Path
from typing import Dict, Optional

# Company tickers in order
COMPANIES = ['NVDA', 'INTC', 'AMD', 'MCHP', 'LSCC']
COMPANY_NAMES = {
    'NVDA': 'NVIDIA',
    'INTC': 'Intel',
    'AMD': 'AMD',
    'MCHP': 'Microchip',
    'LSCC': 'Lattice'
}

def format_currency(value: float, unit: str = 'B') -> str:
    """Format float as currency string."""
    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    else:
        return f"${value:,.0f}"

def format_percent(value: float) -> str:
    """Format as percentage."""
    return f"{value:.2f}%"

def format_ratio(value: float) -> str:
    """Format as ratio."""
    return f"{value:.2f}x"

def calculate_ebitda(operating_income: float, revenue: float, da_pct: float) -> float:
    """Calculate EBITDA = Operating Income + D&A."""
    da = revenue * da_pct
    return operating_income + da

def populate_market_cap_ev(financials: Dict, market_data: Dict, output_path: Path):
    """Generate market cap and enterprise value table."""
    headers = ['Metric'] + COMPANIES
    
    def get_price(ticker):
        if ticker in market_data and 'current_price' in market_data[ticker]:
            return f"{market_data[ticker]['current_price']:.2f}"
        return 'N/A'
    
    def get_market_cap(ticker):
        if ticker in market_data and 'market_cap' in market_data[ticker]:
            return format_currency(market_data[ticker]['market_cap'], 'B')
        return 'N/A'
    
    def get_ev(ticker):
        if ticker in market_data and 'enterprise_value' in market_data[ticker]:
            return format_currency(market_data[ticker]['enterprise_value'], 'B')
        return 'N/A'
    
    def get_mc_revenue(ticker):
        if ticker in market_data and 'market_cap' in market_data[ticker] and financials[ticker]['revenue'] > 0:
            return f"{market_data[ticker]['market_cap'] / financials[ticker]['revenue']:.2f}"
        return 'N/A'
    
    rows = [
        ['Stock Price ($)'] + [get_price(ticker) for ticker in COMPANIES],
        ['Market Cap ($B)'] + [get_market_cap(ticker) for ticker in COMPANIES],
        ['Enterprise Value ($B)'] + [get_ev(ticker) for ticker in COMPANIES],
        ['Market Cap/Revenue (x)'] + [get_mc_revenue(ticker) for ticker in COMPANIES],
    ]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def populate_revenue_profitability(financials: Dict, output_path: Path):
    """Generate revenue and profitability table."""
    headers = ['Metric'] + COMPANIES
    rows = [
        ['Revenue ($B)'] + [format_currency(financials[ticker]['revenue'], 'B') for ticker in COMPANIES],
        ['Gross Margin (%)'] + [
            format_percent(financials[ticker]['gross_margin']) 
            if 'gross_margin' in financials[ticker] else 'N/A'
            for ticker in COMPANIES
        ],
        ['Operating Margin (%)'] + [
            format_percent(financials[ticker]['operating_margin'])
            if 'operating_margin' in financials[ticker] else 'N/A'
            for ticker in COMPANIES
        ],
        ['Net Income ($B)'] + [format_currency(financials[ticker]['net_income'], 'B') for ticker in COMPANIES],
        ['Net Margin (%)'] + [
            format_percent(financials[ticker]['net_margin'])
            if 'net_margin' in financials[ticker] else 'N/A'
            for ticker in COMPANIES
        ],
        ['ROE (%)'] + [
            format_percent(financials[ticker]['roe'])
            if 'roe' in financials[ticker] and financials[ticker]['roe'] else 'N/A'
            for ticker in COMPANIES
        ],
        ['ROA (%)'] + [
            format_percent(financials[ticker]['roa'])
            if 'roa' in financials[ticker] and financials[ticker]['roa'] else 'N/A'
            for ticker in COMPANIES
        ],
    ]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def populate_valuation_multiples(financials: Dict, market_data: Dict, output_path: Path):
    """Generate valuation multiples table."""
    headers = ['Metric'] + COMPANIES
    
    # Calculate EBITDA for each company
    da_pcts = {'NVDA': 0.02, 'INTC': 0.02, 'AMD': 0.02, 'MCHP': 0.03, 'LSCC': 0.03}
    ebitdas = {}
    for ticker in COMPANIES:
        ebitdas[ticker] = calculate_ebitda(
            financials[ticker]['operating_income'],
            financials[ticker]['revenue'],
            da_pcts.get(ticker, 0.02)
        )
    
    def get_pe(ticker):
        if ticker in market_data and 'pe_ratio' in market_data[ticker]:
            pe = market_data[ticker]['pe_ratio']
            if pe and pe < 1000:
                return f"{pe:.1f}"
        return 'N/A'
    
    def get_pb(ticker):
        if ticker in market_data and 'pb_ratio' in market_data[ticker]:
            return f"{market_data[ticker]['pb_ratio']:.2f}"
        return 'N/A'
    
    def get_ev_revenue(ticker):
        if ticker in market_data and 'enterprise_value' in market_data[ticker] and financials[ticker]['revenue'] > 0:
            return f"{market_data[ticker]['enterprise_value'] / financials[ticker]['revenue']:.2f}"
        return 'N/A'
    
    def get_ev_ebitda(ticker):
        if ticker in market_data and 'enterprise_value' in market_data[ticker] and ebitdas[ticker] > 0:
            return f"{market_data[ticker]['enterprise_value'] / ebitdas[ticker]:.2f}"
        return 'N/A'
    
    def get_ev_ebit(ticker):
        if ticker in market_data and 'enterprise_value' in market_data[ticker] and financials[ticker]['operating_income'] > 0:
            return f"{market_data[ticker]['enterprise_value'] / financials[ticker]['operating_income']:.2f}"
        return 'N/A'
    
    rows = [
        ['P/E Ratio'] + [get_pe(ticker) for ticker in COMPANIES],
        ['P/B Ratio'] + [get_pb(ticker) for ticker in COMPANIES],
        ['EV/Revenue (x)'] + [get_ev_revenue(ticker) for ticker in COMPANIES],
        ['EV/EBITDA (x)'] + [get_ev_ebitda(ticker) for ticker in COMPANIES],
        ['EV/EBIT (x)'] + [get_ev_ebit(ticker) for ticker in COMPANIES],
    ]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def populate_operating_metrics(financials: Dict, output_path: Path):
    """Generate operating metrics table."""
    headers = ['Metric'] + COMPANIES
    
    rows = [
        ['R&D as % of Revenue'] + [
            'N/A'  # Would need R&D data from financials
            for ticker in COMPANIES
        ],
        ['Asset Turnover (x)'] + [
            format_ratio(financials[ticker]['asset_turnover'])
            if 'asset_turnover' in financials[ticker] else 'N/A'
            for ticker in COMPANIES
        ],
        ['Current Ratio (x)'] + [
            format_ratio(financials[ticker]['current_ratio'])
            if 'current_ratio' in financials[ticker] else 'N/A'
            for ticker in COMPANIES
        ],
        ['Debt/Equity (x)'] + [
            format_ratio(financials[ticker]['debt_to_equity'] / 100)
            if 'debt_to_equity' in financials[ticker] else 'N/A'
            for ticker in COMPANIES
        ],
        ['Debt/Assets (%)'] + [
            format_percent(financials[ticker]['debt_to_assets'])
            if 'debt_to_assets' in financials[ticker] else 'N/A'
            for ticker in COMPANIES
        ],
    ]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def populate_growth_metrics(financials: Dict, output_path: Path):
    """Generate growth metrics table."""
    headers = ['Metric'] + COMPANIES
    
    # Note: CAGR would need historical data, so we'll leave placeholder
    rows = [
        ['Revenue Growth (YoY)'] + ['N/A' for _ in COMPANIES],  # Would need historical data
        ['3-Year CAGR'] + ['N/A' for _ in COMPANIES],  # Would need historical data
    ]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def load_market_data_from_csv(csv_path: Path) -> Dict:
    """Load market data from market_performance.csv."""
    market_data = {}
    if not csv_path.exists():
        return market_data
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        # Parse the CSV structure
        for row in rows:
            metric = row['Metric']
            for ticker in COMPANIES:
                if ticker not in market_data:
                    market_data[ticker] = {}
                
                value = row.get(ticker, '').replace(',', '').replace('$', '').replace('"', '').strip()
                
                if metric == 'Stock Price ($)':
                    try:
                        market_data[ticker]['current_price'] = float(value)
                    except:
                        pass
                elif metric == 'Market Cap ($B)':
                    try:
                        # Convert billions to actual value
                        market_data[ticker]['market_cap'] = float(value) * 1_000_000_000
                    except:
                        pass
                elif metric == 'Enterprise Value ($B)':
                    try:
                        market_data[ticker]['enterprise_value'] = float(value) * 1_000_000_000
                    except:
                        pass
                elif metric == 'P/E Ratio':
                    try:
                        if value != 'N/A':
                            market_data[ticker]['pe_ratio'] = float(value)
                    except:
                        pass
                elif metric == 'P/B Ratio':
                    try:
                        market_data[ticker]['pb_ratio'] = float(value)
                    except:
                        pass
    
    return market_data

def main():
    """Main function to populate all comps tables."""
    base_path = Path(__file__).parent.parent
    
    # Load data
    financials_path = base_path / 'data' / 'master_financials.json'
    market_perf_path = base_path / 'tables' / 'csv' / 'comps' / 'market_performance.csv'
    
    if not financials_path.exists():
        print(f"Error: {financials_path} not found")
        return
    
    financials = json.load(open(financials_path))
    
    # Load market data from CSV
    market_data = load_market_data_from_csv(market_perf_path)
    if not market_data:
        print("Warning: Could not load market data from market_performance.csv")
        print("Some metrics may be missing.")
    
    # Output directory
    output_dir = base_path / 'tables' / 'csv' / 'comps'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Populate all tables
    print("Populating comps tables...")
    
    populate_market_cap_ev(
        financials, 
        market_data, 
        output_dir / 'market_cap_ev.csv'
    )
    print("  ✓ market_cap_ev.csv")
    
    populate_revenue_profitability(
        financials,
        output_dir / 'revenue_profitability.csv'
    )
    print("  ✓ revenue_profitability.csv")
    
    populate_valuation_multiples(
        financials,
        market_data,
        output_dir / 'valuation_multiples.csv'
    )
    print("  ✓ valuation_multiples.csv")
    
    populate_operating_metrics(
        financials,
        output_dir / 'operating_metrics.csv'
    )
    print("  ✓ operating_metrics.csv")
    
    populate_growth_metrics(
        financials,
        output_dir / 'growth_metrics.csv'
    )
    print("  ✓ growth_metrics.csv")
    
    print("\n✅ All comps tables populated successfully!")
    print("\nNext step: Run 'python3 scripts/csv_to_latex.py --all' to convert to LaTeX")

if __name__ == '__main__':
    main()

