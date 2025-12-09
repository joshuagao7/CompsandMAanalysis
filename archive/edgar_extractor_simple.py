#!/usr/bin/env python3
"""
Simple EDGAR Data Extractor using pipx-installed edgartools
This script extracts basic company information and recent filings for:
NVIDIA (NVDA), Microchip Technology (MCHP), AMD, and Lattice Semiconductor (LSCC)
"""

import subprocess
import json
import sys
import os

# Company tickers to analyze
TICKERS = ['NVDA', 'MCHP', 'AMD', 'LSCC']

def get_pipx_python_path():
    """Get the Python path from the pipx edgartools installation"""
    home = os.path.expanduser("~")
    pipx_venv = os.path.join(home, ".local", "pipx", "venvs", "edgartools", "bin", "python")
    
    if os.path.exists(pipx_venv):
        return pipx_venv
    else:
        # Fallback to regular python3
        return "python3"

def create_extraction_script():
    """Create the actual extraction script content"""
    script_content = '''
import sys
sys.path.insert(0, '/Users/joshuagao/.local/pipx/venvs/edgartools/lib/python3.14/site-packages')

try:
    from edgartools import Company
    import json
    from datetime import datetime
    
    companies = {
        'NVDA': 'NVIDIA Corporation',
        'MCHP': 'Microchip Technology Inc',
        'AMD': 'Advanced Micro Devices Inc',
        'LSCC': 'Lattice Semiconductor Corporation'
    }
    
    results = {}
    
    print("Starting EDGAR data extraction...")
    
    for ticker, name in companies.items():
        print(f"\\nProcessing {ticker} - {name}")
        
        try:
            # Get company info
            company = Company(ticker)
            
            # Basic company information
            company_info = {
                'name': company.name,
                'cik': company.cik,
                'ticker': ticker
            }
            
            # Get recent filings
            print(f"  Getting recent filings for {ticker}...")
            recent_filings = []
            filings = company.filings().head(10)
            
            for filing in filings:
                filing_info = {
                    'form': filing.form,
                    'filing_date': str(filing.filing_date),
                    'accession_number': filing.accession_number
                }
                recent_filings.append(filing_info)
            
            results[ticker] = {
                'company_info': company_info,
                'recent_filings': recent_filings,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            print(f"  ✓ Successfully extracted data for {ticker} ({len(recent_filings)} filings)")
            
        except Exception as e:
            print(f"  ✗ Error processing {ticker}: {str(e)}")
            results[ticker] = {
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    # Save results
    output_file = 'edgar_data_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\\n✓ Data extraction completed!")
    print(f"Results saved to: {output_file}")
    
    # Print summary
    print("\\n" + "="*50)
    print("EXTRACTION SUMMARY")
    print("="*50)
    
    for ticker, data in results.items():
        if 'error' in data:
            print(f"{ticker}: ERROR - {data['error']}")
        else:
            company_name = data['company_info']['name']
            filing_count = len(data['recent_filings'])
            print(f"{ticker}: {company_name} - {filing_count} filings")

except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure edgartools is properly installed.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
'''
    
    return script_content

def main():
    """Main function to run the EDGAR extraction"""
    print("Setting up EDGAR data extraction...")
    
    # Get the pipx Python path
    python_path = get_pipx_python_path()
    
    # Create the extraction script
    script_content = create_extraction_script()
    
    # Write the script to a temporary file
    temp_script = 'temp_edgar_extraction.py'
    with open(temp_script, 'w') as f:
        f.write(script_content)
    
    try:
        # Run the extraction script
        print(f"Running extraction using: {python_path}")
        result = subprocess.run([python_path, temp_script], 
                              capture_output=True, text=True)
        
        # Print the output
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running extraction: {e}")
        return 1

if __name__ == "__main__":
    exit(main())