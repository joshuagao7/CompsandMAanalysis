#!/usr/bin/env python3
"""
EDGAR Data Extractor for NVIDIA, MCHP, AMD, and Lattice
This script uses edgartools to extract financial data from SEC filings
"""

from edgartools import Company
import pandas as pd
from datetime import datetime
import json

# Company ticker symbols and names
COMPANIES = {
    'NVDA': 'NVIDIA Corporation',
    'MCHP': 'Microchip Technology Incorporated', 
    'AMD': 'Advanced Micro Devices Inc',
    'LSCC': 'Lattice Semiconductor Corporation'
}

class EdgarDataExtractor:
    def __init__(self):
        self.data = {}
    
    def get_company_info(self, ticker):
        """Get basic company information"""
        try:
            company = Company(ticker)
            info = {
                'ticker': ticker,
                'name': company.name,
                'cik': company.cik,
                'sic': getattr(company, 'sic', None),
                'industry': getattr(company, 'industry', None),
                'sector': getattr(company, 'sector', None),
            }
            return info
        except Exception as e:
            print(f"Error getting company info for {ticker}: {e}")
            return None
    
    def get_recent_filings(self, ticker, form_types=['10-K', '10-Q'], limit=10):
        """Get recent filings for a company"""
        try:
            company = Company(ticker)
            filings = company.filings(form=form_types).head(limit)
            
            filing_data = []
            for filing in filings:
                filing_info = {
                    'form': filing.form,
                    'filing_date': str(filing.filing_date),
                    'period_end': str(getattr(filing, 'period_end', None)),
                    'accession_number': filing.accession_number,
                    'document_url': getattr(filing, 'document_url', None)
                }
                filing_data.append(filing_info)
            
            return filing_data
        except Exception as e:
            print(f"Error getting filings for {ticker}: {e}")
            return []
    
    def get_financial_data(self, ticker):
        """Extract basic financial data from recent 10-K/10-Q filings"""
        try:
            company = Company(ticker)
            # Get the most recent 10-K and 10-Q
            recent_10k = company.filings(form='10-K').head(1)
            recent_10q = company.filings(form='10-Q').head(1)
            
            financial_data = {}
            
            # Try to get data from 10-K
            if len(recent_10k) > 0:
                try:
                    filing = recent_10k[0]
                    facts = filing.xbrl()
                    if facts:
                        # Extract key financial metrics
                        financial_data['10-K'] = {
                            'filing_date': str(filing.filing_date),
                            'period_end': str(getattr(filing, 'period_end', None)),
                            'total_revenue': self.extract_fact_value(facts, ['Revenues', 'TotalRevenue', 'Revenue']),
                            'net_income': self.extract_fact_value(facts, ['NetIncomeLoss', 'NetIncome']),
                            'total_assets': self.extract_fact_value(facts, ['Assets', 'TotalAssets']),
                            'total_equity': self.extract_fact_value(facts, ['StockholdersEquity', 'TotalStockholdersEquity'])
                        }
                except Exception as e:
                    print(f"Error extracting 10-K data for {ticker}: {e}")
            
            # Try to get data from 10-Q
            if len(recent_10q) > 0:
                try:
                    filing = recent_10q[0]
                    facts = filing.xbrl()
                    if facts:
                        financial_data['10-Q'] = {
                            'filing_date': str(filing.filing_date),
                            'period_end': str(getattr(filing, 'period_end', None)),
                            'total_revenue': self.extract_fact_value(facts, ['Revenues', 'TotalRevenue', 'Revenue']),
                            'net_income': self.extract_fact_value(facts, ['NetIncomeLoss', 'NetIncome'])
                        }
                except Exception as e:
                    print(f"Error extracting 10-Q data for {ticker}: {e}")
            
            return financial_data
        except Exception as e:
            print(f"Error getting financial data for {ticker}: {e}")
            return {}
    
    def extract_fact_value(self, facts, fact_names):
        """Try to extract a fact value using multiple possible fact names"""
        for fact_name in fact_names:
            try:
                if hasattr(facts, fact_name.lower()):
                    fact = getattr(facts, fact_name.lower())
                    # Get the most recent value
                    if hasattr(fact, 'values') and len(fact.values) > 0:
                        return fact.values[0].value
                elif hasattr(facts, fact_name):
                    fact = getattr(facts, fact_name)
                    if hasattr(fact, 'values') and len(fact.values) > 0:
                        return fact.values[0].value
            except:
                continue
        return None
    
    def extract_all_data(self):
        """Extract data for all companies"""
        print("Starting EDGAR data extraction...")
        
        for ticker, company_name in COMPANIES.items():
            print(f"\nProcessing {ticker} - {company_name}")
            
            # Get company info
            company_info = self.get_company_info(ticker)
            
            # Get recent filings
            filings = self.get_recent_filings(ticker)
            
            # Get financial data
            financial_data = self.get_financial_data(ticker)
            
            # Store all data
            self.data[ticker] = {
                'company_info': company_info,
                'recent_filings': filings,
                'financial_data': financial_data,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            print(f"✓ Extracted data for {ticker}")
    
    def save_data(self, filename='edgar_data.json'):
        """Save extracted data to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            print(f"\n✓ Data saved to {filename}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def create_summary_report(self):
        """Create a summary report of extracted data"""
        print("\n" + "="*60)
        print("EDGAR DATA EXTRACTION SUMMARY")
        print("="*60)
        
        for ticker, data in self.data.items():
            company_info = data.get('company_info', {})
            filings = data.get('recent_filings', [])
            financial_data = data.get('financial_data', {})
            
            print(f"\n{ticker} - {company_info.get('name', 'Unknown')}")
            print(f"CIK: {company_info.get('cik', 'N/A')}")
            print(f"Recent filings: {len(filings)} found")
            
            if '10-K' in financial_data:
                print(f"Latest 10-K: {financial_data['10-K'].get('filing_date', 'N/A')}")
            if '10-Q' in financial_data:
                print(f"Latest 10-Q: {financial_data['10-Q'].get('filing_date', 'N/A')}")

def main():
    """Main function to run the extraction"""
    extractor = EdgarDataExtractor()
    
    try:
        # Extract data for all companies
        extractor.extract_all_data()
        
        # Save data to file
        extractor.save_data()
        
        # Print summary
        extractor.create_summary_report()
        
        print(f"\n✓ EDGAR data extraction completed successfully!")
        print(f"Data saved to: edgar_data.json")
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())