#!/usr/bin/env python3
"""
Create comprehensive expectation metrics table for section 1.3.
Includes: P/E, P/B, EV/Revenue, EV/EBITDA, Market Cap/Revenue, P/CF, P/FCF
"""

import json
import csv
from pathlib import Path

def load_financial_data():
    """Load financial data."""
    data_path = Path(__file__).parent.parent / 'data' / 'master_financials.json'
    with open(data_path, 'r') as f:
        return json.load(f)

def load_market_data():
    """Load market data."""
    market_path = Path(__file__).parent.parent / 'tables' / 'csv' / 'comps' / 'market_performance.csv'
    market_data = {}
    
    with open(market_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            metric = row['Metric']
            market_data[metric] = {
                'NVDA': row['NVDA'],
                'INTC': row['INTC'],
                'AMD': row['AMD'],
                'MCHP': row['MCHP'],
                'LSCC': row['LSCC']
            }
    
    return market_data

def parse_value(value_str):
    """Parse value from string, handling commas and N/A."""
    if value_str == 'N/A' or value_str == '':
        return None
    try:
        return float(value_str.replace(',', ''))
    except:
        return None

def estimate_operating_cash_flow(net_income, revenue, operating_income, has_ocf=None):
    """Estimate Operating Cash Flow if not available."""
    if has_ocf is not None:
        return has_ocf
    
    estimated_da = revenue * 0.03  # 3% of revenue
    
    if net_income > 0:
        ocf = net_income + estimated_da
        ocf = ocf * 0.90  # Adjust for working capital
    else:
        if operating_income > -revenue * 0.10:
            ocf = operating_income + estimated_da
        else:
            ocf = max(operating_income + estimated_da, revenue * 0.02)
    
    return max(ocf, revenue * 0.02)

def calculate_free_cash_flow(operating_cash_flow, revenue, has_fcf=None):
    """Estimate Free Cash Flow."""
    if has_fcf is not None:
        return has_fcf
    
    estimated_capex = revenue * 0.09  # 9% of revenue
    fcf = operating_cash_flow - estimated_capex
    return fcf

def main():
    """Create expectation metrics table."""
    financials = load_financial_data()
    market_data = load_market_data()
    
    companies = ['NVDA', 'INTC', 'AMD', 'MCHP', 'LSCC']
    
    # Get market cap values
    market_caps = {}
    for ticker in companies:
        mc_str = market_data['Market Cap ($B)'][ticker]
        market_caps[ticker] = parse_value(mc_str.replace('"', '')) * 1e9
    
    # Get EV values
    ev_values = {}
    for ticker in companies:
        ev_str = market_data['Enterprise Value ($B)'][ticker]
        ev_values[ticker] = parse_value(ev_str.replace('"', '')) * 1e9
    
    # Calculate cash flows
    cash_flows = {}
    for ticker in companies:
        data = financials[ticker]
        ocf = data.get('operating_cash_flow')
        if ocf is None:
            ocf = estimate_operating_cash_flow(
                data['net_income'], 
                data['revenue'], 
                data['operating_income']
            )
        fcf = data.get('free_cash_flow')
        if fcf is None:
            fcf = calculate_free_cash_flow(ocf, data['revenue'])
        cash_flows[ticker] = {'ocf': ocf, 'fcf': fcf}
    
    # Create table data
    rows = []
    for ticker in companies:
        data = financials[ticker]
        mc = market_caps[ticker]
        ev = ev_values[ticker]
        revenue = data['revenue']
        net_income = data['net_income']
        ebitda = data.get('ebitda') or (data['operating_income'] + revenue * 0.03)  # Estimate EBITDA
        ebit = data['ebit']
        ocf = cash_flows[ticker]['ocf']
        fcf = cash_flows[ticker]['fcf']
        
        # Get P/E and P/B from market_data (use existing calculated values)
        pe_str = market_data['P/E Ratio'][ticker]
        pe = parse_value(pe_str.replace('"', ''))
        
        pb_str = market_data['P/B Ratio'][ticker]
        pb = parse_value(pb_str.replace('"', ''))
        
        # Calculate other multiples
        ev_revenue = ev / revenue if revenue > 0 else None
        ev_ebitda = ev / ebitda if ebitda > 0 else None
        mc_revenue = mc / revenue if revenue > 0 else None
        p_cf = mc / ocf if ocf > 0 else None
        p_fcf = mc / fcf if fcf > 0 else None
        
        rows.append({
            'ticker': ticker,
            'pe': pe,
            'pb': pb,
            'ev_revenue': ev_revenue,
            'ev_ebitda': ev_ebitda,
            'mc_revenue': mc_revenue,
            'p_cf': p_cf,
            'p_fcf': p_fcf
        })
    
    # Create LaTeX table
    tex_output_dir = Path(__file__).parent.parent / 'tables' / 'tex' / 'comps'
    tex_output_dir.mkdir(parents=True, exist_ok=True)
    tex_output_path = tex_output_dir / 'expectation_metrics.tex'
    
    tex_content = """\\begin{table}[H]
\\centering
\\caption{Valuation Multiples - Market Expectations}
\\resizebox{\\textwidth}{!}{%
\\begin{tabular}{llrrrrrr}
\\toprule
Company & P/E & P/B & Market Cap/Revenue & EV/Revenue & EV/EBITDA & P/CF & P/FCF \\\\
 & (x) & (x) & (x) & (x) & (x) & (x) & (x) \\\\
\\midrule
"""
    
    for r in rows:
        tex_content += f"{r['ticker']} & "
        tex_content += f"{r['pe']:.1f}x & " if r['pe'] else "N/A & "
        tex_content += f"{r['pb']:.2f}x & " if r['pb'] else "N/A & "
        tex_content += f"{r['mc_revenue']:.2f}x & " if r['mc_revenue'] else "N/A & "
        tex_content += f"{r['ev_revenue']:.2f}x & " if r['ev_revenue'] else "N/A & "
        tex_content += f"{r['ev_ebitda']:.1f}x & " if r['ev_ebitda'] else "N/A & "
        tex_content += f"{r['p_cf']:.1f}x & " if r['p_cf'] else "N/A & "
        tex_content += f"{r['p_fcf']:.1f}x \\\\\n" if r['p_fcf'] else "N/A \\\\\n"
    
    tex_content += """\\midrule
\\multicolumn{8}{l}{\\textit{P/E = Price-to-Earnings; P/B = Price-to-Book; P/CF = Price-to-Cash Flow; P/FCF = Price-to-Free Cash Flow}} \\\\
\\bottomrule
\\end{tabular}%
}
\\end{table}
"""
    
    with open(tex_output_path, 'w', encoding='utf-8') as f:
        f.write(tex_content)
    
    print(f"✓ Created {tex_output_path}")
    
    # Also create CSV
    csv_output_dir = Path(__file__).parent.parent / 'tables' / 'csv' / 'comps'
    csv_output_dir.mkdir(parents=True, exist_ok=True)
    csv_output_path = csv_output_dir / 'expectation_metrics.csv'
    
    headers = ['Company', 'P/E (x)', 'P/B (x)', 'Market Cap/Revenue (x)', 
               'EV/Revenue (x)', 'EV/EBITDA (x)', 'P/CF (x)', 'P/FCF (x)']
    
    csv_rows = []
    for r in rows:
        csv_rows.append([
            r['ticker'],
            f"{r['pe']:.1f}x" if r['pe'] else "N/A",
            f"{r['pb']:.2f}x" if r['pb'] else "N/A",
            f"{r['mc_revenue']:.2f}x" if r['mc_revenue'] else "N/A",
            f"{r['ev_revenue']:.2f}x" if r['ev_revenue'] else "N/A",
            f"{r['ev_ebitda']:.1f}x" if r['ev_ebitda'] else "N/A",
            f"{r['p_cf']:.1f}x" if r['p_cf'] else "N/A",
            f"{r['p_fcf']:.1f}x" if r['p_fcf'] else "N/A"
        ])
    
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(csv_rows)
    
    print(f"✓ Created {csv_output_path}")
    
    print("\nTable includes:")
    print("  - P/E (Price-to-Earnings): Earnings expectations")
    print("  - P/B (Price-to-Book): Asset value expectations")
    print("  - Market Cap/Revenue: Revenue growth expectations")
    print("  - EV/Revenue: Enterprise value relative to revenue")
    print("  - EV/EBITDA: Cash flow generation expectations")
    print("  - P/CF (Price-to-Cash Flow): Operating cash flow expectations")
    print("  - P/FCF (Price-to-Free Cash Flow): Free cash flow expectations")

if __name__ == '__main__':
    main()

