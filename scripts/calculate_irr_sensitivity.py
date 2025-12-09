#!/usr/bin/env python3
"""
Calculate IRR Sensitivity Analysis for NVIDIA-Lattice Acquisition

This script calculates IRR at different synergy levels to show probabilistic thinking
and sensitivity to synergy assumptions.
"""

import json
import sys
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Constants
TAX_RATE = 0.21  # Corporate tax rate
PREMIUM_PCT = 0.30  # 30% premium
DISCOUNT_RATE = 0.10  # WACC for terminal value
TERMINAL_MULTIPLE = 20.0  # Exit EBITDA multiple (higher for strategic value)
HOLDING_PERIOD = 7  # Years (longer for strategic acquisition)


def load_json(filepath: str) -> dict:
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def calculate_irr(cash_flows: List[float]) -> float:
    """
    Calculate IRR using binary search method.
    cash_flows[0] is initial investment (negative), rest are positive cash flows.
    """
    def npv(rate):
        return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
    
    try:
        # Binary search for IRR between -99% and 1000%
        low, high = -0.99, 10.0
        tolerance = 1e-6
        
        # Check if NPV is positive at high rate (no solution)
        if npv(high) > 0:
            return None
        
        # Binary search
        for _ in range(100):  # Max iterations
            mid = (low + high) / 2
            npv_mid = npv(mid)
            
            if abs(npv_mid) < tolerance:
                return mid * 100  # Convert to percentage
            
            if npv_mid > 0:
                low = mid
            else:
                high = mid
        
        # Return the midpoint if converged
        return ((low + high) / 2) * 100
    except:
        return None


