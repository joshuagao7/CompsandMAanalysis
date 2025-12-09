#!/usr/bin/env python3
"""
Investment Banking Comps Model - FINAL WORKING VERSION
Correctly calls financial statement methods and extracts actual data
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
    print("🏦 INVESTMENT BANKING COMPS MODEL - FINAL VERSION")
    print("✅ Successfully initialized for semiconductor sector analysis")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

COMPANIES = {
    'NVDA': 'NVIDIA Corporation',
    'MCHP': 'Microchip Technology Inc',
    'AMD': 'Advanced Micro Devices Inc', 
    'LSCC': 'Lattice Semiconductor Corp'
}

def safe_extract_value(data_obj, possible_attrs):
    """Safely extract a numeric value from various data structures"""
    if data_obj is None:
        return None
    
    try:
        # If it's already a number
        if isinstance(data_obj, (int, float)):
            return float(data_obj)
        
        # If it has a value attribute
        if hasattr(data_obj, 'value'):
            val = data_obj.value
            return float(val) if val is not None else None
        
        # If it's a pandas Series or DataFrame, get the latest value
        if hasattr(data_obj, 'iloc') and len(data_obj) > 0:
            val = data_obj.iloc[-1]  # Get latest value
            return float(val) if pd.notna(val) else None
        
        # If it has values attribute (list-like)
        if hasattr(data_obj, 'values') and data_obj.values is not None:
            if len(data_obj.values) > 0:
                val = data_obj.values[-1]  # Get latest
                return float(val) if val is not None else None
        
        # Try different attribute names
        for attr in possible_attrs:
            if hasattr(data_obj, attr):
                val = getattr(data_obj, attr)
                if val is not None:
                    if callable(val):
                        try:
                            val = val()
                        except:
                            continue
                    if isinstance(val, (int, float)):
                        return float(val)
                    elif hasattr(val, 'iloc') and len(val) > 0:
                        return float(val.iloc[-1])
        
        return None
    except Exception as e:
        return None

def extract_financial_data(ticker, company_name):
    """Extract comprehensive financial data for investment banking analysis"""
    print(f"\n{'='*80}")
    print(f"🚀 INVESTMENT BANKING ANALYSIS: {ticker} - {company_name}")
    print('='*80)
    
    try:
        company = Company(ticker)
        print(f"📊 Company: {company.name}")
        print(f"🏢 CIK: {company.cik}")
        
        metrics = {
            'company_info': {
                'ticker': ticker,
                'name': company.name,
                'cik': company.cik,
                'sic': getattr(company, 'sic', None)
            }
        }
        
        print(f"\n💼 EXTRACTING FINANCIAL STATEMENTS...")
        
        # Get Financials object
        financials = company.get_financials()
        print(f"✅ Financials object loaded: {type(financials)}")
        
        # Get Income Statement
        try:
            income_stmt = company.income_statement()
            print(f"✅ Income Statement: {type(income_stmt)}")
            if income_stmt is not None:
                print(f"   📋 Income Statement Shape: {getattr(income_stmt, 'shape', 'N/A')}")
                print(f"   📋 Income Statement Columns: {list(income_stmt.columns) if hasattr(income_stmt, 'columns') else 'N/A'}")
                
                # Extract key metrics from income statement
                if hasattr(income_stmt, 'columns'):
                    # Look for revenue in various forms
                    revenue_cols = [col for col in income_stmt.columns if any(term in str(col).lower() for term in ['revenue', 'sales', 'total revenue'])]
                    if revenue_cols:
                        revenue = safe_extract_value(income_stmt[revenue_cols[0]], ['iloc', 'value'])
                        if revenue:
                            metrics['revenue'] = revenue
                            print(f"   💰 Revenue: ${revenue:,.0f}")
                    
                    # Look for net income
                    income_cols = [col for col in income_stmt.columns if any(term in str(col).lower() for term in ['net income', 'net earnings', 'profit'])]
                    if income_cols:
                        net_income = safe_extract_value(income_stmt[income_cols[0]], ['iloc', 'value'])
                        if net_income:
                            metrics['net_income'] = net_income
                            print(f"   💎 Net Income: ${net_income:,.0f}")
                    
                    # Look for operating income
                    op_income_cols = [col for col in income_stmt.columns if any(term in str(col).lower() for term in ['operating income', 'operating earnings', 'ebit'])]
                    if op_income_cols:
                        op_income = safe_extract_value(income_stmt[op_income_cols[0]], ['iloc', 'value'])
                        if op_income:
                            metrics['operating_income'] = op_income
                            print(f"   🏭 Operating Income: ${op_income:,.0f}")
        except Exception as e:
            print(f"❌ Income Statement Error: {e}")
        
        # Get Balance Sheet
        try:
            balance_sheet = company.balance_sheet()
            print(f"✅ Balance Sheet: {type(balance_sheet)}")
            if balance_sheet is not None:
                print(f"   📋 Balance Sheet Shape: {getattr(balance_sheet, 'shape', 'N/A')}")
                print(f"   📋 Balance Sheet Columns: {list(balance_sheet.columns) if hasattr(balance_sheet, 'columns') else 'N/A'}")
                
                if hasattr(balance_sheet, 'columns'):
                    # Look for total assets
                    asset_cols = [col for col in balance_sheet.columns if any(term in str(col).lower() for term in ['total assets', 'assets'])]
                    if asset_cols:
                        total_assets = safe_extract_value(balance_sheet[asset_cols[0]], ['iloc', 'value'])
                        if total_assets:
                            metrics['total_assets'] = total_assets
                            print(f"   🏢 Total Assets: ${total_assets:,.0f}")
                    
                    # Look for shareholders equity
                    equity_cols = [col for col in balance_sheet.columns if any(term in str(col).lower() for term in ['shareholders equity', 'stockholders equity', 'total equity'])]
                    if equity_cols:
                        equity = safe_extract_value(balance_sheet[equity_cols[0]], ['iloc', 'value'])
                        if equity:
                            metrics['shareholders_equity'] = equity
                            print(f"   🏦 Shareholders Equity: ${equity:,.0f}")
                    
                    # Look for cash
                    cash_cols = [col for col in balance_sheet.columns if any(term in str(col).lower() for term in ['cash', 'cash and equivalents'])]
                    if cash_cols:
                        cash = safe_extract_value(balance_sheet[cash_cols[0]], ['iloc', 'value'])
                        if cash:
                            metrics['cash'] = cash
                            print(f"   💵 Cash: ${cash:,.0f}")
        except Exception as e:
            print(f"❌ Balance Sheet Error: {e}")
        
        # Calculate Financial Ratios
        print(f"\n📊 CALCULATING INVESTMENT BANKING RATIOS")
        
        revenue = metrics.get('revenue')
        net_income = metrics.get('net_income')
        operating_income = metrics.get('operating_income')
        total_assets = metrics.get('total_assets')
        equity = metrics.get('shareholders_equity')
        
        if revenue and net_income:
            metrics['net_margin'] = (net_income / revenue) * 100
            print(f"   📈 Net Margin: {metrics['net_margin']:.1f}%")
        
        if revenue and operating_income:
            metrics['operating_margin'] = (operating_income / revenue) * 100
            print(f"   🏭 Operating Margin: {metrics['operating_margin']:.1f}%")
        
        if net_income and equity:
            metrics['roe'] = (net_income / equity) * 100
            print(f"   🎯 ROE: {metrics['roe']:.1f}%")
        
        if net_income and total_assets:
            metrics['roa'] = (net_income / total_assets) * 100
            print(f"   📊 ROA: {metrics['roa']:.1f}%")
        
        if revenue and total_assets:
            metrics['asset_turnover'] = revenue / total_assets
            print(f"   🔄 Asset Turnover: {metrics['asset_turnover']:.2f}x")
        
        # Try to get shares outstanding for per-share metrics
        try:
            shares_data = company.shares_outstanding_fact
            if shares_data:
                shares = safe_extract_value(shares_data, ['value', 'iloc'])
                if shares:
                    metrics['shares_outstanding'] = shares
                    print(f"   📊 Shares Outstanding: {shares:,.0f}")
                    
                    if net_income:
                        metrics['eps'] = net_income / shares
                        print(f"   💰 EPS: ${metrics['eps']:.2f}")
                    
                    if equity:
                        metrics['book_value_per_share'] = equity / shares
                        print(f"   📈 Book Value/Share: ${metrics['book_value_per_share']:.2f}")
        except Exception as e:
            print(f"   ⚠️  Shares Outstanding: {e}")
        
        metrics['extraction_timestamp'] = datetime.now().isoformat()
        print(f"\n✅ Successfully extracted comprehensive metrics for {ticker}")
        
        return metrics
        
    except Exception as e:
        print(f"\n❌ ERROR processing {ticker}: {e}")
        return {
            'company_info': {'ticker': ticker, 'name': company_name},
            'error': str(e),
            'extraction_timestamp': datetime.now().isoformat()
        }

def create_investment_banking_comps_table(companies_data):
    """Create professional investment banking comps table"""
    print(f"\n{'='*100}")
    print("🏦 INVESTMENT BANKING COMPARABLE COMPANIES ANALYSIS")
    print("📊 SEMICONDUCTOR SECTOR FINANCIAL METRICS")
    print('='*100)
    
    # Build comps table data
    comps_data = []
    
    for ticker, metrics in companies_data.items():
        if 'error' in metrics:
            print(f"⚠️  {ticker}: {metrics['error']}")
            continue
        
        # Extract financial metrics for comps table
        company_row = {
            'Ticker': ticker,
            'Company Name': metrics['company_info']['name'][:30],
            'Revenue ($M)': f"${metrics.get('revenue', 0)/1_000_000:,.0f}" if metrics.get('revenue') else 'N/A',
            'Net Income ($M)': f"${metrics.get('net_income', 0)/1_000_000:,.0f}" if metrics.get('net_income') else 'N/A',
            'Total Assets ($M)': f"${metrics.get('total_assets', 0)/1_000_000:,.0f}" if metrics.get('total_assets') else 'N/A',
            'Equity ($M)': f"${metrics.get('shareholders_equity', 0)/1_000_000:,.0f}" if metrics.get('shareholders_equity') else 'N/A',
            'Net Margin': f"{metrics.get('net_margin', 0):.1f}%" if metrics.get('net_margin') else 'N/A',
            'Operating Margin': f"{metrics.get('operating_margin', 0):.1f}%" if metrics.get('operating_margin') else 'N/A',
            'ROE': f"{metrics.get('roe', 0):.1f}%" if metrics.get('roe') else 'N/A',
            'ROA': f"{metrics.get('roa', 0):.1f}%" if metrics.get('roa') else 'N/A',
            'Asset Turnover': f"{metrics.get('asset_turnover', 0):.2f}x" if metrics.get('asset_turnover') else 'N/A',
            'EPS': f"${metrics.get('eps', 0):.2f}" if metrics.get('eps') else 'N/A'
        }
        comps_data.append(company_row)
    
    if comps_data:
        # Create and display comps table
        df = pd.DataFrame(comps_data)
        print(df.to_string(index=False, max_colwidth=15))
        
        # Save to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        csv_filename = f'Investment_Banking_Semiconductor_Comps_{timestamp}.csv'
        json_filename = f'Investment_Banking_Detailed_Metrics_{timestamp}.json'
        
        df.to_csv(csv_filename, index=False)
        with open(json_filename, 'w') as f:
            json.dump(companies_data, f, indent=2, default=str)
        
        print(f"\n🎯 INVESTMENT BANKING DELIVERABLES:")
        print(f"   📊 Comps Table (Excel Ready): {csv_filename}")
        print(f"   📋 Detailed Financial Metrics: {json_filename}")
        
        # Investment insights
        successful_extractions = len([d for d in comps_data if d['Revenue ($M)'] != 'N/A'])
        print(f"\n💡 INVESTMENT INSIGHTS:")
        print(f"   ✅ Successfully extracted financial data for {successful_extractions}/{len(comps_data)} companies")
        if successful_extractions >= 2:
            print(f"   🏆 Sufficient data for comprehensive comps analysis")
            print(f"   📈 Ready for valuation multiples and peer benchmarking")
        
        return df
    else:
        print("❌ No valid data extracted for comps table")
        return None

def main():
    """Main investment banking analysis"""
    print("🚀 INVESTMENT BANKING SEMICONDUCTOR COMPS MODEL")
    print("📊 Extracting comprehensive financial metrics for comps analysis")
    
    all_companies_data = {}
    
    # Extract financial data for all companies
    for ticker, company_name in COMPANIES.items():
        all_companies_data[ticker] = extract_financial_data(ticker, company_name)
    
    # Create investment banking comps table
    comps_df = create_investment_banking_comps_table(all_companies_data)
    
    print(f"\n🎯 INVESTMENT BANKING ANALYSIS COMPLETE!")
    print("Ready for pitch books, valuation models, and client presentations")
    
    return 0

if __name__ == "__main__":
    exit(main())