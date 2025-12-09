#!/usr/bin/env python3
"""
Update Has/Gets Analysis CSV Table with Calculated Values

This script calculates all pro forma metrics and updates the has_gets_analysis.csv file.
"""

import json
import csv
import sys
from pathlib import Path

# Import calculation functions
sys.path.insert(0, str(Path(__file__).parent))
from calculate_has_gets import calculate_has_gets_metrics

def format_currency(value: float) -> str:
    """Format float as currency string."""
    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    else:
        return f"${value:,.0f}"

# Constants for formatting
TAX_RATE = 0.21
INTEREST_RATE = 0.04
DA_PCT_NVDA = 0.02
DA_PCT_LSCC = 0.03
PREMIUM_PCT = 0.30


def format_for_table(value, format_type='currency'):
    """Format value for CSV table."""
    if value is None:
        return 'N/A'
    
    if format_type == 'currency':
        if abs(value) >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.2f}T"
        elif abs(value) >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        else:
            return f"${value:,.0f}"
    elif format_type == 'ratio':
        return f"{value:.2f}x"
    elif format_type == 'percent':
        return f"{value:.2f}%"
    elif format_type == 'price':
        return f"${value:.2f}"
    else:
        return str(value)


def update_has_gets_csv():
    """Calculate metrics and update CSV file."""
    
    base_path = Path(__file__).parent.parent
    csv_path = base_path / 'tables' / 'csv' / 'ma' / 'has_gets_analysis.csv'
    
    # Calculate all metrics
    results = calculate_has_gets_metrics()
    
    # Load financial data for "Has" columns
    financials_path = base_path / 'data' / 'master_financials.json'
    market_data_path = base_path / 'data' / 'market_data.json'
    
    financials = json.load(open(financials_path))
    market_data = json.load(open(market_data_path))
    
    nvda = financials['NVDA']
    lscc = financials['LSCC']
    nvda_market = market_data['NVDA']
    lscc_market = market_data['LSCC']
    
    # Calculate EBITDA for ratios
    def calc_ebitda(operating_income, revenue, da_pct):
        return operating_income + (revenue * da_pct)
    
    nvda_ebitda = calc_ebitda(nvda['operating_income'], nvda['revenue'], DA_PCT_NVDA)
    lscc_ebitda = calc_ebitda(lscc['operating_income'], lscc['revenue'], DA_PCT_LSCC)
    
    # Calculate interest
    nvda_interest = nvda['total_debt'] * INTEREST_RATE
    lscc_interest = lscc['total_debt'] * INTEREST_RATE
    
    # Seller Has values
    seller_has_share_price = lscc_market['current_price']
    seller_has_pe = lscc_market['pe_ratio']
    seller_has_debt_ebitda = lscc['total_debt'] / lscc_ebitda if lscc_ebitda > 0 else None
    seller_has_ebitda_interest = lscc_ebitda / lscc_interest if lscc_interest > 0 else None
    seller_has_debt_cap = (lscc['total_debt'] / (lscc['total_debt'] + lscc['stockholders_equity']) * 100) if (lscc['total_debt'] + lscc['stockholders_equity']) > 0 else None
    seller_has_net_debt = lscc['total_debt'] - lscc_market['cash']
    seller_has_net_debt_cap = (seller_has_net_debt / (lscc['total_debt'] + lscc['stockholders_equity']) * 100) if (lscc['total_debt'] + lscc['stockholders_equity']) > 0 else None
    
    # Seller Gets values (based on offer price)
    seller_gets_share_price = results['seller_gets']['share_price']
    # Implied PE ratio: Offer Price / EPS
    seller_gets_pe = seller_gets_share_price / lscc['eps'] if lscc['eps'] > 0 else None
    # Operating ratios: Debt and EBITDA don't change with offer price
    # These represent the company's operating metrics at the offer valuation
    seller_gets_debt_ebitda = seller_has_debt_ebitda  # Same as Seller Has - operating metrics unchanged
    seller_gets_ebitda_interest = seller_has_ebitda_interest  # Same as Seller Has - operating metrics unchanged
    # Debt/Capitalization at offer price: Debt / (Debt + Offer Value Equity)
    # This shows leverage at offer valuation, which is relevant
    offer_equity_value = results['seller_gets']['total_consideration']
    seller_gets_debt_cap = (lscc['total_debt'] / (lscc['total_debt'] + offer_equity_value) * 100) if (lscc['total_debt'] + offer_equity_value) > 0 else None
    seller_gets_net_debt_cap = (seller_has_net_debt / (lscc['total_debt'] + offer_equity_value) * 100) if (lscc['total_debt'] + offer_equity_value) > 0 else None
    
    # Buyer Has values
    buyer_has_share_price = nvda_market['current_price']
    buyer_has_pe = nvda_market['pe_ratio']
    buyer_has_debt_ebitda = nvda['total_debt'] / nvda_ebitda if nvda_ebitda > 0 else None
    buyer_has_ebitda_interest = nvda_ebitda / nvda_interest if nvda_interest > 0 else None
    buyer_has_debt_cap = (nvda['total_debt'] / (nvda['total_debt'] + nvda['stockholders_equity']) * 100) if (nvda['total_debt'] + nvda['stockholders_equity']) > 0 else None
    buyer_has_net_debt = nvda['total_debt'] - nvda_market['cash']
    buyer_has_net_debt_cap = (buyer_has_net_debt / (nvda['total_debt'] + nvda['stockholders_equity']) * 100) if (nvda['total_debt'] + nvda['stockholders_equity']) > 0 else None
    
    # Build CSV rows
    rows = [
        ['Metric', 'Seller Has', 'Seller Gets', 'Buyer Has', 'Buyer Gets'],
        [
            'Share price',
            format_for_table(seller_has_share_price, 'price'),
            format_for_table(results['seller_gets']['share_price'], 'price'),
            format_for_table(buyer_has_share_price, 'price'),
            format_for_table(results['buyer_gets']['share_price'], 'price')
        ],
        [
            'PE ratio',
            format_for_table(seller_has_pe, 'ratio') if seller_has_pe else 'N/A',
            format_for_table(seller_gets_pe, 'ratio') if seller_gets_pe else 'N/A',
            format_for_table(buyer_has_pe, 'ratio') if buyer_has_pe else 'N/A',
            format_for_table(results['buyer_gets']['pe_ratio'], 'ratio') if results['buyer_gets']['pe_ratio'] else 'N/A'
        ],
        ['Credit Ratios', '', '', '', ''],
        [
            'Debt/EBITDA ratio',
            format_for_table(seller_has_debt_ebitda, 'ratio') if seller_has_debt_ebitda else 'N/A',
            format_for_table(seller_gets_debt_ebitda, 'ratio') if seller_gets_debt_ebitda else 'N/A',
            format_for_table(buyer_has_debt_ebitda, 'ratio') if buyer_has_debt_ebitda else 'N/A',
            format_for_table(results['buyer_gets']['debt_ebitda'], 'ratio') if results['buyer_gets']['debt_ebitda'] else 'N/A'
        ],
        [
            'EBITDA/interest',
            format_for_table(seller_has_ebitda_interest, 'ratio') if seller_has_ebitda_interest else 'N/A',
            format_for_table(seller_gets_ebitda_interest, 'ratio') if seller_gets_ebitda_interest else 'N/A',
            format_for_table(buyer_has_ebitda_interest, 'ratio') if buyer_has_ebitda_interest else 'N/A',
            format_for_table(results['buyer_gets']['ebitda_interest'], 'ratio') if results['buyer_gets']['ebitda_interest'] else 'N/A'
        ],
        [
            'Debt/capitalization',
            format_for_table(seller_has_debt_cap, 'percent') if seller_has_debt_cap else 'N/A',
            format_for_table(seller_gets_debt_cap, 'percent') if seller_gets_debt_cap else 'N/A',
            format_for_table(buyer_has_debt_cap, 'percent') if buyer_has_debt_cap else 'N/A',
            format_for_table(results['buyer_gets']['debt_capitalization'], 'percent') if results['buyer_gets']['debt_capitalization'] else 'N/A'
        ],
        [
            'Debt (net of cash)/capitalization',
            format_for_table(seller_has_net_debt_cap, 'percent') if seller_has_net_debt_cap else 'N/A',
            format_for_table(seller_gets_net_debt_cap, 'percent') if seller_gets_net_debt_cap else 'N/A',
            format_for_table(buyer_has_net_debt_cap, 'percent') if buyer_has_net_debt_cap else 'N/A',
            format_for_table(results['buyer_gets']['net_debt_capitalization'], 'percent') if results['buyer_gets']['net_debt_capitalization'] else 'N/A'
        ],
        ['Book Values', '', '', '', ''],
        [
            'Debt',
            format_for_table(lscc['total_debt'], 'currency'),
            format_for_table(lscc['total_debt'], 'currency'),  # Debt stays with company
            format_for_table(nvda['total_debt'], 'currency'),
            format_for_table(results['buyer_gets']['debt'], 'currency')
        ],
        [
            'Common stock and retained earnings',
            format_for_table(lscc['stockholders_equity'], 'currency'),
            'N/A',
            format_for_table(nvda['stockholders_equity'], 'currency'),
            format_for_table(results['buyer_gets']['equity'], 'currency')
        ],
        [
            'Market value of shares outstanding',
            format_for_table(lscc_market['market_cap'], 'currency'),
            format_for_table(results['seller_gets']['total_consideration'], 'currency'),
            format_for_table(nvda_market['market_cap'], 'currency'),
            format_for_table(results['buyer_gets']['market_cap'], 'currency')
        ],
        ['', '', '', '', ''],  # Empty row
        ['Assumptions', '', '', '', ''],
        ['Offer Premium', '', f'{PREMIUM_PCT * 100:.0f}%', '', ''],
        ['Tax Rate', '', f'{TAX_RATE * 100:.0f}%', '', ''],
        ['Interest Rate (on debt)', '', f'{INTEREST_RATE * 100:.0f}%', '', ''],
        ['D&A as % of Revenue - NVIDIA', '', '', '', f'{DA_PCT_NVDA * 100:.0f}%'],
        ['D&A as % of Revenue - Lattice', '', f'{DA_PCT_LSCC * 100:.0f}%', '', ''],
        ['Annual Synergies', '', format_for_table(123_200_000, 'currency'), '', ''],
        ['Deal Structure', '', '100% Cash', '', ''],
        ['Transaction Value', '', format_for_table(results['transaction']['transaction_value'], 'currency'), '', ''],
        ['Goodwill', '', format_for_table(results['transaction']['goodwill'], 'currency'), '', ''],
    ]
    
    # Write CSV
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"\n✅ Successfully updated {csv_path}")
    print(f"\nKey Updates:")
    print(f"  Seller Gets - Share Price: ${results['seller_gets']['share_price']:.2f}")
    print(f"  Seller Gets - Total Consideration: {format_currency(results['seller_gets']['total_consideration'])}")
    print(f"  Buyer Gets - P/E Ratio: {results['buyer_gets']['pe_ratio']:.2f}x" if results['buyer_gets']['pe_ratio'] else "  Buyer Gets - P/E Ratio: N/A")
    print(f"  Buyer Gets - Debt/EBITDA: {results['buyer_gets']['debt_ebitda']:.2f}x" if results['buyer_gets']['debt_ebitda'] else "  Buyer Gets - Debt/EBITDA: N/A")
    print(f"  Buyer Gets - Equity: {format_currency(results['buyer_gets']['equity'])}")


if __name__ == '__main__':
    try:
        update_has_gets_csv()
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

