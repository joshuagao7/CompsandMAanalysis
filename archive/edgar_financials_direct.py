#!/usr/bin/env python3
"""
Investment Banking Comps Model - Direct Financial Statements Approach
Uses income_statement, balance_sheet, and cash_flow objects directly
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add the pipx edgartools site-packages to path
pipx_site_packages = "/Users/joshuagao/.local/pipx/venvs/edgartools/lib/python3.14/site-packages"
sys.path.insert(0, pipx_site_packages)

try:
    from edgar import Company, set_identity
    set_identity("Investment Banking Analysis joshua.gao@yale.edu")
    print("✅ Investment Banking Financial Statements Analyzer initialized")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

COMPANIES = {
    'NVDA': 'NVIDIA Corporation',
    'MCHP': 'Microchip Technology Inc',
    'AMD': 'Advanced Micro Devices Inc', 
    'LSCC': 'Lattice Semiconductor Corp'
}

def extract_company_financials(ticker, company_name):
    """Extract financial data using direct financial statement access"""
    print(f"\n{'='*70}")
    print(f"🏦 EXTRACTING FINANCIALS FOR {ticker} - {company_name}")
    print('='*70)
    
    try:
        company = Company(ticker)
        print(f"Company: {company.name}")
        print(f"CIK: {company.cik}")
        
        metrics = {
            'company_info': {
                'ticker': ticker,
                'name': company.name,
                'cik': company.cik,
                'sic': getattr(company, 'sic', None)
            }
        }
        
        # Try Income Statement
        print(f"\n📊 INCOME STATEMENT ACCESS")
        try:
            income_stmt = company.income_statement
            if income_stmt is not None:
                print(f"✅ Income Statement: Available")
                print(f"   Type: {type(income_stmt)}")
                print(f"   Attributes: {[attr for attr in dir(income_stmt) if not attr.startswith('_')][:10]}...")
                
                # Try to extract data
                if hasattr(income_stmt, 'values') or hasattr(income_stmt, 'to_dict'):
                    metrics['income_statement_available'] = True
                    
                    # Try different ways to access the data
                    if hasattr(income_stmt, 'get_revenue'):
                        try:
                            revenue = income_stmt.get_revenue()
                            if revenue:
                                print(f"   📈 Revenue method found: {revenue}")
                                metrics['revenue'] = revenue
                        except:
                            pass
                    
            else:
                print(f"❌ Income Statement: Not available")
        except Exception as e:
            print(f"❌ Income Statement Error: {e}")
        
        # Try Balance Sheet
        print(f"\n🏛️ BALANCE SHEET ACCESS")
        try:
            balance_sheet = company.balance_sheet
            if balance_sheet is not None:
                print(f"✅ Balance Sheet: Available")
                print(f"   Type: {type(balance_sheet)}")
                print(f"   Attributes: {[attr for attr in dir(balance_sheet) if not attr.startswith('_')][:10]}...")
                metrics['balance_sheet_available'] = True
            else:
                print(f"❌ Balance Sheet: Not available")
        except Exception as e:
            print(f"❌ Balance Sheet Error: {e}")
        
        # Try Cash Flow
        print(f"\n💰 CASH FLOW ACCESS")
        try:
            cash_flow = company.cash_flow
            if cash_flow is not None:
                print(f"✅ Cash Flow: Available")
                print(f"   Type: {type(cash_flow)}")
                print(f"   Attributes: {[attr for attr in dir(cash_flow) if not attr.startswith('_')][:10]}...")
                metrics['cash_flow_available'] = True
            else:
                print(f"❌ Cash Flow: Not available")
        except Exception as e:
            print(f"❌ Cash Flow Error: {e}")
        
        # Try to access financial data through different methods
        print(f"\n🔍 ALTERNATIVE DATA ACCESS METHODS")
        
        # Method 1: get_financials()
        try:
            financials = company.get_financials()
            if financials:
                print(f"✅ get_financials(): Available")
                print(f"   Type: {type(financials)}")
                if hasattr(financials, '__len__'):
                    print(f"   Length: {len(financials)}")
                metrics['financials_method_available'] = True
                
                # Try to extract specific metrics
                if hasattr(financials, 'revenue'):
                    print(f"   📊 Revenue available through financials")
                elif hasattr(financials, 'Revenue'):
                    print(f"   📊 Revenue (capitalized) available")
        except Exception as e:
            print(f"❌ get_financials() Error: {e}")
        
        # Method 2: Direct attribute access
        try:
            # Try some common financial attributes
            attributes_to_try = ['revenue', 'total_revenue', 'net_income', 'total_assets', 'stockholders_equity']
            
            for attr in attributes_to_try:
                if hasattr(company, attr):
                    value = getattr(company, attr)
                    if value is not None:
                        print(f"   ✅ Found {attr}: {type(value)}")
                        metrics[f'{attr}_available'] = True
        except Exception as e:
            print(f"❌ Direct attribute access error: {e}")
        
        # Method 3: Try latest 10-K and 10-Q for specific data
        print(f"\n📋 LATEST FILINGS DATA")
        try:
            latest_10k = company.latest_tenk
            if latest_10k:
                print(f"✅ Latest 10-K: {latest_10k.filing_date}")
                metrics['latest_10k_date'] = str(latest_10k.filing_date)
                
                # Try to get XBRL from the filing
                try:
                    xbrl = latest_10k.xbrl()
                    if xbrl:
                        print(f"   📊 XBRL data available from 10-K")
                        metrics['xbrl_from_10k_available'] = True
                        
                        # Look for common tags in XBRL
                        common_tags = ['Revenues', 'Revenue', 'TotalRevenue', 'NetIncomeLoss', 'Assets']
                        for tag in common_tags:
                            if hasattr(xbrl, tag.lower()):
                                fact = getattr(xbrl, tag.lower())
                                if fact and hasattr(fact, 'values') and fact.values:
                                    value = fact.values[0].value
                                    print(f"   💰 {tag}: ${value:,.0f}")
                                    metrics[tag.lower()] = value
                except Exception as e:
                    print(f"   ❌ XBRL access error: {e}")
        except Exception as e:
            print(f"❌ Latest 10-K error: {e}")
        
        metrics['extraction_timestamp'] = datetime.now().isoformat()
        print(f"\n✅ Completed analysis for {ticker}")
        
        return metrics
        
    except Exception as e:
        print(f"\n❌ Major error processing {ticker}: {e}")
        return {
            'company_info': {'ticker': ticker, 'name': company_name},
            'error': str(e),
            'extraction_timestamp': datetime.now().isoformat()
        }

def main():
    """Main analysis function"""
    print("🚀 INVESTMENT BANKING FINANCIAL STATEMENTS ANALYSIS")
    print("🔍 Direct Financial Data Access Investigation")
    
    all_results = {}
    
    # Analyze all companies
    for ticker, company_name in COMPANIES.items():
        all_results[ticker] = extract_company_financials(ticker, company_name)
    
    # Save results
    output_file = 'financial_statements_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n📊 ANALYSIS SUMMARY")
    print('='*50)
    
    for ticker, data in all_results.items():
        if 'error' not in data:
            company_name = data['company_info']['name']
            print(f"\n{ticker} - {company_name}:")
            
            # Show what's available
            available_items = []
            for key, value in data.items():
                if key.endswith('_available') and value:
                    available_items.append(key.replace('_available', ''))
            
            if available_items:
                print(f"  ✅ Available: {', '.join(available_items)}")
            else:
                print(f"  ❌ No direct financial data access found")
                
            # Show any actual values found
            financial_values = {}
            for key, value in data.items():
                if isinstance(value, (int, float)) and not key.endswith('cik'):
                    financial_values[key] = value
            
            if financial_values:
                print(f"  💰 Values found:")
                for key, value in financial_values.items():
                    print(f"     {key}: ${value:,.0f}")
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("🔍 This analysis will guide the next approach for financial data extraction")
    
    return 0

if __name__ == "__main__":
    exit(main())