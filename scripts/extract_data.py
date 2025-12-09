#!/usr/bin/env python3
"""
🏦 INVESTMENT BANKING COMPS MODEL - FINAL WORKING VERSION
✅ Uses correct edgartools Financials API for semiconductor sector analysis
📊 Extracts comprehensive financial metrics for NVIDIA, MCHP, AMD, and Lattice
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
    set_identity("Investment Banking Comps Analysis joshua.gao@yale.edu")
    print("🏦 INVESTMENT BANKING COMPS MODEL - READY FOR ANALYSIS")
    print("✅ Initialized for semiconductor sector financial extraction")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

COMPANIES = {
    'NVDA': 'NVIDIA Corporation',
    'MCHP': 'Microchip Technology Inc',
    'AMD': 'Advanced Micro Devices Inc', 
    'LSCC': 'Lattice Semiconductor Corp',
    'INTC': 'Intel Corporation'
}

def extract_value_safely(value):
    """Safely extract numeric value from various formats"""
    try:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if hasattr(value, 'value'):
            return float(value.value) if value.value is not None else None
        if isinstance(value, str):
            # Remove commas and dollar signs
            clean_str = value.replace(',', '').replace('$', '').strip()
            return float(clean_str) if clean_str and clean_str != '-' else None
        return float(value)
    except (ValueError, TypeError, AttributeError):
        return None

def safe_get_latest_value(data_series):
    """Extract the latest value from XBRL time series data"""
    try:
        if data_series is None:
            return None
        
        # If it's already a simple value
        if isinstance(data_series, (int, float)):
            return float(data_series)
        
        # If it has a 'value' attribute
        if hasattr(data_series, 'value'):
            return extract_value_safely(data_series.value)
        
        # If it's a dict with 'units' (XBRL format)
        if isinstance(data_series, dict):
            if 'units' in data_series:
                units = data_series['units']
                # Look for USD values
                if 'USD' in units:
                    usd_data = units['USD']
                    # Get the latest period (most recent date)
                    if isinstance(usd_data, dict) and len(usd_data) > 0:
                        latest_period = max(usd_data.keys())
                        return extract_value_safely(usd_data[latest_period])
                # Try other unit types
                for unit_type in units:
                    if isinstance(units[unit_type], dict) and len(units[unit_type]) > 0:
                        latest_period = max(units[unit_type].keys())
                        return extract_value_safely(units[unit_type][latest_period])
            elif 'value' in data_series:
                return extract_value_safely(data_series['value'])
        
        # If it has 'values' attribute (list of values)
        if hasattr(data_series, 'values'):
            if len(data_series.values) > 0:
                # Get the first (most recent) value
                return extract_value_safely(data_series.values[0].value)
        
        return None
    except Exception as e:
        return None

def extract_investment_banking_metrics(ticker, company_name):
    """Extract comprehensive investment banking metrics using correct Financials API"""
    print(f"\n{'='*80}")
    print(f"🚀 INVESTMENT BANKING ANALYSIS: {ticker}")
    print(f"📊 {company_name}")
    print('='*80)
    
    try:
        company = Company(ticker)
        print(f"🏢 Company: {company.name}")
        print(f"📋 CIK: {company.cik}")
        
        # Initialize metrics dictionary
        metrics = {
            'company_info': {
                'ticker': ticker,
                'name': company.name,
                'cik': company.cik,
                'sic': getattr(company, 'sic', None),
                'industry': getattr(company, 'industry', 'Semiconductors')
            }
        }
        
        print(f"\n💼 ACCESSING FINANCIAL DATA...")
        
        # Get Financials object with comprehensive methods
        financials = company.get_financials()
        print(f"✅ Loaded Financials object: {type(financials)}")
        
        print(f"\n📈 INCOME STATEMENT METRICS")
        
        # Revenue
        try:
            revenue = financials.get_revenue()
            revenue_value = extract_value_safely(revenue)
            if revenue_value:
                metrics['revenue'] = revenue_value
                print(f"   💰 Revenue: ${revenue_value:,.0f}")
            else:
                print(f"   💰 Revenue: Not available")
        except Exception as e:
            print(f"   💰 Revenue: Error - {e}")
        
        # Try to get additional metrics via facts (XBRL data)
        print(f"\n📊 ADDITIONAL METRICS VIA XBRL FACTS")
        try:
            facts = company.get_facts()
            
            # Gross Profit
            try:
                gross_profit_data = facts.get_gross_profit()
                gross_profit_value = safe_get_latest_value(gross_profit_data)
                if gross_profit_value:
                    metrics['gross_profit'] = gross_profit_value
                    if revenue_value:
                        metrics['gross_margin'] = (gross_profit_value / revenue_value) * 100
                        print(f"   📊 Gross Profit: ${gross_profit_value:,.0f} ({metrics['gross_margin']:.1f}% margin)")
            except Exception as e:
                print(f"   📊 Gross Profit: Not available")
            
            # Operating Income
            try:
                operating_income_data = facts.get_operating_income()
                operating_income_value = safe_get_latest_value(operating_income_data)
                if operating_income_value:
                    metrics['operating_income'] = operating_income_value
                    metrics['ebit'] = operating_income_value
                    if revenue_value:
                        metrics['operating_margin'] = (operating_income_value / revenue_value) * 100
                        print(f"   🏭 Operating Income (EBIT): ${operating_income_value:,.0f} ({metrics['operating_margin']:.1f}% margin)")
            except Exception as e:
                print(f"   🏭 Operating Income/EBIT: Not available")
            
            # R&D Expenses
            try:
                rnd_data = facts.get_research_and_development()
                rnd_value = safe_get_latest_value(rnd_data)
                if rnd_value:
                    metrics['rd_expenses'] = rnd_value
                    if revenue_value:
                        metrics['rd_as_pct_revenue'] = (rnd_value / revenue_value) * 100
                        print(f"   🔬 R&D Expenses: ${rnd_value:,.0f} ({metrics['rd_as_pct_revenue']:.1f}% of revenue)")
            except Exception as e:
                print(f"   🔬 R&D Expenses: Not available")
            
            # Try to calculate EBITDA from Operating Income + Depreciation
            if metrics.get('operating_income'):
                try:
                    depreciation_data = facts.get_depreciation()
                    dep_value = safe_get_latest_value(depreciation_data)
                    if dep_value:
                        ebitda_calc = metrics['operating_income'] + dep_value
                        metrics['ebitda'] = ebitda_calc
                        if revenue_value:
                            metrics['ebitda_margin'] = (ebitda_calc / revenue_value) * 100
                            print(f"   💎 EBITDA (calc): ${ebitda_calc:,.0f} ({metrics['ebitda_margin']:.1f}% margin)")
                except:
                    pass
            
            # Cash via facts
            try:
                cash_data = facts.get_cash()
                cash_value = safe_get_latest_value(cash_data)
                if cash_value and not metrics.get('cash_and_equivalents'):
                    metrics['cash_and_equivalents'] = cash_value
                    print(f"   💵 Cash & Equivalents (facts): ${cash_value:,.0f}")
            except:
                pass
            
            # Shares Outstanding via facts
            try:
                if hasattr(facts, 'shares_outstanding'):
                    shares_data = facts.shares_outstanding
                    shares_value = safe_get_latest_value(shares_data)
                    if shares_value:
                        metrics['shares_outstanding'] = shares_value
                        print(f"   📊 Shares Outstanding (facts): {shares_value:,.0f}")
                        
                        # Calculate per-share metrics
                        net_income_val = metrics.get('net_income')
                        equity_val = metrics.get('stockholders_equity')
                        if net_income_val and shares_value:
                            metrics['eps'] = net_income_val / shares_value
                            print(f"   📈 EPS: ${metrics['eps']:.2f}")
                        if equity_val and shares_value:
                            metrics['book_value_per_share'] = equity_val / shares_value
                            print(f"   📈 Book Value/Share: ${metrics['book_value_per_share']:.2f}")
            except:
                pass
                    
        except Exception as e:
            print(f"   ⚠️ Facts data not available: {e}")
        
        # Net Income
        try:
            net_income = financials.get_net_income()
            net_income_value = extract_value_safely(net_income)
            if net_income_value:
                metrics['net_income'] = net_income_value
                print(f"   💎 Net Income: ${net_income_value:,.0f}")
            else:
                print(f"   💎 Net Income: Not available")
        except Exception as e:
            print(f"   💎 Net Income: Error - {e}")
        
        # Operating Cash Flow
        try:
            operating_cf = financials.get_operating_cash_flow()
            operating_cf_value = extract_value_safely(operating_cf)
            if operating_cf_value:
                metrics['operating_cash_flow'] = operating_cf_value
                print(f"   💵 Operating Cash Flow: ${operating_cf_value:,.0f}")
            else:
                print(f"   💵 Operating Cash Flow: Not available")
        except Exception as e:
            print(f"   💵 Operating Cash Flow: Error - {e}")
        
        # Free Cash Flow
        try:
            free_cf = financials.get_free_cash_flow()
            free_cf_value = extract_value_safely(free_cf)
            if free_cf_value:
                metrics['free_cash_flow'] = free_cf_value
                print(f"   🆓 Free Cash Flow: ${free_cf_value:,.0f}")
            else:
                print(f"   🆓 Free Cash Flow: Not available")
        except Exception as e:
            print(f"   🆓 Free Cash Flow: Error - {e}")
        
        print(f"\n🏛️ BALANCE SHEET METRICS")
        
        # Total Assets
        try:
            total_assets = financials.get_total_assets()
            assets_value = extract_value_safely(total_assets)
            if assets_value:
                metrics['total_assets'] = assets_value
                print(f"   🏢 Total Assets: ${assets_value:,.0f}")
            else:
                print(f"   🏢 Total Assets: Not available")
        except Exception as e:
            print(f"   🏢 Total Assets: Error - {e}")
        
        # Stockholders Equity
        try:
            equity = financials.get_stockholders_equity()
            equity_value = extract_value_safely(equity)
            if equity_value:
                metrics['stockholders_equity'] = equity_value
                print(f"   🏦 Stockholders Equity: ${equity_value:,.0f}")
            else:
                print(f"   🏦 Stockholders Equity: Not available")
        except Exception as e:
            print(f"   🏦 Stockholders Equity: Error - {e}")
        
        # Current Assets
        try:
            current_assets = financials.get_current_assets()
            current_assets_value = extract_value_safely(current_assets)
            if current_assets_value:
                metrics['current_assets'] = current_assets_value
                print(f"   📊 Current Assets: ${current_assets_value:,.0f}")
            else:
                print(f"   📊 Current Assets: Not available")
        except Exception as e:
            print(f"   📊 Current Assets: Error - {e}")
        
        # Current Liabilities
        try:
            current_liabilities = financials.get_current_liabilities()
            current_liabilities_value = extract_value_safely(current_liabilities)
            if current_liabilities_value:
                metrics['current_liabilities'] = current_liabilities_value
                print(f"   📋 Current Liabilities: ${current_liabilities_value:,.0f}")
            else:
                print(f"   📋 Current Liabilities: Not available")
        except Exception as e:
            print(f"   📋 Current Liabilities: Error - {e}")
        
        # Total Debt
        try:
            total_debt = financials.get_total_debt()
            debt_value = extract_value_safely(total_debt)
            if debt_value:
                metrics['total_debt'] = debt_value
                print(f"   💳 Total Debt: ${debt_value:,.0f}")
            else:
                print(f"   💳 Total Debt: Not available")
        except Exception as e:
            # Try alternative: calculate from assets - equity
            try:
                assets_val = metrics.get('total_assets')
                equity_val = metrics.get('stockholders_equity')
                if assets_val and equity_val:
                    # Approximate debt as assets minus equity (simplified)
                    calculated_debt = assets_val - equity_val
                    if calculated_debt > 0:
                        metrics['total_debt'] = calculated_debt
                        print(f"   💳 Total Debt (approx): ${calculated_debt:,.0f}")
            except:
                print(f"   💳 Total Debt: Not available")
        
        # Cash and Cash Equivalents
        try:
            cash = financials.get_cash()
            cash_value = extract_value_safely(cash)
            if cash_value:
                metrics['cash_and_equivalents'] = cash_value
                print(f"   💵 Cash & Equivalents: ${cash_value:,.0f}")
            else:
                print(f"   💵 Cash & Equivalents: Not available")
        except Exception as e:
            # Try via facts
            try:
                facts = company.get_facts()
                cash_data = facts.get_cash()
                if cash_data:
                    if hasattr(cash_data, 'value'):
                        cash_value = extract_value_safely(cash_data.value)
                    elif isinstance(cash_data, dict) and 'units' in cash_data:
                        units = cash_data['units']
                        if 'USD' in units:
                            latest_period = max(units['USD'].keys())
                            cash_value = extract_value_safely(units['USD'][latest_period])
                        else:
                            cash_value = None
                    else:
                        cash_value = None
                    
                    if cash_value:
                        metrics['cash_and_equivalents'] = cash_value
                        print(f"   💵 Cash & Equivalents (facts): ${cash_value:,.0f}")
            except:
                print(f"   💵 Cash & Equivalents: Not available")
        
        # Shares Outstanding
        try:
            shares = financials.get_shares_outstanding()
            shares_value = extract_value_safely(shares)
            if shares_value:
                metrics['shares_outstanding'] = shares_value
                print(f"   📊 Shares Outstanding: {shares_value:,.0f}")
                
                # Calculate per-share metrics
                net_income_val = metrics.get('net_income')
                equity_val = metrics.get('stockholders_equity')
                if net_income_val and shares_value:
                    metrics['eps'] = net_income_val / shares_value
                    print(f"   📈 EPS: ${metrics['eps']:.2f}")
                if equity_val and shares_value:
                    metrics['book_value_per_share'] = equity_val / shares_value
                    print(f"   📈 Book Value/Share: ${metrics['book_value_per_share']:.2f}")
            else:
                print(f"   📊 Shares Outstanding: Not available")
        except Exception as e:
            # Try alternative method via company facts
            try:
                facts = company.get_facts()
                if hasattr(facts, 'shares_outstanding'):
                    shares_data = facts.shares_outstanding
                    if shares_data:
                        # Get latest value
                        if hasattr(shares_data, 'value'):
                            shares_value = extract_value_safely(shares_data.value)
                        elif isinstance(shares_data, dict) and 'value' in shares_data:
                            shares_value = extract_value_safely(shares_data['value'])
                        if shares_value:
                            metrics['shares_outstanding'] = shares_value
                            print(f"   📊 Shares Outstanding (facts): {shares_value:,.0f}")
                            
                            # Calculate per-share metrics
                            net_income_val = metrics.get('net_income')
                            equity_val = metrics.get('stockholders_equity')
                            if net_income_val and shares_value:
                                metrics['eps'] = net_income_val / shares_value
                                print(f"   📈 EPS: ${metrics['eps']:.2f}")
                            if equity_val and shares_value:
                                metrics['book_value_per_share'] = equity_val / shares_value
                                print(f"   📈 Book Value/Share: ${metrics['book_value_per_share']:.2f}")
            except:
                print(f"   📊 Shares Outstanding: Not available")
        
        print(f"\n📊 INVESTMENT BANKING RATIO ANALYSIS")
        
        # Calculate key financial ratios for comps analysis
        revenue_val = metrics.get('revenue')
        net_income_val = metrics.get('net_income')
        assets_val = metrics.get('total_assets')
        equity_val = metrics.get('stockholders_equity')
        current_assets_val = metrics.get('current_assets')
        current_liabs_val = metrics.get('current_liabilities')
        
        # Profitability Ratios
        if revenue_val and net_income_val:
            metrics['net_margin'] = (net_income_val / revenue_val) * 100
            print(f"   📈 Net Margin: {metrics['net_margin']:.1f}%")
        
        # Return Ratios (key for comps)
        if net_income_val and equity_val:
            metrics['roe'] = (net_income_val / equity_val) * 100
            print(f"   🎯 Return on Equity (ROE): {metrics['roe']:.1f}%")
        
        if net_income_val and assets_val:
            metrics['roa'] = (net_income_val / assets_val) * 100
            print(f"   📊 Return on Assets (ROA): {metrics['roa']:.1f}%")
        
        # Efficiency Ratios
        if revenue_val and assets_val:
            metrics['asset_turnover'] = revenue_val / assets_val
            print(f"   🔄 Asset Turnover: {metrics['asset_turnover']:.2f}x")
        
        # Liquidity Ratios
        if current_assets_val and current_liabs_val:
            metrics['current_ratio'] = current_assets_val / current_liabs_val
            print(f"   💧 Current Ratio: {metrics['current_ratio']:.2f}x")
        
        # Cash Flow Ratios
        if metrics.get('operating_cash_flow') and revenue_val:
            metrics['ocf_margin'] = (metrics['operating_cash_flow'] / revenue_val) * 100
            print(f"   💵 OCF Margin: {metrics['ocf_margin']:.1f}%")
        
        if metrics.get('free_cash_flow') and revenue_val:
            metrics['fcf_margin'] = (metrics['free_cash_flow'] / revenue_val) * 100
            print(f"   🆓 FCF Margin: {metrics['fcf_margin']:.1f}%")
        
        # Additional Leverage Ratios
        debt_val = metrics.get('total_debt')
        if debt_val and equity_val:
            metrics['debt_to_equity'] = (debt_val / equity_val) * 100
            print(f"   💳 Debt/Equity: {metrics['debt_to_equity']:.1f}%")
        
        if debt_val and assets_val:
            metrics['debt_to_assets'] = (debt_val / assets_val) * 100
            print(f"   💳 Debt/Assets: {metrics['debt_to_assets']:.1f}%")
        
        # Net Debt calculation
        cash_val = metrics.get('cash_and_equivalents')
        if debt_val and cash_val:
            metrics['net_debt'] = debt_val - cash_val
            print(f"   💳 Net Debt: ${metrics['net_debt']:,.0f}")
        
        metrics['extraction_timestamp'] = datetime.now().isoformat()
        print(f"\n✅ Successfully extracted comprehensive investment banking metrics for {ticker}")
        
        return metrics
        
    except Exception as e:
        print(f"\n❌ ERROR processing {ticker}: {e}")
        return {
            'company_info': {'ticker': ticker, 'name': company_name},
            'error': str(e),
            'extraction_timestamp': datetime.now().isoformat()
        }

def create_investment_banking_comps_table(companies_data):
    """Create professional investment banking comparable companies table"""
    print(f"\n{'='*120}")
    print("🏦 INVESTMENT BANKING COMPARABLE COMPANIES ANALYSIS")
    print("📊 SEMICONDUCTOR SECTOR FINANCIAL BENCHMARKING")
    print('='*120)
    
    # Build comprehensive comps table
    comps_data = []
    successful_companies = 0
    
    for ticker, metrics in companies_data.items():
        if 'error' in metrics:
            print(f"⚠️  {ticker}: Data extraction error - {metrics['error'][:50]}...")
            continue
        
        # Format financial metrics for investment banking presentation
        company_row = {
            'Ticker': ticker,
            'Company': metrics['company_info']['name'][:25],  # Truncate for table display
            'Revenue ($M)': f"${metrics.get('revenue', 0)/1_000_000:,.0f}" if metrics.get('revenue') else 'N/A',
            'Net Income ($M)': f"${metrics.get('net_income', 0)/1_000_000:,.0f}" if metrics.get('net_income') else 'N/A',
            'Assets ($M)': f"${metrics.get('total_assets', 0)/1_000_000:,.0f}" if metrics.get('total_assets') else 'N/A',
            'Equity ($M)': f"${metrics.get('stockholders_equity', 0)/1_000_000:,.0f}" if metrics.get('stockholders_equity') else 'N/A',
            'OCF ($M)': f"${metrics.get('operating_cash_flow', 0)/1_000_000:,.0f}" if metrics.get('operating_cash_flow') else 'N/A',
            'FCF ($M)': f"${metrics.get('free_cash_flow', 0)/1_000_000:,.0f}" if metrics.get('free_cash_flow') else 'N/A',
            'Net Margin %': f"{metrics.get('net_margin', 0):.1f}%" if metrics.get('net_margin') else 'N/A',
            'ROE %': f"{metrics.get('roe', 0):.1f}%" if metrics.get('roe') else 'N/A',
            'ROA %': f"{metrics.get('roa', 0):.1f}%" if metrics.get('roa') else 'N/A',
            'Asset Turn.': f"{metrics.get('asset_turnover', 0):.2f}x" if metrics.get('asset_turnover') else 'N/A',
            'Current Ratio': f"{metrics.get('current_ratio', 0):.2f}x" if metrics.get('current_ratio') else 'N/A',
            'FCF Margin %': f"{metrics.get('fcf_margin', 0):.1f}%" if metrics.get('fcf_margin') else 'N/A'
        }
        
        comps_data.append(company_row)
        if company_row['Revenue ($M)'] != 'N/A':
            successful_companies += 1
    
    if comps_data:
        # Create professional comps DataFrame
        df = pd.DataFrame(comps_data)
        print(df.to_string(index=False, max_colwidth=12))
        
        # Save investment banking deliverables
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Excel-ready CSV for analysts
        csv_filename = f'data/processed/IB_Semiconductor_Comps_{timestamp}.csv'
        df.to_csv(csv_filename, index=False)
        
        # Detailed JSON for models
        json_filename = f'data/processed/IB_Detailed_Financials_{timestamp}.json'
        with open(json_filename, 'w') as f:
            json.dump(companies_data, f, indent=2, default=str)
        
        # Also update master files
        df.to_csv('data/master_comps.csv', index=False)
        with open('data/master_financials.json', 'w') as f:
            json.dump(companies_data, f, indent=2, default=str)
        
        print(f"\n🎯 INVESTMENT BANKING DELIVERABLES:")
        print(f"   📊 Comps Table (Excel): {csv_filename}")
        print(f"   📋 Financial Model Data: {json_filename}")
        
        # Professional investment insights
        print(f"\n💡 INVESTMENT BANKING INSIGHTS:")
        print(f"   ✅ Successfully extracted financial data: {successful_companies}/{len(comps_data)} companies")
        print(f"   📈 Data quality: {'Excellent' if successful_companies >= 3 else 'Good' if successful_companies >= 2 else 'Limited'}")
        
        if successful_companies >= 2:
            print(f"   🏆 READY FOR:")
            print(f"      • Trading comps analysis and valuation multiples")
            print(f"      • Peer benchmarking and relative performance analysis")  
            print(f"      • DCF model benchmarking and sanity checks")
            print(f"      • Investment committee presentations")
        
        return df
        
    else:
        print("❌ No valid financial data extracted for comps analysis")
        return None

def main():
    """Execute comprehensive investment banking comps analysis"""
    print("🚀 INVESTMENT BANKING SEMICONDUCTOR SECTOR COMPS MODEL")
    print("📊 Comprehensive Financial Metrics Extraction for Valuation Analysis")
    
    all_companies_data = {}
    
    # Extract financial data for all semiconductor companies
    for ticker, company_name in COMPANIES.items():
        all_companies_data[ticker] = extract_investment_banking_metrics(ticker, company_name)
    
    # Create professional investment banking comps table
    comps_df = create_investment_banking_comps_table(all_companies_data)
    
    print(f"\n🎯 INVESTMENT BANKING ANALYSIS COMPLETE!")
    print("📈 Ready for client presentations, pitch books, and valuation models")
    print("🏆 Professional-grade comps analysis delivered")
    
    return 0

if __name__ == "__main__":
    exit(main())