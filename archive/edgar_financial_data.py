#!/usr/bin/env python3
"""
EDGAR Financial Data Extractor
Demonstrates how to extract financial statements and facts for semiconductor companies
"""

import sys
import os
import json
from datetime import datetime

# Add the pipx edgartools site-packages to path
pipx_site_packages = "/Users/joshuagao/.local/pipx/venvs/edgartools/lib/python3.14/site-packages"
sys.path.insert(0, pipx_site_packages)

try:
    from edgar import Company, set_identity
    set_identity("Academic Research joshua.gao@yale.edu")
    print("✓ Successfully imported edgar module and set identity")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

COMPANIES = {
    'NVDA': 'NVIDIA Corporation',
    'MCHP': 'Microchip Technology Incorporated',  
    'AMD': 'Advanced Micro Devices Inc',
    'LSCC': 'Lattice Semiconductor Corporation'
}

def get_company_financials(ticker, company_name):
    """Extract financial data for a company"""
    print(f"\nProcessing {ticker} - {company_name}")
    
    try:
        company = Company(ticker)
        
        result = {
            'ticker': ticker,
            'name': company.name,
            'cik': company.cik,
            'sic': getattr(company, 'sic', None),
            'industry': getattr(company, 'industry', None)
        }
        
        print(f"  Company: {result['name']}")
        print(f"  CIK: {result['cik']}")
        print(f"  SIC: {result['sic']}")
        
        # Try to get latest 10-K and 10-Q
        financial_data = {}
        
        try:
            latest_10k = company.latest_tenk
            if latest_10k:
                print(f"  Latest 10-K: {latest_10k.filing_date}")
                financial_data['latest_10k'] = {
                    'filing_date': str(latest_10k.filing_date),
                    'accession_number': latest_10k.accession_number
                }
        except Exception as e:
            print(f"  Could not get latest 10-K: {e}")
        
        try:
            latest_10q = company.latest_tenq
            if latest_10q:
                print(f"  Latest 10-Q: {latest_10q.filing_date}")
                financial_data['latest_10q'] = {
                    'filing_date': str(latest_10q.filing_date),
                    'accession_number': latest_10q.accession_number
                }
        except Exception as e:
            print(f"  Could not get latest 10-Q: {e}")
        
        # Try to get financial statements
        try:
            print("  Attempting to get financial statements...")
            
            # Try income statement
            try:
                income_stmt = company.income_statement
                if income_stmt is not None:
                    financial_data['has_income_statement'] = True
                    print("    ✓ Income statement available")
            except Exception as e:
                print(f"    Income statement not available: {e}")
            
            # Try balance sheet
            try:
                balance_sheet = company.balance_sheet
                if balance_sheet is not None:
                    financial_data['has_balance_sheet'] = True
                    print("    ✓ Balance sheet available")
            except Exception as e:
                print(f"    Balance sheet not available: {e}")
            
            # Try cash flow
            try:
                cash_flow = company.cash_flow
                if cash_flow is not None:
                    financial_data['has_cash_flow'] = True
                    print("    ✓ Cash flow statement available")
            except Exception as e:
                print(f"    Cash flow statement not available: {e}")
                
        except Exception as e:
            print(f"  Error getting financial statements: {e}")
        
        # Try to get facts (XBRL data)
        try:
            print("  Attempting to get company facts...")
            facts = company.get_facts()
            if facts:
                financial_data['has_facts'] = True
                financial_data['facts_count'] = len(facts) if hasattr(facts, '__len__') else 'unknown'
                print(f"    ✓ Company facts available ({financial_data['facts_count']})")
        except Exception as e:
            print(f"    Could not get facts: {e}")
        
        result['financial_data'] = financial_data
        result['extraction_timestamp'] = datetime.now().isoformat()
        
        print(f"  ✓ Successfully processed {ticker}")
        return result
        
    except Exception as e:
        print(f"  ✗ Error processing {ticker}: {e}")
        return {
            'ticker': ticker,
            'error': str(e),
            'extraction_timestamp': datetime.now().isoformat()
        }

def main():
    """Main extraction function"""
    print("="*70)
    print("EDGAR FINANCIAL DATA EXTRACTOR")
    print("="*70)
    print("Extracting financial data for semiconductor companies:")
    for ticker, name in COMPANIES.items():
        print(f"  • {ticker} - {name}")
    print()
    
    results = {}
    
    # Process each company
    for ticker, company_name in COMPANIES.items():
        results[ticker] = get_company_financials(ticker, company_name)
    
    # Save results
    output_file = 'edgar_financial_data.json'
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n✓ Financial data saved to: {output_file}")
    except Exception as e:
        print(f"\n✗ Error saving data: {e}")
    
    # Summary report
    print("\n" + "="*70)
    print("FINANCIAL DATA EXTRACTION SUMMARY")
    print("="*70)
    
    for ticker, data in results.items():
        if 'error' in data:
            print(f"{ticker:<6} ERROR: {data['error']}")
        else:
            name = data.get('name', 'Unknown')
            financial_data = data.get('financial_data', {})
            
            statements = []
            if financial_data.get('has_income_statement'): statements.append('IS')
            if financial_data.get('has_balance_sheet'): statements.append('BS')  
            if financial_data.get('has_cash_flow'): statements.append('CF')
            if financial_data.get('has_facts'): statements.append('FACTS')
            
            latest_10k = financial_data.get('latest_10k', {}).get('filing_date', 'N/A')
            latest_10q = financial_data.get('latest_10q', {}).get('filing_date', 'N/A')
            
            print(f"{ticker:<6} {name:<35} 10-K: {latest_10k:<12} 10-Q: {latest_10q:<12} Data: {', '.join(statements)}")
    
    print(f"\n✓ Results saved to: {output_file}")
    return 0

if __name__ == "__main__":
    exit(main())