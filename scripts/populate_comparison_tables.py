#!/usr/bin/env python3
"""
Populate Comparison Tables from Master Financial Data

This script reads from master_financial_data.csv and generates
individual comparison tables for the analysis.

Run this after extract_10k_data.py to generate formatted comparison tables.
"""

import csv
from pathlib import Path
from typing import Dict, Optional

def parse_float(value: str) -> Optional[float]:
    """Parse a float from string, handling empty values."""
    if not value or value.strip() == '':
        return None
    try:
        return float(value)
    except ValueError:
        return None

def format_currency(value: Optional[float], in_millions: bool = True) -> str:
    """Format a currency value for display."""
    if value is None:
        return ''
    
    if in_millions:
        value = value / 1_000_000
        return f"${value:,.2f}M"
    else:
        return f"${value:,.0f}"

def format_percent(value: Optional[float]) -> str:
    """Format a percentage value."""
    if value is None:
        return ''
    return f"{value:.2f}%"

def load_master_data(master_path: Path) -> Dict[str, Dict[str, str]]:
    """Load master financial data."""
    if not master_path.exists():
        print(f"Error: Master table not found: {master_path}")
        print("Run extract_10k_data.py first to create the master table.")
        return {}
    
    companies_data = {}
    with open(master_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies_data[row['Company']] = row
    
    return companies_data

def populate_revenue_profitability(master_data: Dict, output_path: Path):
    """Generate revenue and profitability comparison table."""
    headers = ['Company', 'Revenue', 'EBITDA', 'EBITDA Margin', 'Net Income', 'Net Margin']
    rows = []
    
    # Filter to comps companies only (exclude Lattice for comps)
    comps_companies = ['NVIDIA (NVDA)', 'AMD', 'Microchip (MCHP)', 'TSMC']
    
    for company in comps_companies:
        if company not in master_data:
            continue
        
        data = master_data[company]
        row = [company]
        
        # Revenue
        revenue = parse_float(data.get('Revenue', ''))
        row.append(format_currency(revenue))
        
        # EBITDA
        ebitda = parse_float(data.get('EBITDA', ''))
        row.append(format_currency(ebitda))
        
        # EBITDA Margin
        ebitda_margin = parse_float(data.get('EBITDA_Margin_Pct', ''))
        if ebitda_margin is None and ebitda and revenue:
            ebitda_margin = (ebitda / revenue) * 100
        row.append(format_percent(ebitda_margin))
        
        # Net Income
        net_income = parse_float(data.get('Net_Income', ''))
        row.append(format_currency(net_income))
        
        # Net Margin
        net_margin = parse_float(data.get('Net_Margin_Pct', ''))
        if net_margin is None and net_income and revenue:
            net_margin = (net_income / revenue) * 100
        row.append(format_percent(net_margin))
        
        rows.append(row)
    
    # Write CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"  ✓ Generated {output_path.name}")

def populate_operating_metrics(master_data: Dict, output_path: Path):
    """Generate operating metrics comparison table."""
    headers = ['Company', 'R&D / Revenue', 'Gross Margin', 'ROE', 'ROIC']
    rows = []
    
    comps_companies = ['NVIDIA (NVDA)', 'AMD', 'Microchip (MCHP)', 'TSMC']
    
    for company in comps_companies:
        if company not in master_data:
            continue
        
        data = master_data[company]
        row = [company]
        
        # R&D / Revenue
        rd_pct = parse_float(data.get('R_D_Pct_Revenue', ''))
        row.append(format_percent(rd_pct))
        
        # Gross Margin
        gross_margin = parse_float(data.get('Gross_Margin_Pct', ''))
        row.append(format_percent(gross_margin))
        
        # ROE (Return on Equity) = Net Income / Total Equity
        net_income = parse_float(data.get('Net_Income', ''))
        total_equity = parse_float(data.get('Total_Equity', ''))
        roe = None
        if net_income and total_equity and total_equity != 0:
            roe = (net_income / total_equity) * 100
        row.append(format_percent(roe))
        
        # ROIC (Return on Invested Capital) = EBIT / (Total Debt + Total Equity)
        ebit = parse_float(data.get('EBIT', ''))
        total_debt = parse_float(data.get('Total_Debt', ''))
        roic = None
        if ebit and total_debt is not None and total_equity is not None:
            invested_capital = (total_debt or 0) + (total_equity or 0)
            if invested_capital != 0:
                roic = (ebit / invested_capital) * 100
        row.append(format_percent(roic))
        
        rows.append(row)
    
    # Write CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"  ✓ Generated {output_path.name}")

def populate_market_cap_ev(master_data: Dict, output_path: Path):
    """Generate market cap and enterprise value table."""
    headers = ['Company', 'Market Cap', 'Enterprise Value', 'Cash & Equiv.', 'Net Debt']
    rows = []
    
    comps_companies = ['NVIDIA (NVDA)', 'AMD', 'Microchip (MCHP)', 'TSMC']
    
    for company in comps_companies:
        if company not in master_data:
            continue
        
        data = master_data[company]
        row = [company]
        
        # Market Cap - needs to be added manually (not in 10-K)
        market_cap = parse_float(data.get('Market_Cap', ''))
        row.append(format_currency(market_cap) if market_cap else '')
        
        # Enterprise Value - needs to be added manually or calculated
        ev = parse_float(data.get('Enterprise_Value', ''))
        row.append(format_currency(ev) if ev else '')
        
        # Cash & Equivalents
        cash = parse_float(data.get('Cash', ''))
        row.append(format_currency(cash))
        
        # Net Debt
        net_debt = parse_float(data.get('Net_Debt', ''))
        if net_debt is None:
            total_debt = parse_float(data.get('Total_Debt', ''))
            if cash and total_debt:
                net_debt = total_debt - cash
        row.append(format_currency(net_debt))
        
        rows.append(row)
    
    # Write CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"  ✓ Generated {output_path.name}")

def populate_valuation_multiples(master_data: Dict, output_path: Path):
    """Generate valuation multiples table."""
    headers = ['Company', 'EV/Revenue', 'EV/EBITDA', 'P/E', 'P/B', 'EV/EBIT']
    rows = []
    
    comps_companies = ['NVIDIA (NVDA)', 'AMD', 'Microchip (MCHP)', 'TSMC']
    
    for company in comps_companies:
        if company not in master_data:
            continue
        
        data = master_data[company]
        row = [company]
        
        ev = parse_float(data.get('Enterprise_Value', ''))
        revenue = parse_float(data.get('Revenue', ''))
        ebitda = parse_float(data.get('EBITDA', ''))
        ebit = parse_float(data.get('EBIT', ''))
        market_cap = parse_float(data.get('Market_Cap', ''))
        net_income = parse_float(data.get('Net_Income', ''))
        total_equity = parse_float(data.get('Total_Equity', ''))
        shares = parse_float(data.get('Shares_Outstanding', ''))
        
        # EV/Revenue
        ev_revenue = None
        if ev and revenue and revenue != 0:
            ev_revenue = ev / revenue
        row.append(f"{ev_revenue:.2f}x" if ev_revenue else '')
        
        # EV/EBITDA
        ev_ebitda = None
        if ev and ebitda and ebitda != 0:
            ev_ebitda = ev / ebitda
        row.append(f"{ev_ebitda:.2f}x" if ev_ebitda else '')
        
        # P/E (Price to Earnings) = Market Cap / Net Income
        pe = None
        if market_cap and net_income and net_income != 0:
            pe = market_cap / net_income
        row.append(f"{pe:.2f}x" if pe else '')
        
        # P/B (Price to Book) = Market Cap / Total Equity
        pb = None
        if market_cap and total_equity and total_equity != 0:
            pb = market_cap / total_equity
        row.append(f"{pb:.2f}x" if pb else '')
        
        # EV/EBIT
        ev_ebit = None
        if ev and ebit and ebit != 0:
            ev_ebit = ev / ebit
        row.append(f"{ev_ebit:.2f}x" if ev_ebit else '')
        
        rows.append(row)
    
    # Write CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"  ✓ Generated {output_path.name}")

def populate_growth_metrics(master_data: Dict, output_path: Path):
    """Generate growth metrics table (requires historical data)."""
    headers = ['Company', 'Revenue CAGR (3Y)', 'EBITDA CAGR (3Y)', 'Revenue Growth (YoY)']
    rows = []
    
    comps_companies = ['NVIDIA (NVDA)', 'AMD', 'Microchip (MCHP)', 'TSMC']
    
    for company in comps_companies:
        if company not in master_data:
            continue
        
        data = master_data[company]
        row = [company]
        
        # These require historical data (multiple years)
        # For now, leave empty - user can fill manually
        row.append('')  # Revenue CAGR (3Y)
        row.append('')  # EBITDA CAGR (3Y)
        row.append('')  # Revenue Growth (YoY)
        
        rows.append(row)
    
    # Write CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"  ✓ Generated {output_path.name}")

def main():
    """Main function to populate all comparison tables."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tables_dir = project_root / 'tables' / 'csv'
    master_path = tables_dir / 'master_financial_data.csv'
    comps_dir = tables_dir / 'comps'
    
    # Ensure directories exist
    comps_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Populate Comparison Tables from Master Data")
    print("=" * 60)
    print(f"Master table: {master_path}\n")
    
    # Load master data
    master_data = load_master_data(master_path)
    
    if not master_data:
        print("No data found. Exiting.")
        return
    
    print(f"Loaded data for {len(master_data)} companies\n")
    
    # Generate comparison tables
    populate_revenue_profitability(master_data, comps_dir / 'revenue_profitability.csv')
    populate_operating_metrics(master_data, comps_dir / 'operating_metrics.csv')
    populate_market_cap_ev(master_data, comps_dir / 'market_cap_ev.csv')
    populate_valuation_multiples(master_data, comps_dir / 'valuation_multiples.csv')
    populate_growth_metrics(master_data, comps_dir / 'growth_metrics.csv')
    
    print("\n" + "=" * 60)
    print("Comparison tables generated!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review generated tables in tables/csv/comps/")
    print("2. Manually add Market Cap and Enterprise Value to master_financial_data.csv")
    print("3. Re-run this script to update comparison tables with market data")
    print("4. Add historical data for growth metrics if available")
    print("5. Run: python scripts/csv_to_latex.py --all")

if __name__ == '__main__':
    main()

