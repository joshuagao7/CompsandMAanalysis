#!/usr/bin/env python3
"""
Investment Banking Comps Model - FIXED VERSION
Extracts comprehensive financial metrics using correct XBRL API methods
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
    print("✓ Investment Banking Comps Model initialized")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

COMPANIES = {
    'NVDA': 'NVIDIA Corporation',
    'MCHP': 'Microchip Technology Inc',
    'AMD': 'Advanced Micro Devices Inc', 
    'LSCC': 'Lattice Semiconductor Corp'
}

class InvestmentBankingCompsModel:
    def __init__(self):
        self.companies_data = {}
    
    def safe_get_latest_value(self, data_series):
        """Safely extract the latest value from a data series"""
        try:
            if data_series is not None and hasattr(data_series, 'values') and len(data_series.values) > 0:
                # Get the most recent value
                latest = data_series.values[0]
                if hasattr(latest, 'value') and latest.value is not None:
                    return float(latest.value)
            return None
        except Exception as e:
            return None
    
    def extract_financial_metrics(self, ticker, company_name):
        """Extract comprehensive financial metrics using correct XBRL API"""
        print(f"\n{'='*70}")
        print(f"🏦 INVESTMENT BANKING ANALYSIS - {ticker}")
        print(f"📊 {company_name}")
        print('='*70)
        
        try:
            company = Company(ticker)
            facts = company.get_facts()
            
            if not facts:
                print("❌ No XBRL facts available")
                return None
            
            print(f"✅ Loaded {len(facts)} XBRL facts")
            
            # Initialize metrics
            metrics = {
                'company_info': {
                    'ticker': ticker,
                    'name': company.name,
                    'cik': company.cik,
                    'sic': getattr(company, 'sic', None)
                }
            }
            
            print(f"\n📈 INCOME STATEMENT ANALYSIS")
            
            # Revenue
            try:
                revenue_data = facts.get_revenue()
                revenue = self.safe_get_latest_value(revenue_data)
                if revenue:
                    metrics['revenue'] = revenue
                    print(f"  💰 Revenue: ${revenue:,.0f}")
                else:
                    print("  💰 Revenue: Not available")
            except Exception as e:
                print(f"  💰 Revenue: Error - {e}")
            
            # Gross Profit
            try:
                gross_profit_data = facts.get_gross_profit()
                gross_profit = self.safe_get_latest_value(gross_profit_data)
                if gross_profit and revenue:
                    metrics['gross_profit'] = gross_profit
                    metrics['gross_margin'] = (gross_profit / revenue) * 100
                    print(f"  📊 Gross Profit: ${gross_profit:,.0f}")
                    print(f"  📊 Gross Margin: {metrics['gross_margin']:.1f}%")
                else:
                    print("  📊 Gross Profit: Not available")
            except Exception as e:
                print(f"  📊 Gross Profit: Error - {e}")
            
            # Operating Income
            try:
                operating_income_data = facts.get_operating_income()
                operating_income = self.safe_get_latest_value(operating_income_data)
                if operating_income:
                    metrics['operating_income'] = operating_income
                    if revenue:
                        metrics['operating_margin'] = (operating_income / revenue) * 100
                        print(f"  🏭 Operating Income: ${operating_income:,.0f}")
                        print(f"  🏭 Operating Margin: {metrics['operating_margin']:.1f}%")
                    else:
                        print(f"  🏭 Operating Income: ${operating_income:,.0f}")
                else:
                    print("  🏭 Operating Income: Not available")
            except Exception as e:
                print(f"  🏭 Operating Income: Error - {e}")
            
            # Net Income
            try:
                net_income_data = facts.get_net_income()
                net_income = self.safe_get_latest_value(net_income_data)
                if net_income:
                    metrics['net_income'] = net_income
                    if revenue:
                        metrics['net_margin'] = (net_income / revenue) * 100
                        print(f"  💎 Net Income: ${net_income:,.0f}")
                        print(f"  💎 Net Margin: {metrics['net_margin']:.1f}%")
                    else:
                        print(f"  💎 Net Income: ${net_income:,.0f}")
                else:
                    print("  💎 Net Income: Not available")
            except Exception as e:
                print(f"  💎 Net Income: Error - {e}")
            
            print(f"\n🏛️ BALANCE SHEET ANALYSIS")
            
            # Total Assets
            try:
                total_assets_data = facts.get_total_assets()
                total_assets = self.safe_get_latest_value(total_assets_data)
                if total_assets:
                    metrics['total_assets'] = total_assets
                    print(f"  🏢 Total Assets: ${total_assets:,.0f}")
                else:
                    print("  🏢 Total Assets: Not available")
            except Exception as e:
                print(f"  🏢 Total Assets: Error - {e}")
            
            # Shareholders Equity
            try:
                equity_data = facts.get_shareholders_equity()
                equity = self.safe_get_latest_value(equity_data)
                if equity:
                    metrics['shareholders_equity'] = equity
                    print(f"  🏦 Shareholders' Equity: ${equity:,.0f}")
                else:
                    print("  🏦 Shareholders' Equity: Not available")
            except Exception as e:
                print(f"  🏦 Shareholders' Equity: Error - {e}")
            
            # Shares Outstanding
            try:
                shares_data = facts.shares_outstanding
                shares = self.safe_get_latest_value(shares_data)
                if shares:
                    metrics['shares_outstanding'] = shares
                    print(f"  📊 Shares Outstanding: {shares:,.0f}")
                    
                    # Calculate per-share metrics
                    if equity:
                        metrics['book_value_per_share'] = equity / shares
                        print(f"  📈 Book Value/Share: ${metrics['book_value_per_share']:.2f}")
                        
                    if net_income:
                        metrics['eps'] = net_income / shares
                        print(f"  💰 EPS: ${metrics['eps']:.2f}")
                else:
                    print("  📊 Shares Outstanding: Not available")
            except Exception as e:
                print(f"  📊 Shares Outstanding: Error - {e}")
            
            print(f"\n🔍 FINANCIAL RATIO ANALYSIS")
            
            # Calculate key ratios
            if net_income and equity:
                metrics['roe'] = (net_income / equity) * 100
                print(f"  📊 Return on Equity (ROE): {metrics['roe']:.1f}%")
            
            if net_income and total_assets:
                metrics['roa'] = (net_income / total_assets) * 100
                print(f"  📈 Return on Assets (ROA): {metrics['roa']:.1f}%")
            
            if revenue and total_assets:
                metrics['asset_turnover'] = revenue / total_assets
                print(f"  🔄 Asset Turnover: {metrics['asset_turnover']:.2f}x")
            
            metrics['extraction_timestamp'] = datetime.now().isoformat()
            print(f"\n✅ Successfully extracted metrics for {ticker}")
            
            return metrics
            
        except Exception as e:
            print(f"\n❌ Error processing {ticker}: {e}")
            return {
                'company_info': {'ticker': ticker, 'name': company_name},
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    def create_investment_banking_comps_table(self):
        """Create professional investment banking comps table"""
        print(f"\n{'='*100}")
        print("🏦 INVESTMENT BANKING COMPARABLE COMPANIES ANALYSIS")
        print("📊 SEMICONDUCTOR SECTOR COMPS MODEL")
        print('='*100)
        
        # Prepare data for comps table
        comps_data = []
        
        for ticker, metrics in self.companies_data.items():
            if 'error' in metrics:
                continue
            
            # Format all metrics for professional presentation
            company_data = {
                'Ticker': ticker,
                'Company Name': metrics['company_info']['name'][:25],  # Truncate long names
                'Revenue ($M)': f"${metrics.get('revenue', 0)/1_000_000:,.0f}" if metrics.get('revenue') else 'N/A',
                'Gross Margin': f"{metrics.get('gross_margin', 0):.1f}%" if metrics.get('gross_margin') else 'N/A',
                'EBIT Margin': f"{metrics.get('operating_margin', 0):.1f}%" if metrics.get('operating_margin') else 'N/A',
                'Net Margin': f"{metrics.get('net_margin', 0):.1f}%" if metrics.get('net_margin') else 'N/A',
                'Total Assets ($M)': f"${metrics.get('total_assets', 0)/1_000_000:,.0f}" if metrics.get('total_assets') else 'N/A',
                'Equity ($M)': f"${metrics.get('shareholders_equity', 0)/1_000_000:,.0f}" if metrics.get('shareholders_equity') else 'N/A',
                'ROE': f"{metrics.get('roe', 0):.1f}%" if metrics.get('roe') else 'N/A',
                'ROA': f"{metrics.get('roa', 0):.1f}%" if metrics.get('roa') else 'N/A',
                'Asset Turnover': f"{metrics.get('asset_turnover', 0):.2f}x" if metrics.get('asset_turnover') else 'N/A',
                'EPS': f"${metrics.get('eps', 0):.2f}" if metrics.get('eps') else 'N/A',
                'Book Value/Share': f"${metrics.get('book_value_per_share', 0):.2f}" if metrics.get('book_value_per_share') else 'N/A'
            }
            comps_data.append(company_data)
        
        if comps_data:
            # Create professional DataFrame
            df = pd.DataFrame(comps_data)
            print(df.to_string(index=False))
            
            # Save to multiple formats for banker presentation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            
            # CSV for Excel import
            csv_filename = f'IB_Semiconductor_Comps_{timestamp}.csv'
            df.to_csv(csv_filename, index=False)
            
            # JSON for data analysis
            json_filename = f'IB_Semiconductor_Metrics_{timestamp}.json'
            with open(json_filename, 'w') as f:
                json.dump(self.companies_data, f, indent=2, default=str)
            
            print(f"\n💼 INVESTMENT BANKING DELIVERABLES:")
            print(f"   📊 Comps Table: {csv_filename}")
            print(f"   📋 Detailed Metrics: {json_filename}")
            
            # Print key insights
            self.print_investment_insights(comps_data)
            
            return df
        else:
            print("❌ No valid data for comps analysis")
            return None
    
    def print_investment_insights(self, comps_data):
        """Print key investment banking insights"""
        print(f"\n🎯 KEY INVESTMENT INSIGHTS:")
        
        # Find companies with data for comparison
        valid_companies = [c for c in comps_data if c['Revenue ($M)'] != 'N/A']
        
        if len(valid_companies) >= 2:
            print(f"  📊 {len(valid_companies)} companies have complete financial data")
            print(f"  🏆 Ready for detailed comps analysis and valuation modeling")
            print(f"  💡 Suitable for DCF, trading comps, and transaction comps analysis")
        else:
            print(f"  ⚠️  Limited data available for comprehensive comps analysis")
            print(f"  💡 Consider supplementing with additional data sources")
    
    def run_investment_banking_analysis(self):
        """Run complete investment banking analysis"""
        print("🚀 STARTING INVESTMENT BANKING COMPS MODEL ANALYSIS")
        print("📊 Semiconductor Sector Deep Dive")
        
        # Extract metrics for all companies
        for ticker, company_name in COMPANIES.items():
            self.companies_data[ticker] = self.extract_financial_metrics(ticker, company_name)
        
        # Create professional comps table
        comps_df = self.create_investment_banking_comps_table()
        
        print(f"\n🎯 ANALYSIS COMPLETE!")
        print("Ready for investment banking presentation and valuation modeling")
        
        return self.companies_data, comps_df

def main():
    """Main function"""
    model = InvestmentBankingCompsModel()
    companies_data, comps_df = model.run_investment_banking_analysis()
    return 0

if __name__ == "__main__":
    exit(main())