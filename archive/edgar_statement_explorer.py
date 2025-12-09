#!/usr/bin/env python3
"""
MultiPeriodStatement Explorer - Understanding the data structure
"""

import sys
import os

# Add the pipx edgartools site-packages to path
pipx_site_packages = "/Users/joshuagao/.local/pipx/venvs/edgartools/lib/python3.14/site-packages"
sys.path.insert(0, pipx_site_packages)

try:
    from edgar import Company, set_identity
    set_identity("Investment Banking Analysis joshua.gao@yale.edu")
    print("✅ MultiPeriodStatement Explorer initialized")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def explore_financial_statement(ticker):
    """Explore the structure of financial statement objects"""
    print(f"\n{'='*60}")
    print(f"EXPLORING FINANCIAL STATEMENTS FOR {ticker}")
    print('='*60)
    
    try:
        company = Company(ticker)
        print(f"Company: {company.name}")
        
        # Explore Income Statement
        print(f"\n📊 INCOME STATEMENT EXPLORATION")
        try:
            income_stmt = company.income_statement()
            print(f"✅ Type: {type(income_stmt)}")
            print(f"✅ Dir: {[attr for attr in dir(income_stmt) if not attr.startswith('_')][:15]}...")
            
            # Try to get the actual data
            if hasattr(income_stmt, 'data'):
                print(f"✅ Has data attribute: {type(income_stmt.data)}")
                if hasattr(income_stmt.data, 'columns'):
                    print(f"   Columns: {list(income_stmt.data.columns)[:10]}...")
                elif hasattr(income_stmt.data, 'keys'):
                    print(f"   Keys: {list(income_stmt.data.keys())[:10]}...")
            
            if hasattr(income_stmt, 'values'):
                print(f"✅ Has values: {type(income_stmt.values)}")
            
            if hasattr(income_stmt, 'to_dict'):
                print(f"✅ Can convert to dict")
                try:
                    data_dict = income_stmt.to_dict()
                    print(f"   Dict keys: {list(data_dict.keys())[:10]}...")
                except Exception as e:
                    print(f"   Dict conversion error: {e}")
            
            # Try calling it as string to see data
            if hasattr(income_stmt, '__str__'):
                try:
                    str_repr = str(income_stmt)[:500]  # First 500 chars
                    print(f"✅ String representation preview:\n{str_repr}...")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Income Statement error: {e}")
        
        # Similar exploration for Balance Sheet
        print(f"\n🏦 BALANCE SHEET EXPLORATION")
        try:
            balance_sheet = company.balance_sheet()
            print(f"✅ Type: {type(balance_sheet)}")
            
            # Check if it has the same structure
            if hasattr(balance_sheet, 'data'):
                print(f"✅ Has data attribute: {type(balance_sheet.data)}")
            
            if hasattr(balance_sheet, '__str__'):
                try:
                    str_repr = str(balance_sheet)[:500]
                    print(f"✅ String representation preview:\n{str_repr}...")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Balance Sheet error: {e}")
        
        # Try the Financials object approach
        print(f"\n💼 FINANCIALS OBJECT EXPLORATION")
        try:
            financials = company.get_financials()
            print(f"✅ Type: {type(financials)}")
            print(f"✅ Dir: {[attr for attr in dir(financials) if not attr.startswith('_')][:15]}...")
            
            # Check for common financial metrics
            financial_attrs = ['revenue', 'net_income', 'total_assets', 'equity']
            for attr in financial_attrs:
                if hasattr(financials, attr):
                    value = getattr(financials, attr)
                    print(f"   ✅ {attr}: {value} (type: {type(value)})")
            
            # Try string representation
            if hasattr(financials, '__str__'):
                try:
                    str_repr = str(financials)[:800]
                    print(f"✅ Financials string preview:\n{str_repr}...")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Financials error: {e}")
        
    except Exception as e:
        print(f"❌ Major error: {e}")

def main():
    """Explore one company in detail"""
    # Just explore NVIDIA to understand the data structure
    explore_financial_statement('NVDA')
    
    print(f"\n🎯 EXPLORATION COMPLETE")
    print("This will help us understand how to extract the actual financial data")
    
    return 0

if __name__ == "__main__":
    exit(main())