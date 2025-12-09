#!/usr/bin/env python3
"""
Investment Banking Comps Model Data Extractor
Extracts comprehensive financial metrics for NVIDIA, MCHP, AMD, and Lattice Semiconductor
for comparable company analysis
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Add the pipx edgartools site-packages to path
pipx_site_packages = "/Users/joshuagao/.local/pipx/venvs/edgartools/lib/python3.14/site-packages"
sys.path.insert(0, pipx_site_packages)

try:
    from edgar import Company, set_identity
    set_identity("Investment Banking Analysis joshua.gao@yale.edu")
    print("✓ Successfully imported edgar module for investment banking analysis")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Semiconductor companies for comps analysis
COMPANIES = {
    'NVDA': 'NVIDIA Corporation',
    'MCHP': 'Microchip Technology Inc',
    'AMD': 'Advanced Micro Devices Inc', 
    'LSCC': 'Lattice Semiconductor Corp'
}

# Key XBRL tags for financial metrics (common variations)
REVENUE_TAGS = [
    'Revenues', 'Revenue', 'TotalRevenue', 'SalesRevenue', 'NetRevenue',
    'RevenueFromContractWithCustomerExcludingAssessedTax'
]

GROSS_PROFIT_TAGS = [
    'GrossProfit', 'GrossProfitLoss'
]

OPERATING_INCOME_TAGS = [
    'OperatingIncomeLoss', 'IncomeLossFromOperations', 'OperatingIncome'
]

NET_INCOME_TAGS = [
    'NetIncomeLoss', 'ProfitLoss', 'NetIncomeLossAvailableToCommonStockholdersBasic',
    'NetIncomeLossAvailableToCommonStockholders'
]

TOTAL_ASSETS_TAGS = [
    'Assets', 'AssetsCurrent', 'TotalAssets'
]

TOTAL_DEBT_TAGS = [
    'LongTermDebt', 'DebtCurrent', 'DebtNoncurrent', 'TotalDebt'
]

CASH_TAGS = [
    'CashAndCashEquivalentsAtCarryingValue', 'Cash', 'CashCashEquivalentsAndShortTermInvestments'
]

EQUITY_TAGS = [
    'StockholdersEquity', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'
]

SHARES_OUTSTANDING_TAGS = [
    'CommonStockSharesOutstanding', 'SharesOutstanding', 'WeightedAverageNumberOfSharesOutstandingBasic'
]

EPS_TAGS = [
    'EarningsPerShareBasic', 'EarningsPerShareDiluted'
]

class CompsModelExtractor:
    def __init__(self):
        self.companies_data = {}
        self.metrics_data = defaultdict(dict)
    
    def find_metric_value(self, facts, tag_list, period_filter=None):
        """Find a metric value from XBRL facts using multiple possible tags"""
        for tag in tag_list:
            try:
                # Try different case variations
                for tag_variant in [tag, tag.lower(), tag.upper()]:
                    if hasattr(facts, tag_variant):
                        fact = getattr(facts, tag_variant)
                        if hasattr(fact, 'values') and len(fact.values) > 0:
                            # Get the most recent annual value
                            for value in fact.values:
                                if hasattr(value, 'period') and hasattr(value, 'value'):
                                    # Prefer annual periods over quarterly
                                    if period_filter and period_filter in str(value.period):
                                        return float(value.value) if value.value else None
                                    elif not period_filter:
                                        return float(value.value) if value.value else None
                            # Fallback to first value if no period match
                            if fact.values[0].value is not None:
                                return float(fact.values[0].value)
            except Exception as e:
                continue
        return None
    
    def extract_company_metrics(self, ticker, company_name):
        """Extract comprehensive financial metrics for a company"""
        print(f"\n{'='*60}")
        print(f"EXTRACTING METRICS FOR {ticker} - {company_name}")
        print('='*60)
        
        try:
            company = Company(ticker)
            print(f"Company: {company.name}")
            print(f"CIK: {company.cik}")
            
            # Get company facts (XBRL data)
            print("Fetching XBRL facts...")
            facts = company.get_facts()
            
            if not facts:
                print("No facts available")
                return None
                
            print(f"Found {len(facts) if hasattr(facts, '__len__') else 'unknown'} XBRL facts")
            
            # Initialize metrics dictionary
            metrics = {
                'company_info': {
                    'ticker': ticker,
                    'name': company.name,
                    'cik': company.cik,
                    'sic': getattr(company, 'sic', None)
                }
            }
            
            # Extract Income Statement Metrics
            print("\n📊 INCOME STATEMENT METRICS")
            
            # Revenue
            revenue = self.find_metric_value(facts, REVENUE_TAGS)
            if revenue:
                metrics['revenue'] = revenue
                print(f"  Revenue: ${revenue:,.0f}")
            else:
                print("  Revenue: Not found")
            
            # Gross Profit
            gross_profit = self.find_metric_value(facts, GROSS_PROFIT_TAGS)
            if gross_profit and revenue:
                metrics['gross_profit'] = gross_profit
                metrics['gross_margin'] = (gross_profit / revenue) * 100
                print(f"  Gross Profit: ${gross_profit:,.0f}")
                print(f"  Gross Margin: {metrics['gross_margin']:.1f}%")
            else:
                print("  Gross Profit: Not found")
            
            # Operating Income
            operating_income = self.find_metric_value(facts, OPERATING_INCOME_TAGS)
            if operating_income:
                metrics['operating_income'] = operating_income
                if revenue:
                    metrics['operating_margin'] = (operating_income / revenue) * 100
                    print(f"  Operating Income: ${operating_income:,.0f}")
                    print(f"  Operating Margin: {metrics['operating_margin']:.1f}%")
            else:
                print("  Operating Income: Not found")
            
            # Net Income
            net_income = self.find_metric_value(facts, NET_INCOME_TAGS)
            if net_income:
                metrics['net_income'] = net_income
                if revenue:
                    metrics['net_margin'] = (net_income / revenue) * 100
                    print(f"  Net Income: ${net_income:,.0f}")
                    print(f"  Net Margin: {metrics['net_margin']:.1f}%")
            else:
                print("  Net Income: Not found")
            
            # Balance Sheet Metrics
            print("\n🏦 BALANCE SHEET METRICS")
            
            # Total Assets
            total_assets = self.find_metric_value(facts, TOTAL_ASSETS_TAGS)
            if total_assets:
                metrics['total_assets'] = total_assets
                print(f"  Total Assets: ${total_assets:,.0f}")
            else:
                print("  Total Assets: Not found")
            
            # Cash
            cash = self.find_metric_value(facts, CASH_TAGS)
            if cash:
                metrics['cash'] = cash
                print(f"  Cash & Equivalents: ${cash:,.0f}")
            else:
                print("  Cash: Not found")
            
            # Total Equity
            equity = self.find_metric_value(facts, EQUITY_TAGS)
            if equity:
                metrics['shareholders_equity'] = equity
                print(f"  Shareholders' Equity: ${equity:,.0f}")
            else:
                print("  Shareholders' Equity: Not found")
            
            # Per-Share Metrics
            print("\n📈 PER-SHARE METRICS")
            
            # Shares Outstanding
            shares = self.find_metric_value(facts, SHARES_OUTSTANDING_TAGS)
            if shares:
                metrics['shares_outstanding'] = shares
                print(f"  Shares Outstanding: {shares:,.0f}")
                
                # Book Value per Share
                if equity:
                    metrics['book_value_per_share'] = equity / shares
                    print(f"  Book Value per Share: ${metrics['book_value_per_share']:.2f}")
            else:
                print("  Shares Outstanding: Not found")
            
            # EPS
            eps = self.find_metric_value(facts, EPS_TAGS)
            if eps:
                metrics['eps'] = eps
                print(f"  Earnings per Share: ${eps:.2f}")
            else:
                print("  EPS: Not found")
            
            # Financial Ratios
            print("\n📊 FINANCIAL RATIOS")
            
            # ROE
            if net_income and equity:
                metrics['roe'] = (net_income / equity) * 100
                print(f"  Return on Equity (ROE): {metrics['roe']:.1f}%")
            
            # ROA
            if net_income and total_assets:
                metrics['roa'] = (net_income / total_assets) * 100
                print(f"  Return on Assets (ROA): {metrics['roa']:.1f}%")
            
            # Asset Turnover
            if revenue and total_assets:
                metrics['asset_turnover'] = revenue / total_assets
                print(f"  Asset Turnover: {metrics['asset_turnover']:.2f}x")
            
            metrics['extraction_timestamp'] = datetime.now().isoformat()
            
            print(f"\n✅ Successfully extracted metrics for {ticker}")
            return metrics
            
        except Exception as e:
            print(f"\n❌ Error extracting metrics for {ticker}: {e}")
            return {
                'company_info': {'ticker': ticker, 'name': company_name},
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    def create_comps_table(self):
        """Create a formatted comparable companies table"""
        print(f"\n{'='*100}")
        print("INVESTMENT BANKING COMPARABLE COMPANIES ANALYSIS")
        print('='*100)
        
        # Create DataFrame for comps table
        comps_data = []
        
        for ticker, metrics in self.companies_data.items():
            if 'error' in metrics:
                continue
                
            company_data = {
                'Ticker': ticker,
                'Company Name': metrics['company_info']['name'],
                'Revenue ($M)': metrics.get('revenue', 0) / 1_000_000 if metrics.get('revenue') else 'N/A',
                'Gross Margin (%)': f"{metrics.get('gross_margin', 0):.1f}%" if metrics.get('gross_margin') else 'N/A',
                'Operating Margin (%)': f"{metrics.get('operating_margin', 0):.1f}%" if metrics.get('operating_margin') else 'N/A',
                'Net Margin (%)': f"{metrics.get('net_margin', 0):.1f}%" if metrics.get('net_margin') else 'N/A',
                'Total Assets ($M)': metrics.get('total_assets', 0) / 1_000_000 if metrics.get('total_assets') else 'N/A',
                'Cash ($M)': metrics.get('cash', 0) / 1_000_000 if metrics.get('cash') else 'N/A',
                'ROE (%)': f"{metrics.get('roe', 0):.1f}%" if metrics.get('roe') else 'N/A',
                'ROA (%)': f"{metrics.get('roa', 0):.1f}%" if metrics.get('roa') else 'N/A',
                'Asset Turnover': f"{metrics.get('asset_turnover', 0):.2f}x" if metrics.get('asset_turnover') else 'N/A',
                'EPS ($)': f"${metrics.get('eps', 0):.2f}" if metrics.get('eps') else 'N/A',
                'Book Value/Share ($)': f"${metrics.get('book_value_per_share', 0):.2f}" if metrics.get('book_value_per_share') else 'N/A'
            }
            comps_data.append(company_data)
        
        if comps_data:
            df = pd.DataFrame(comps_data)
            print(df.to_string(index=False))
            
            # Save to CSV
            csv_filename = 'semiconductor_comps_analysis.csv'
            df.to_csv(csv_filename, index=False)
            print(f"\n💾 Comps table saved to: {csv_filename}")
            
            return df
        else:
            print("No valid data for comps table")
            return None
    
    def extract_all_companies(self):
        """Extract metrics for all companies"""
        print("🚀 Starting comprehensive financial metrics extraction for comps model...")
        
        for ticker, company_name in COMPANIES.items():
            self.companies_data[ticker] = self.extract_company_metrics(ticker, company_name)
        
        # Save raw data
        with open('semiconductor_financial_metrics.json', 'w') as f:
            json.dump(self.companies_data, f, indent=2, default=str)
        
        print(f"\n💾 Raw financial metrics saved to: semiconductor_financial_metrics.json")
        
        # Create comps table
        comps_df = self.create_comps_table()
        
        return self.companies_data, comps_df

def main():
    """Main function"""
    extractor = CompsModelExtractor()
    companies_data, comps_df = extractor.extract_all_companies()
    
    print(f"\n🎯 EXTRACTION COMPLETE!")
    print("Files created:")
    print("  • semiconductor_financial_metrics.json - Raw financial data")
    print("  • semiconductor_comps_analysis.csv - Formatted comps table")
    
    return 0

if __name__ == "__main__":
    exit(main())