#!/usr/bin/env python3
"""
Calculate Has/Gets Analysis Metrics for NVIDIA-Lattice Acquisition

This script calculates all pro forma financial metrics for the Has/Gets analysis table,
including Seller Gets (Lattice) and Buyer Gets (NVIDIA post-acquisition) columns.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Constants
TAX_RATE = 0.21  # Corporate tax rate
INTEREST_RATE = 0.04  # Assumed interest rate on debt
DA_PCT_NVDA = 0.02  # D&A as % of revenue for NVIDIA
DA_PCT_LSCC = 0.03  # D&A as % of revenue for Lattice
PREMIUM_PCT = 0.30  # 30% premium on offer price


def load_json(filepath: str) -> Dict:
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def parse_value(value_str: str) -> float:
    """Parse value string (e.g., '$123.45M' or '$1.23B') to float."""
    if not value_str or value_str == 'N/A':
        return 0.0
    
    # Remove $ and whitespace
    value_str = value_str.replace('$', '').replace(',', '').strip()
    
    # Handle millions and billions
    if value_str.endswith('M'):
        return float(value_str[:-1]) * 1_000_000
    elif value_str.endswith('B'):
        return float(value_str[:-1]) * 1_000_000_000
    elif value_str.endswith('T'):
        return float(value_str[:-1]) * 1_000_000_000_000
    else:
        return float(value_str)


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


def calculate_ebitda(operating_income: float, revenue: float, da_pct: float) -> float:
    """Calculate EBITDA = Operating Income + D&A."""
    da = revenue * da_pct
    return operating_income + da


def calculate_has_gets_metrics():
    """Calculate all Has/Gets metrics."""
    
    # Load financial data
    base_path = Path(__file__).parent.parent
    financials_path = base_path / 'data' / 'master_financials.json'
    market_data_path = base_path / 'data' / 'market_data.json'
    synergy_path = base_path / 'tables' / 'csv' / 'ma' / 'synergy_estimates.csv'
    
    financials = load_json(financials_path)
    market_data = load_json(market_data_path)
    
    # Extract NVIDIA data
    nvda = financials['NVDA']
    nvda_market = market_data['NVDA']
    
    # Extract Lattice data
    lscc = financials['LSCC']
    lscc_market = market_data['LSCC']
    
    # Load synergies
    annual_synergies = 123_200_000  # $123.2M from synergy_estimates.csv
    
    # ============================================================================
    # TRANSACTION PARAMETERS
    # ============================================================================
    lscc_current_price = lscc_market['current_price']
    offer_price = lscc_current_price * (1 + PREMIUM_PCT)
    lscc_shares = lscc['shares_outstanding']
    transaction_value = offer_price * lscc_shares
    
    print("=" * 80)
    print("TRANSACTION PARAMETERS")
    print("=" * 80)
    print(f"Lattice Current Price: ${lscc_current_price:.2f}")
    print(f"Offer Price (30% premium): ${offer_price:.2f}")
    print(f"Lattice Shares Outstanding: {lscc_shares:,.0f}")
    print(f"Total Transaction Value: {format_currency(transaction_value)}")
    print(f"Premium: {PREMIUM_PCT * 100:.1f}%")
    print()
    
    # ============================================================================
    # SELLER GETS (Lattice)
    # ============================================================================
    print("=" * 80)
    print("SELLER GETS (Lattice)")
    print("=" * 80)
    
    seller_gets = {
        'share_price': offer_price,
        'pe_ratio': None,  # N/A - receiving cash
        'total_consideration': transaction_value,
    }
    
    print(f"Share Price: ${seller_gets['share_price']:.2f}")
    print(f"PE Ratio: N/A (receiving cash)")
    print(f"Total Consideration: {format_currency(seller_gets['total_consideration'])}")
    print()
    
    # ============================================================================
    # BUYER GETS (NVIDIA Pro Forma)
    # ============================================================================
    print("=" * 80)
    print("BUYER GETS (NVIDIA Pro Forma)")
    print("=" * 80)
    
    # Basic metrics (unchanged in all-cash deal)
    nvda_share_price = nvda_market['current_price']
    nvda_market_cap = nvda_market['market_cap']
    
    # Calculate EBITDA for both companies
    nvda_ebitda = calculate_ebitda(
        nvda['operating_income'],
        nvda['revenue'],
        DA_PCT_NVDA
    )
    
    lscc_ebitda = calculate_ebitda(
        lscc['operating_income'],
        lscc['revenue'],
        DA_PCT_LSCC
    )
    
    print(f"\nEBITDA Calculations:")
    print(f"  NVIDIA EBITDA: {format_currency(nvda_ebitda)}")
    print(f"  Lattice EBITDA: {format_currency(lscc_ebitda)}")
    
    # Pro forma combined metrics
    pro_forma_net_income = (
        nvda['net_income'] +
        lscc['net_income'] +
        annual_synergies * (1 - TAX_RATE)  # After-tax synergies
    )
    
    pro_forma_ebitda = nvda_ebitda + lscc_ebitda + annual_synergies
    
    # Pro forma debt
    pro_forma_debt = nvda['total_debt'] + lscc['total_debt']
    
    # Pro forma cash
    pro_forma_cash = (
        nvda_market['cash'] +
        lscc_market['cash'] -
        transaction_value
    )
    
    # Pro forma equity
    lscc_book_value = lscc['stockholders_equity']
    goodwill = transaction_value - lscc_book_value
    
    pro_forma_equity = (
        nvda['stockholders_equity'] -
        transaction_value +
        goodwill
    )
    
    # Calculate interest expense
    nvda_interest = nvda['total_debt'] * INTEREST_RATE
    lscc_interest = lscc['total_debt'] * INTEREST_RATE
    pro_forma_interest = nvda_interest + lscc_interest
    
    # Calculate ratios
    pro_forma_pe = nvda_market_cap / pro_forma_net_income if pro_forma_net_income > 0 else None
    
    pro_forma_debt_ebitda = pro_forma_debt / pro_forma_ebitda if pro_forma_ebitda > 0 else None
    
    pro_forma_ebitda_interest = pro_forma_ebitda / pro_forma_interest if pro_forma_interest > 0 else None
    
    # Debt/Capitalization (using book equity)
    total_capitalization_book = pro_forma_debt + pro_forma_equity
    pro_forma_debt_cap_book = (pro_forma_debt / total_capitalization_book * 100) if total_capitalization_book > 0 else None
    
    # Debt/Capitalization (using market cap)
    total_capitalization_market = pro_forma_debt + nvda_market_cap
    pro_forma_debt_cap_market = (pro_forma_debt / total_capitalization_market * 100) if total_capitalization_market > 0 else None
    
    # Net Debt/Capitalization
    pro_forma_net_debt = pro_forma_debt - pro_forma_cash
    pro_forma_net_debt_cap = (pro_forma_net_debt / total_capitalization_book * 100) if total_capitalization_book > 0 else None
    
    # ============================================================================
    # OUTPUT RESULTS
    # ============================================================================
    print(f"\nPro Forma Financial Metrics:")
    print(f"  Net Income: {format_currency(pro_forma_net_income)}")
    print(f"  EBITDA: {format_currency(pro_forma_ebitda)}")
    print(f"  Debt: {format_currency(pro_forma_debt)}")
    print(f"  Cash: {format_currency(pro_forma_cash)}")
    print(f"  Equity: {format_currency(pro_forma_equity)}")
    print(f"  Goodwill: {format_currency(goodwill)}")
    print(f"  Interest Expense: {format_currency(pro_forma_interest)}")
    
    print(f"\nPro Forma Ratios:")
    print(f"  P/E Ratio: {pro_forma_pe:.2f}x" if pro_forma_pe else "  P/E Ratio: N/A")
    print(f"  Debt/EBITDA: {pro_forma_debt_ebitda:.2f}x" if pro_forma_debt_ebitda else "  Debt/EBITDA: N/A")
    print(f"  EBITDA/Interest: {pro_forma_ebitda_interest:.2f}x" if pro_forma_ebitda_interest else "  EBITDA/Interest: N/A")
    print(f"  Debt/Capitalization (book): {pro_forma_debt_cap_book:.2f}%" if pro_forma_debt_cap_book else "  Debt/Capitalization: N/A")
    print(f"  Net Debt/Capitalization: {pro_forma_net_debt_cap:.2f}%" if pro_forma_net_debt_cap else "  Net Debt/Capitalization: N/A")
    
    # ============================================================================
    # FORMAT FOR CSV UPDATE
    # ============================================================================
    print("\n" + "=" * 80)
    print("CSV UPDATE VALUES")
    print("=" * 80)
    print("\nSeller Gets:")
    print(f"  Share price: ${offer_price:.2f}")
    print(f"  PE ratio: N/A")
    print(f"  Market value of shares outstanding: {format_currency(transaction_value)}")
    
    print("\nBuyer Gets:")
    print(f"  Share price: ${nvda_share_price:.2f}")
    print(f"  PE ratio: {pro_forma_pe:.2f}" if pro_forma_pe else "  PE ratio: N/A")
    print(f"  Debt/EBITDA ratio: {pro_forma_debt_ebitda:.2f}x" if pro_forma_debt_ebitda else "  Debt/EBITDA ratio: N/A")
    print(f"  EBITDA/interest: {pro_forma_ebitda_interest:.2f}x" if pro_forma_ebitda_interest else "  EBITDA/interest: N/A")
    print(f"  Debt/capitalization: {pro_forma_debt_cap_book:.2f}%" if pro_forma_debt_cap_book else "  Debt/capitalization: N/A")
    print(f"  Debt (net of cash)/capitalization: {pro_forma_net_debt_cap:.2f}%" if pro_forma_net_debt_cap else "  Debt (net of cash)/capitalization: N/A")
    print(f"  Debt: {format_currency(pro_forma_debt)}")
    print(f"  Common stock and retained earnings: {format_currency(pro_forma_equity)}")
    print(f"  Market value of shares outstanding: {format_currency(nvda_market_cap)}")
    
    # ============================================================================
    # RETURN DICTIONARY FOR PROGRAMMATIC USE
    # ============================================================================
    return {
        'seller_gets': {
            'share_price': offer_price,
            'pe_ratio': None,
            'total_consideration': transaction_value,
        },
        'buyer_gets': {
            'share_price': nvda_share_price,
            'pe_ratio': pro_forma_pe,
            'debt_ebitda': pro_forma_debt_ebitda,
            'ebitda_interest': pro_forma_ebitda_interest,
            'debt_capitalization': pro_forma_debt_cap_book,
            'net_debt_capitalization': pro_forma_net_debt_cap,
            'debt': pro_forma_debt,
            'equity': pro_forma_equity,
            'market_cap': nvda_market_cap,
        },
        'transaction': {
            'offer_price': offer_price,
            'premium_pct': PREMIUM_PCT * 100,
            'transaction_value': transaction_value,
            'goodwill': goodwill,
        }
    }


if __name__ == '__main__':
    try:
        results = calculate_has_gets_metrics()
        print("\n" + "=" * 80)
        print("Calculation complete!")
        print("=" * 80)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
