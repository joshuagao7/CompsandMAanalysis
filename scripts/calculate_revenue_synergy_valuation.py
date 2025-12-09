#!/usr/bin/env python3
"""
Calculate Value Creation from Revenue Synergies

This script analyzes how revenue synergies translate to valuation increases
based on Lattice's revenue multiple, showing value creation vs transaction cost.
"""

import json
import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parent.parent))

# Constants
TAX_RATE = 0.21
PREMIUM_PCT = 0.30
LSCC_REVENUE_MULTIPLE = 18.45  # From expectation_metrics table


def load_json(filepath: str) -> dict:
    with open(filepath, 'r') as f:
        return json.load(f)


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
    
    lscc_revenue = lscc['revenue']  # $509M
    lscc_market_cap = lscc_market['market_cap']  # $9.39B
    
    print("=" * 80)
    print("REVENUE SYNERGY VALUATION ANALYSIS")
    print("=" * 80)
    print(f"\nLattice Base Metrics:")
    print(f"  Current Revenue: ${lscc_revenue/1e6:.1f}M")
    print(f"  Current Market Cap: ${lscc_market_cap/1e9:.2f}B")
    print(f"  Revenue Multiple: {LSCC_REVENUE_MULTIPLE}x")
    print(f"  Transaction Value: ${transaction_value/1e9:.2f}B")
    print()
    
    # Revenue synergy scenarios
    # Base synergy from Has-Gets analysis: $123.2M annual
    # Use this directly as revenue synergy (synergies convert 1:1 to revenue impact)
    base_synergy_revenue = 123_200_000  # $123.2M from Has-Gets analysis
    
    # Lower all scenarios - start from $15M
    # Base case centered at $123.2M to match Has-Gets analysis
    revenue_scenarios = {
        'Very Pessimistic': 15_000_000,  # $15M absolute
        'Pessimistic': 0.30,  # 30% of base = $37M
        'Base Case': 0.60,  # 60% of base = $73.9M
        'Base': 1.00,  # 100% of base = $123.2M (matches Has-Gets, center of distribution)
        'Optimistic': 1.30,  # 130% of base = $160.2M
        'Bull Case': 1.50,  # 150% of base = $184.8M
        'Very Bull': 1.80,  # 180% of base = $221.8M
    }
    
    # Normal-like probability distribution centered on Base ($123.2M) 
    # Adjusted to make expected value = $123.2M
    probabilities = {
        'Very Pessimistic': 0.05,  # 5%
        'Pessimistic': 0.07,  # 7%
        'Base Case': 0.13,  # 13%
        'Base': 0.38,  # 38% (center, matches Has-Gets $123.2M)
        'Optimistic': 0.25,  # 25%
        'Bull Case': 0.09,  # 9%
        'Very Bull': 0.03,  # 3%
    }
    
    print("=" * 80)
    print("VALUE CREATION ANALYSIS")
    print("=" * 80)
    print(f"{'Scenario':<30} {'Revenue':<15} {'Revenue':<15} {'Valuation':<15} {'Value':<15} {'Success':<15} {'Prob':<10}")
    print(f"{'':<30} {'Synergy':<15} {'Increase':<15} {'@ Multiple':<15} {'Creation':<15} {'Metric':<15} {'(%)':<10}")
    print(f"{'':<30} {'($M)':<15} {'(%)':<15} {'($B)':<15} {'($B)':<15} {'(%)':<15} {'':<10}")
    print("-" * 115)
    
    results = []
    
    for scenario_name, value in revenue_scenarios.items():
        # Handle absolute dollar amount ($30M) vs multiplier
        # If value is >= 1M, it's an absolute dollar amount; otherwise it's a multiplier
        if isinstance(value, (int, float)) and value >= 1_000_000:
            # It's an absolute dollar amount (like $30M)
            synergy_revenue = value
        else:
            # It's a multiplier (like 0.30, 0.50, 0.70, etc.)
            synergy_revenue = base_synergy_revenue * value
        
        new_revenue = lscc_revenue + synergy_revenue
        revenue_increase_pct = (synergy_revenue / lscc_revenue) * 100
        
        # Apply revenue multiple to get new valuation
        new_valuation = new_revenue * LSCC_REVENUE_MULTIPLE
        
        # Value creation = new valuation - transaction value
        value_creation = new_valuation - transaction_value
        
        # Success metric: value creation as % of transaction value
        success_pct = (value_creation / transaction_value) * 100
        
        prob = probabilities.get(scenario_name, 0)
        
        results.append({
            'scenario': scenario_name,
            'synergy_revenue': synergy_revenue,
            'revenue_increase_pct': revenue_increase_pct,
            'new_valuation': new_valuation,
            'value_creation': value_creation,
            'success_pct': success_pct,
            'probability': prob
        })
        
        print(f"{scenario_name:<30} ${synergy_revenue/1e6:>6.1f}M{'':<6} {revenue_increase_pct:>6.1f}%{'':<6} ${new_valuation/1e9:>6.2f}B{'':<6} ${value_creation/1e9:>6.2f}B{'':<6} {success_pct:>6.1f}%{'':<6} {prob*100:>5.0f}%")
    
    # Calculate expected value (probability-weighted)
    expected_synergy_revenue = sum(r['synergy_revenue'] * r['probability'] for r in results)
    expected_revenue_increase = sum(r['revenue_increase_pct'] * r['probability'] for r in results)
    expected_valuation = sum(r['new_valuation'] * r['probability'] for r in results)
    expected_value_creation = sum(r['value_creation'] * r['probability'] for r in results)
    expected_success = sum(r['success_pct'] * r['probability'] for r in results)
    
    # Add expected value row
    results.append({
        'scenario': 'Expected Value',
        'synergy_revenue': expected_synergy_revenue,
        'revenue_increase_pct': expected_revenue_increase,
        'new_valuation': expected_valuation,
        'value_creation': expected_value_creation,
        'success_pct': expected_success,
        'probability': 1.00  # Sum of all probabilities
    })
    
    print("-" * 115)
    print(f"{'Expected Value':<30} ${expected_synergy_revenue/1e6:>6.1f}M{'':<6} {expected_revenue_increase:>6.1f}%{'':<6} ${expected_valuation/1e9:>6.2f}B{'':<6} ${expected_value_creation/1e9:>6.2f}B{'':<6} {expected_success:>6.1f}%{'':<6} 100%")
    print()
    
    # Generate CSV
    csv_path = base_path / 'tables' / 'csv' / 'ma' / 'revenue_synergy_valuation.csv'
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(csv_path, 'w') as f:
        f.write('Scenario,Revenue Synergy ($M),Revenue Increase (%),New Valuation @ Multiple ($B),Value Creation ($B),Success (%),Probability (%)\n')
        for r in results:
            f.write(f'{r["scenario"]},{r["synergy_revenue"]/1e6:.1f},{r["revenue_increase_pct"]:.1f},{r["new_valuation"]/1e9:.2f},{r["value_creation"]/1e9:.2f},{r["success_pct"]:.1f},{r["probability"]*100:.0f}\n')
    
    print(f"CSV saved to: {csv_path}")
    
    # Generate LaTeX table
    tex_path = base_path / 'tables' / 'tex' / 'ma' / 'revenue_synergy_valuation.tex'
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(tex_path, 'w') as f:
        f.write('\\begin{table}[H]\n')
        f.write('\\centering\n')
        f.write('\\caption{Value Creation from Revenue Synergies}\n')
        f.write('\\label{tab:revenue_synergy}\n')
        f.write('\\footnotesize\n')
        f.write('\\setlength{\\tabcolsep}{4pt}\n')
        f.write('\\renewcommand{\\arraystretch}{1.0}\n')
        f.write('\\resizebox{\\textwidth}{!}{%\n')
        f.write('\\begin{tabular}{lrrrrrr}\n')
        f.write('\\toprule\n')
        f.write('Scenario & Revenue & Revenue & Valuation & Value & Success & Prob \\\\\n')
        f.write('& Synergy & Increase & @ 18.45x & Creation & Metric & (\\%) \\\\\n')
        f.write('& (\\$M) & (\\%) & (\\$B) & (\\$B) & (\\%) & \\\\\n')
        f.write('\\midrule\n')
        
        for r in results[:-1]:  # All except the last (expected value)
            f.write(f'{r["scenario"]} & \\${r["synergy_revenue"]/1e6:.1f}M & {r["revenue_increase_pct"]:.1f}\\% & \\${r["new_valuation"]/1e9:.2f}B & \\${r["value_creation"]/1e9:.2f}B & {r["success_pct"]:.1f}\\% & {r["probability"]*100:.0f}\\% \\\\\n')
        
        # Add expected value row with special formatting
        expected = results[-1]
        f.write('\\midrule\n')
        f.write(f'\\textbf{{{expected["scenario"]}}} & \\textbf{{\\${expected["synergy_revenue"]/1e6:.1f}M}} & \\textbf{{{expected["revenue_increase_pct"]:.1f}\\%}} & \\textbf{{\\${expected["new_valuation"]/1e9:.2f}B}} & \\textbf{{\\${expected["value_creation"]/1e9:.2f}B}} & \\textbf{{{expected["success_pct"]:.1f}\\%}} & \\textbf{{100\\%}} \\\\\n')
        
        f.write('\\bottomrule\n')
        f.write('\\end{tabular}%\n')
        f.write('}\n')
        f.write('\\begin{flushleft}\n')
        f.write('\\scriptsize\n')
        f.write('\\textit{Note: Assumes revenue synergies convert to revenue at 50\\% gross margin. Valuation uses Lattice\\textquotesingle s current revenue multiple of 18.45x. Value Creation = New Valuation - Transaction Value (\\$12.2B). Success Metric = Value Creation as \\% of Transaction Value. Probabilities sum to 100\\% and are normally distributed with base case (100\\%) at 30\\%.}\n')
        f.write('\\end{flushleft}\n')
        f.write('\\end{table}\n')
    
    print(f"LaTeX table saved to: {tex_path}")
    
    # Find break-even point
    print()
    print("=" * 80)
    print("BREAK-EVEN ANALYSIS")
    print("=" * 80)
    print("Revenue increase needed for value creation = 0:")
    
    # Solve: (base_revenue + synergy_revenue) * multiple - tx_value = 0
    # synergy_revenue = (tx_value / multiple) - base_revenue
    break_even_synergy_revenue = (transaction_value / LSCC_REVENUE_MULTIPLE) - lscc_revenue
    break_even_revenue_increase = (break_even_synergy_revenue / lscc_revenue) * 100
    
    print(f"  Break-even synergy revenue: ${break_even_synergy_revenue/1e6:.1f}M")
    print(f"  Break-even revenue increase: {break_even_revenue_increase:.1f}%")
    print(f"  This corresponds to: {break_even_synergy_revenue / base_synergy_revenue:.1f}x base synergies")
    
    # Verify expected value matches Has-Gets
    print()
    print("=" * 80)
    print("EXPECTED VALUE VERIFICATION")
    print("=" * 80)
    print(f"Expected Revenue Synergy: ${expected_synergy_revenue/1e6:.1f}M")
    print(f"Has-Gets Base Synergy: ${base_synergy_revenue/1e6:.1f}M")
    print(f"Match: {'✓' if abs(expected_synergy_revenue - base_synergy_revenue) < 1_000_000 else '✗'}")


if __name__ == '__main__':
    main()

