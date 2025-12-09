#!/usr/bin/env python3
"""
Calculate cash flow metrics and Price-to-Cash Flow multiples.
P/CF = Market Cap / Operating Cash Flow (measures cash flow expectations)
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
    """Load market cap data."""
    market_path = Path(__file__).parent.parent / 'tables' / 'csv' / 'comps' / 'market_performance.csv'
    market_caps = {}
    
    with open(market_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Metric'] == 'Market Cap ($B)':
                market_caps['NVDA'] = float(row['NVDA'].replace(',', '')) * 1e9
                market_caps['INTC'] = float(row['INTC']) * 1e9
                market_caps['AMD'] = float(row['AMD']) * 1e9
                market_caps['MCHP'] = float(row['MCHP']) * 1e9
                market_caps['LSCC'] = float(row['LSCC']) * 1e9
                break
    
    return market_caps

def estimate_operating_cash_flow(net_income, revenue, operating_income, has_ocf=None):
    """
    Estimate Operating Cash Flow if not available.
    OCF ≈ Net Income + D&A + Non-cash items - Changes in Working Capital
    
    Better estimation:
    - For profitable companies: OCF typically 1.1-1.3x Net Income (after D&A add-back)
    - D&A typically 2-4% of revenue for semiconductor companies
    """
    if has_ocf is not None:
        return has_ocf
    
    # Estimate D&A as 2.5-3.5% of revenue (typical for semiconductor companies)
    estimated_da = revenue * 0.03  # 3% of revenue
    
    if net_income > 0:
        # For profitable companies: OCF ≈ Net Income + D&A + adjustments
        # Add D&A back, and account for typical working capital changes
        # OCF is often 1.1-1.5x net income for growing companies
        ocf = net_income + estimated_da
        # Adjust for working capital (typically reduces OCF by 5-15% for growing companies)
        ocf = ocf * 0.90  # Assume 10% reduction for working capital
    else:
        # For unprofitable companies, OCF might be positive if D&A is high
        # OCF ≈ Operating Income + D&A (if operating income is negative but close to break-even)
        if operating_income > -revenue * 0.10:  # If losses are less than 10% of revenue
            ocf = operating_income + estimated_da
        else:
            # Large losses - OCF likely negative or very small
            ocf = max(operating_income + estimated_da, revenue * 0.02)
    
    return max(ocf, revenue * 0.02)  # Minimum 2% of revenue

def calculate_free_cash_flow(operating_cash_flow, revenue, has_fcf=None):
    """
    Estimate Free Cash Flow = Operating Cash Flow - CapEx
    CapEx typically 5-15% of revenue for semiconductor companies
    """
    if has_fcf is not None:
        return has_fcf
    
    # Estimate CapEx as 8-10% of revenue (typical for semiconductor companies)
    estimated_capex = revenue * 0.09  # 9% of revenue
    
    fcf = operating_cash_flow - estimated_capex
    return fcf

def main():
    """Calculate cash flow metrics."""
    financials = load_financial_data()
    market_caps = load_market_data()
    
    companies = ['NVDA', 'INTC', 'AMD', 'MCHP', 'LSCC']
    
    results = []
    
    print("Calculating Cash Flow Metrics...")
    print("=" * 80)
    
    for ticker in companies:
        data = financials[ticker]
        market_cap = market_caps[ticker]
        
        revenue = data['revenue']
        net_income = data['net_income']
        operating_income = data['operating_income']
        
        # Get or estimate operating cash flow
        ocf = data.get('operating_cash_flow')
        if ocf is None:
            ocf = estimate_operating_cash_flow(net_income, revenue, operating_income)
            estimated = True
        else:
            estimated = False
        
        # Get or estimate free cash flow
        fcf = data.get('free_cash_flow')
        if fcf is None:
            fcf = calculate_free_cash_flow(ocf, revenue)
            fcf_estimated = True
        else:
            fcf_estimated = False
        
        # Calculate multiples
        p_cf = market_cap / ocf if ocf > 0 else None
        p_fcf = market_cap / fcf if fcf > 0 else None
        
        # OCF Margin
        ocf_margin = (ocf / revenue) * 100 if revenue > 0 else None
        
        # FCF Margin
        fcf_margin = (fcf / revenue) * 100 if revenue > 0 else None
        
        results.append({
            'ticker': ticker,
            'company': data['company_info']['name'],
            'revenue_m': revenue / 1e6,
            'net_income_m': net_income / 1e6,
            'operating_cash_flow_m': ocf / 1e6,
            'free_cash_flow_m': fcf / 1e6,
            'market_cap_m': market_cap / 1e6,
            'p_cf': p_cf,
            'p_fcf': p_fcf,
            'ocf_margin': ocf_margin,
            'fcf_margin': fcf_margin,
            'ocf_estimated': estimated,
            'fcf_estimated': fcf_estimated
        })
        
        print(f"\n{ticker} ({data['company_info']['name']}):")
        print(f"  Operating Cash Flow: ${ocf/1e6:,.0f}M {'(estimated)' if estimated else ''}")
        print(f"  Free Cash Flow: ${fcf/1e6:,.0f}M {'(estimated)' if fcf_estimated else ''}")
        print(f"  Market Cap: ${market_cap/1e6:,.0f}M")
        if p_cf:
            print(f"  P/CF (Price-to-Cash Flow): {p_cf:.1f}x")
        if p_fcf:
            print(f"  P/FCF (Price-to-Free Cash Flow): {p_fcf:.1f}x")
        print(f"  OCF Margin: {ocf_margin:.1f}%" if ocf_margin else "  OCF Margin: N/A")
        print(f"  FCF Margin: {fcf_margin:.1f}%" if fcf_margin else "  FCF Margin: N/A")
    
    # Create CSV table
    output_dir = Path(__file__).parent.parent / 'tables' / 'csv' / 'comps'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'cash_flow_metrics.csv'
    
    headers = ['Company', 'Operating CF ($M)', 'Free CF ($M)', 'Market Cap ($M)', 
               'P/CF (x)', 'P/FCF (x)', 'OCF Margin (%)', 'FCF Margin (%)']
    
    rows = []
    for r in results:
        rows.append([
            r['ticker'],
            f"${r['operating_cash_flow_m']:,.0f}",
            f"${r['free_cash_flow_m']:,.0f}",
            f"${r['market_cap_m']:,.0f}",
            f"{r['p_cf']:.1f}x" if r['p_cf'] else "N/A",
            f"{r['p_fcf']:.1f}x" if r['p_fcf'] else "N/A",
            f"{r['ocf_margin']:.1f}%" if r['ocf_margin'] else "N/A",
            f"{r['fcf_margin']:.1f}%" if r['fcf_margin'] else "N/A"
        ])
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"\n✓ Created {output_path}")
    
    # Create LaTeX table
    tex_output_dir = Path(__file__).parent.parent / 'tables' / 'tex' / 'comps'
    tex_output_dir.mkdir(parents=True, exist_ok=True)
    tex_output_path = tex_output_dir / 'cash_flow_metrics.tex'
    
    tex_content = """\\begin{table}[H]