def calculate_irr_sensitivity():
    """Calculate IRR at different synergy levels."""
    
    # Load financial data
    base_path = Path(__file__).parent.parent
    financials_path = base_path / 'data' / 'master_financials.json'
    market_data_path = base_path / 'data' / 'market_data.json'
    
    financials = load_json(financials_path)
    market_data = load_json(market_data_path)
    
    # Extract Lattice data
    lscc = financials['LSCC']
    lscc_market = market_data['LSCC']
    
    # Transaction parameters
    lscc_current_price = lscc_market['current_price']
    offer_price = lscc_current_price * (1 + PREMIUM_PCT)
    lscc_shares = lscc['shares_outstanding']
    transaction_value = offer_price * lscc_shares  # $12.2B
    
    # Base Lattice cash flow
    # From comprehensive_comps table: Lattice has $23M Free CF, $69M Operating CF
    lscc_operating_cf = lscc.get('operating_cash_flow', 69_000_000)
    lscc_free_cash_flow = 23_000_000  # Actual FCF from comprehensive table
    
    # Base EBITDA for terminal value calculation
    lscc_revenue = lscc['revenue']
    lscc_operating_income = lscc['operating_income']
    lscc_ebitda = lscc_operating_income + (lscc_revenue * 0.03)  # Add D&A estimate
    
    print("=" * 80)
    print("IRR SENSITIVITY ANALYSIS")
    print("=" * 80)
    print(f"\nTransaction Value: ${transaction_value/1e9:.2f}B")
    print(f"Base Lattice FCF: ${lscc_free_cash_flow/1e6:.1f}M")
    print(f"Base Lattice EBITDA: ${lscc_ebitda/1e6:.1f}M")
    print(f"Holding Period: {HOLDING_PERIOD} years")
    print(f"Terminal EBITDA Multiple: {TERMINAL_MULTIPLE}x")
    print()
    
    # Synergy scenarios (as % of base $123.2M)
    synergy_scenarios = {
        'Pessimistic (50%)': 0.50,
        'Base Case (75%)': 0.75,
        'Base (100%)': 1.00,
        'Optimistic (125%)': 1.25,
        'Bull Case (150%)': 1.50,
        'Very Bull (200%)': 2.00,
    }
    
    base_synergies = 123_200_000  # $123.2M base case
    
    results = []
    
    print("=" * 80)
    print("IRR BY SYNERGY LEVEL")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Annual Synergies':<20} {'IRR':<10} {'NPV @ 10%':<15}")
    print("-" * 80)
    
    for scenario_name, multiplier in synergy_scenarios.items():
        annual_synergies = base_synergies * multiplier
        after_tax_synergies = annual_synergies * (1 - TAX_RATE)
        
        # Annual cash flow = Lattice FCF + after-tax synergies
        annual_cf = lscc_free_cash_flow + after_tax_synergies
        
        # Build cash flow stream
        cash_flows = [-transaction_value]  # Initial investment (negative)
        
        # Annual cash flows for holding period
        for year in range(1, HOLDING_PERIOD + 1):
            # Assume 3% growth in base FCF and 5% growth in synergies over time
            base_growth = (1.03) ** (year - 1)
            synergy_growth = (1.05) ** (year - 1)
            cf_year = (lscc_free_cash_flow * base_growth) + (after_tax_synergies * synergy_growth)
            cash_flows.append(cf_year)
        
        # Terminal value: Exit EBITDA multiple
        # Use final year EBITDA with synergies
        final_year_growth = (1.05) ** (HOLDING_PERIOD - 1)
        terminal_ebitda = lscc_ebitda + (annual_synergies * final_year_growth)
        terminal_value = terminal_ebitda * TERMINAL_MULTIPLE
        cash_flows[-1] += terminal_value  # Add terminal value to final year
        
        # Calculate IRR
        irr = calculate_irr(cash_flows)
        
        # Calculate NPV at 10% discount rate
        npv = sum(cf / (1.10) ** i for i, cf in enumerate(cash_flows))
        
        results.append({
            'scenario': scenario_name,
            'synergy_multiplier': multiplier,
            'annual_synergies': annual_synergies,
            'irr': irr,
            'npv': npv
        })
        
        irr_str = f"{irr:.1f}%" if irr else "N/A"
        print(f"{scenario_name:<25} ${annual_synergies/1e6:>6.1f}M{'':<10} {irr_str:<10} ${npv/1e9:>6.2f}B")
    
    print()
    
    # Calculate break-even synergy level (IRR = 10%)
    print("=" * 80)
    print("BREAK-EVEN ANALYSIS")
    print("=" * 80)
    
    target_irr = 0.10
    for test_mult in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        test_synergies = base_synergies * test_mult
        after_tax_synergies = test_synergies * (1 - TAX_RATE)
        
        cash_flows = [-transaction_value]
        for year in range(1, HOLDING_PERIOD + 1):
            base_growth = (1.03) ** (year - 1)
            synergy_growth = (1.05) ** (year - 1)
            cf_year = (lscc_free_cash_flow * base_growth) + (after_tax_synergies * synergy_growth)
            cash_flows.append(cf_year)
        
        final_year_growth = (1.05) ** (HOLDING_PERIOD - 1)
        terminal_ebitda = lscc_ebitda + (test_synergies * final_year_growth)
        terminal_value = terminal_ebitda * TERMINAL_MULTIPLE
        cash_flows[-1] += terminal_value
        
        irr = calculate_irr(cash_flows)
        if irr and irr/100 >= target_irr:
            print(f"Break-even synergy level (IRR ≥ 10%): {test_mult*100:.0f}% of base = ${test_synergies/1e6:.1f}M")
            break
    
    print()
    
    # Probability-weighted expected IRR
    print("=" * 80)
    print("PROBABILITY-WEIGHTED EXPECTED IRR")
    print("=" * 80)
    
    # Assign probabilities to scenarios
    probabilities = {
        'Pessimistic (50%)': 0.10,
        'Base Case (75%)': 0.20,
        'Base (100%)': 0.35,
        'Optimistic (125%)': 0.20,
        'Bull Case (150%)': 0.10,
        'Very Bull (200%)': 0.05,
    }
    
    expected_irr = 0
    for result in results:
        prob = probabilities.get(result['scenario'], 0)
        if result['irr']:
            expected_irr += prob * (result['irr'] / 100)
    
    print(f"Expected IRR: {expected_irr*100:.1f}%")
    print(f"\nProbability Distribution:")
    for result in results:
        prob = probabilities.get(result['scenario'], 0)
        irr_str = f"{result['irr']:.1f}%" if result['irr'] else "N/A"
        print(f"  {result['scenario']:<25} {prob*100:>5.0f}%  →  IRR: {irr_str}")
    
    return results


if __name__ == '__main__':
    try:
        results = calculate_irr_sensitivity()
        print("\n" + "=" * 80)
        print("Analysis complete!")
        print("=" * 80)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

