#!/usr/bin/env python3

# Simple test to verify edgartools installation and basic functionality

import sys
import os

try:
    print("Attempting to import edgartools...")
    from edgartools import Company
    print("✓ Successfully imported edgartools")
    
    print("\nTesting basic functionality with NVIDIA (NVDA)...")
    company = Company("NVDA")
    print(f"✓ Company name: {company.name}")
    print(f"✓ CIK: {company.cik}")
    
    print("\nGetting recent filings...")
    filings = company.filings().head(3)
    print(f"✓ Found {len(filings)} recent filings")
    
    for i, filing in enumerate(filings, 1):
        print(f"  {i}. {filing.form} filed on {filing.filing_date}")
    
    print("\n✓ Basic EDGAR functionality test passed!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)