\\centering
\\caption{Cash Flow Metrics and Valuation Multiples}
\\resizebox{\\textwidth}{!}{%
\\begin{tabular}{llrrrr}
\\toprule
Company & Operating CF & Free CF & Market Cap & P/CF & P/FCF \\\\
 & (\\$M) & (\\$M) & (\\$M) & (x) & (x) \\\\
\\midrule
"""
    
    for r in results:
        company_name = r['ticker']
        tex_content += f"{company_name} & "
        tex_content += f"\\${r['operating_cash_flow_m']:,.0f} & "
        tex_content += f"\\${r['free_cash_flow_m']:,.0f} & "
        tex_content += f"\\${r['market_cap_m']:,.0f} & "
        tex_content += f"{r['p_cf']:.1f}x & " if r['p_cf'] else "N/A & "
        tex_content += f"{r['p_fcf']:.1f}x \\\\\n" if r['p_fcf'] else "N/A \\\\\n"
    
    tex_content += """\\midrule
\\multicolumn{6}{l}{\\textit{P/CF = Price-to-Cash Flow (Market Cap / Operating Cash Flow)}} \\\\
\\multicolumn{6}{l}{\\textit{P/FCF = Price-to-Free Cash Flow (Market Cap / Free Cash Flow)}} \\\\
\\bottomrule
\\end{tabular}%
}
\\end{table}
"""
    
    with open(tex_output_path, 'w', encoding='utf-8') as f:
        f.write(tex_content)
    
    print(f"✓ Created {tex_output_path}")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print("P/CF (Price-to-Cash Flow) measures market expectations for cash generation.")
    print("Higher multiples indicate market expects strong future cash flow growth.")
    print("\nKey Findings:")
    
    # Sort by P/CF
    sorted_results = sorted([r for r in results if r['p_cf']], key=lambda x: x['p_cf'], reverse=True)
    for r in sorted_results:
        print(f"  {r['ticker']}: P/CF = {r['p_cf']:.1f}x")

if __name__ == '__main__':
    main()

