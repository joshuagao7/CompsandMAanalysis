#!/usr/bin/env python3
"""
Create IRR Sensitivity Table for LaTeX

This script generates a CSV table showing IRR at different synergy levels,
which can be converted to LaTeX for the writeup.
"""

import json
import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parent.parent))

# Constants
TAX_RATE = 0.21
PREMIUM_PCT = 0.30
TERMINAL_MULTIPLE = 20.0
HOLDING_PERIOD = 7


def load_json(filepath: str) -> dict:
    with open(filepath, 'r') as f:
        return json.load(f)


def calculate_irr(cash_flows: List[float]) -> float:
    def npv(rate):
        return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
    
    try:
        low, high = -0.99, 10.0
        tolerance = 1e-6
        
        if npv(high) > 0:
            return None
        
        for _ in range(100):
            mid = (low + high) / 2
            npv_mid = npv(mid)
            
            if abs(npv_mid) < tolerance:
                return mid * 100
            
            if npv_mid > 0:
                low = mid
            else:
                high = mid
        
        return ((low + high) / 2) * 100
    except:
        return None


def find_transaction_value_for_irr(target_irr: float, annual_synergies: float, 
                                     lscc_fcf: float, lscc_ebitda: float) -> float:
    """Find transaction value that gives target IRR."""
    low, high = 1e9, 50e9  # Search between $1B and $50B
    
    for _ in range(100):
        test_value = (low + high) / 2
        
        cash_flows = [-test_value]
        for year in range(1, HOLDING_PERIOD + 1):
            base_growth = (1.03) ** (year - 1)
            synergy_growth = (1.05) ** (year - 1)
            after_tax_synergies = annual_synergies * (1 - TAX_RATE)
            cf_year = (lscc_fcf * base_growth) + (after_tax_synergies * synergy_growth)
            cash_flows.append(cf_year)
        
        final_year_growth = (1.05) ** (HOLDING_PERIOD - 1)
        terminal_ebitda = lscc_ebitda + (annual_synergies * final_year_growth)
        terminal_value = terminal_ebitda * TERMINAL_MULTIPLE
        cash_flows[-1] += terminal_value
        
        irr = calculate_irr(cash_flows)
        
        if irr is None:
            high = test_value
            continue
        
        if abs(irr/100 - target_irr) < 0.001:
            return test_value
        
        if irr/100 < target_irr:
            high = test_value
        else:
            low = test_value
    
    return (low + high) / 2


