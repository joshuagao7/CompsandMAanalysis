#!/usr/bin/env python3
"""
EDGAR Data Extractor for NVIDIA, MCHP, AMD, and Lattice Semiconductor
Uses the pipx-installed edgartools to extract SEC filing data
"""

import sys
import os
import json
from datetime import datetime

# Add the pipx edgartools site-packages to path
pipx_site_packages = "/Users/joshuagao/.local/pipx/venvs/edgartools/lib/python3.14/site-packages"
sys.path.insert(0, pipx_site_packages)

try:
    # Import from edgar module (not edgartools)
    from edgar import Company, set_identity
    
    # Set identity for SEC API access (required)
    set_identity("Academic Research joshua.gao@yale.edu")
    
    print("✓ Successfully imported edgar module and set identity")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Available modules in pipx environment:")
    for item in os.listdir(pipx_site_packages):
        if not item.startswith('.') and not item.startswith('_'):
            print(f"  - {item}")
    sys.exit(1)

# Company data
COMPANIES = {
    'NVDA': 'NVIDIA Corporation',
    'MCHP': 'Microchip Technology Incorporated',
    'AMD': 'Advanced Micro Devices Inc',
    'LSCC': 'Lattice Semiconductor Corporation'
}

def extract_company_data(ticker, company_name):
    """Extract data for a single company"""
    print(f"\nProcessing {ticker} - {company_name}")
    
    try:
        # Create company object
        company = Company(ticker)
        
        # Basic company information
        company_info = {
            'ticker': ticker,
            'name': getattr(company, 'name', company_name),
            'cik': getattr(company, 'cik', None),
            'sic': getattr(company, 'sic', None)
        }
        
        print(f"  Company: {company_info['name']}")
        print(f"  CIK: {company_info['cik']}")
        
        # Get recent filings
        print("  Fetching recent filings...")
        filings_data = []
        
        try:
            # Get recent 10-K and 10-Q filings
            filings = []
            
            # Get recent filings using the correct API
            all_filings = company.get_filings(form=['10-K', '10-Q'])[:20]  # Get last 20 filings
            
            for filing in all_filings:
                filing_info = {
                    'form': getattr(filing, 'form', 'Unknown'),
                    'filing_date': str(getattr(filing, 'filing_date', 'Unknown')),
                    'accession_number': getattr(filing, 'accession_number', 'Unknown'),
                    'period_end': str(getattr(filing, 'period_end', None)) if hasattr(filing, 'period_end') else None
                }
                filings_data.append(filing_info)
            
            # Also try to get latest 10-K and 10-Q specifically
            try:
                latest_10k = company.latest_tenk
                if latest_10k:
                    print(f"    Latest 10-K: {latest_10k.filing_date}")
                    
                latest_10q = company.latest_tenq  
                if latest_10q:
                    print(f"    Latest 10-Q: {latest_10q.filing_date}")
            except:
                pass
                
        except Exception as e:
            print(f"  Warning: Could not fetch filings - {e}")
        
        print(f"  ✓ Found {len(filings_data)} recent filings")
        
        return {
            'company_info': company_info,
            'recent_filings': filings_data,
            'extraction_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"  ✗ Error processing {ticker}: {e}")
        return {
            'error': str(e),
            'extraction_timestamp': datetime.now().isoformat()
        }

def main():
    """Main extraction function"""
    print("="*60)
    print("EDGAR DATA EXTRACTOR")
    print("="*60)
    print("Extracting SEC filing data for semiconductor companies:")
    for ticker, name in COMPANIES.items():
        print(f"  • {ticker} - {name}")
    print()
    
    results = {}
    
    # Extract data for each company
    for ticker, company_name in COMPANIES.items():
        results[ticker] = extract_company_data(ticker, company_name)
    
    # Save results to JSON file
    output_file = 'edgar_semiconductor_data.json'
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n✓ Data saved to: {output_file}")
    except Exception as e:
        print(f"\n✗ Error saving data: {e}")
    
    # Print summary report
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    
    success_count = 0
    for ticker, data in results.items():
        if 'error' in data:
            print(f"{ticker:<6} ERROR: {data['error']}")
        else:
            company_name = data['company_info']['name']
            filing_count = len(data['recent_filings'])
            print(f"{ticker:<6} {company_name:<40} {filing_count:>3} filings")
            success_count += 1
    
    print(f"\n✓ Successfully processed {success_count}/{len(COMPANIES)} companies")
    print(f"✓ Results saved to: {output_file}")
    
    return 0

if __name__ == "__main__":
    exit(main())