def main():
    base_path = Path(__file__).parent.parent
    financials_path = base_path / 'data' / 'master_financials.json'
    market_data_path = base_path / 'data' / 'market_data.json'
    
    financials = load_json(financials_path)
    market_data = load_json(market_data_path)
    
    lscc = financials['LSCC']
    lscc_market = market_data['LSCC']
    
    lscc_current_price = lscc_market['current_price']
    offer_price = lscc_current_price * (1 + PREMIUM_PCT)
    lscc_shares = lscc['shares_outstanding']
    transaction_value = offer_price * lscc_shares
    
    lscc_fcf = 23_000_000
    lscc_revenue = lscc['revenue']
    lscc_operating_income = lscc['operating_income']
    lscc_ebitda = lscc_operating_income + (lscc_revenue * 0.03)
    
    base_synergies = 123_200_000
    
    synergy_scenarios = {
        'Pessimistic (50\%)': 0.50,
        'Base Case (75\%)': 0.75,
        'Base (100\%)': 1.00,
        'Optimistic (125\%)': 1.25,
        'Bull Case (150\%)': 1.50,
        'Very Bull (200\%)': 2.00,
    }
    
    # Generate CSV
    csv_path = base_path / 'tables' / 'csv' / 'ma' / 'irr_sensitivity.csv'
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(csv_path, 'w') as f:
        f.write('Scenario,Annual Synergies ($M),IRR (%),NPV @ 10% ($B),Transaction Value for 10% IRR ($B)\n')
        
        for scenario_name, multiplier in synergy_scenarios.items():
            annual_synergies = base_synergies * multiplier
            after_tax_synergies = annual_synergies * (1 - TAX_RATE)
            
            cash_flows = [-transaction_value]
            for year in range(1, HOLDING_PERIOD + 1):
                base_growth = (1.03) ** (year - 1)
                synergy_growth = (1.05) ** (year - 1)
                cf_year = (lscc_fcf * base_growth) + (after_tax_synergies * synergy_growth)
                cash_flows.append(cf_year)
            
            final_year_growth = (1.05) ** (HOLDING_PERIOD - 1)
            terminal_ebitda = lscc_ebitda + (annual_synergies * final_year_growth)
            terminal_value = terminal_ebitda * TERMINAL_MULTIPLE
            cash_flows[-1] += terminal_value
            
            irr = calculate_irr(cash_flows)
            npv = sum(cf / (1.10) ** i for i, cf in enumerate(cash_flows))
            
            # Find transaction value for 10% IRR
            tx_value_10pct = find_transaction_value_for_irr(0.10, annual_synergies, 
                                                           lscc_fcf, lscc_ebitda)
            
            irr_str = f"{irr:.1f}" if irr else "N/A"
            f.write(f'{scenario_name},{annual_synergies/1e6:.1f},{irr_str},{npv/1e9:.2f},{tx_value_10pct/1e9:.2f}\n')
    
    print(f"IRR sensitivity table saved to: {csv_path}")
    
    # Also create LaTeX table
    tex_path = base_path / 'tables' / 'tex' / 'ma' / 'irr_sensitivity.tex'
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(tex_path, 'w') as f:
        f.write('\\begin{table}[H]\n')
        f.write('\\centering\n')
        f.write('\\caption{IRR Sensitivity Analysis: Synergy Scenarios}\n')
        f.write('\\label{tab:irr_sensitivity}\n')
        f.write('\\footnotesize\n')
        f.write('\\setlength{\\tabcolsep}{4pt}\n')
        f.write('\\renewcommand{\\arraystretch}{1.0}\n')
        f.write('\\resizebox{\\textwidth}{!}{%\n')
        f.write('\\begin{tabular}{lrrrr}\n')
        f.write('\\toprule\n')
        f.write('Scenario & Annual Synergies & IRR & NPV @ 10\\% & Tx Value for \\\\\n')
        f.write('& (\\$M) & (\\%) & (\\$B) & 10\\% IRR (\\$B) \\\\\n')
        f.write('\\midrule\n')
        
        for scenario_name, multiplier in synergy_scenarios.items():
            annual_synergies = base_synergies * multiplier
            after_tax_synergies = annual_synergies * (1 - TAX_RATE)
            
            cash_flows = [-transaction_value]
            for year in range(1, HOLDING_PERIOD + 1):
                base_growth = (1.03) ** (year - 1)
                synergy_growth = (1.05) ** (year - 1)
                cf_year = (lscc_fcf * base_growth) + (after_tax_synergies * synergy_growth)
                cash_flows.append(cf_year)
            
            final_year_growth = (1.05) ** (HOLDING_PERIOD - 1)
            terminal_ebitda = lscc_ebitda + (annual_synergies * final_year_growth)
            terminal_value = terminal_ebitda * TERMINAL_MULTIPLE
            cash_flows[-1] += terminal_value
            
            irr = calculate_irr(cash_flows)
            npv = sum(cf / (1.10) ** i for i, cf in enumerate(cash_flows))
            tx_value_10pct = find_transaction_value_for_irr(0.10, annual_synergies, 
                                                           lscc_fcf, lscc_ebitda)
            
            irr_str = f"{irr:.1f}\\%" if irr else "N/A"
            f.write(f'{scenario_name} & ${annual_synergies/1e6:.1f}M & {irr_str} & ${npv/1e9:.2f}B & ${tx_value_10pct/1e9:.2f}B \\\\\n')
        
        f.write('\\bottomrule\n')
        f.write('\\end{tabular}%\n')
        f.write('}\n')
        f.write('\\begin{flushleft}\n')
        f.write('\\scriptsize\n')
        f.write('\\textit{Note: Assumes 7-year holding period, 20x terminal EBITDA multiple, 3\\% base FCF growth, 5\\% synergy growth. Transaction value: \\$12.2B. Negative IRRs indicate strategic acquisition where financial returns are secondary to strategic value.}\n')
        f.write('\\end{flushleft}\n')
        f.write('\\end{table}\n')
    
    print(f"LaTeX table saved to: {tex_path}")


if __name__ == '__main__':
    main()

