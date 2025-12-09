#!/usr/bin/env python3
"""
Calculate 3-year CAGR for companies using historical revenue data from EDGAR.
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import pandas as pd

# Add parent directory to path to import edgartools
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from edgar import Company, set_identity
except ImportError:
    print("Error: edgartools not found. Install with: pipx install edgartools")
    sys.exit(1)

# Set identity for SEC API
set_identity("Investment Banking Analysis joshua.gao@yale.edu")

def get_revenue_history(ticker, years=4):
    """
    Extract revenue history for a company from EDGAR using facts API.
    
    Args:
        ticker: Stock ticker symbol
        years: Number of years of data to retrieve
    
    Returns:
        List of (year, revenue) tuples, sorted by year
    """
    try:
        company = Company(ticker)
        print(f"  Company: {company.name}")
        
        # Get facts (XBRL data) - this is the main method
        facts = company.get_facts()
        
        if not facts:
            print(f"  No facts available")
            return []
        
        print(f"  Facts object type: {type(facts)}")
        print(f"  Facts attributes: {dir(facts)[:10]}")
        
        # Access the facts dataframe directly for historical data
        revenue_data = []
        
        try:
            # Get the facts dataframe - this should contain historical data
            if hasattr(facts, 'dataframe'):
                df = facts.dataframe
                print(f"  Facts dataframe shape: {df.shape}")
                print(f"  Facts dataframe columns: {df.columns.tolist()[:10]}")
                
                # Look for revenue-related columns
                revenue_cols = [col for col in df.columns if 'revenue' in col.lower() or 'revenues' in col.lower()]
                print(f"  Revenue columns found: {revenue_cols}")
                
                if revenue_cols:
                    # Use the first revenue column
                    revenue_col = revenue_cols[0]
                    
                    # Filter for annual (10-K) filings
                    if 'form' in df.columns:
                        annual_df = df[df['form'] == '10-K'].copy()
                    else:
                        annual_df = df.copy()
                    
                    # Find date column
                    date_cols = [col for col in annual_df.columns if 'end' in col.lower() or 'date' in col.lower() or 'period' in col.lower()]
                    
                    if date_cols:
                        date_col = date_cols[0]
                        
                        for _, row in annual_df.iterrows():
                            try:
                                end_date = row[date_col]
                                revenue = row[revenue_col]
                                
                                # Skip if revenue is null or zero
                                if pd.isna(revenue) or revenue == 0:
                                    continue
                                
                                # Parse year from date
                                if isinstance(end_date, str):
                                    year = int(end_date.split('-')[0])
                                elif hasattr(end_date, 'year'):
                                    year = end_date.year
                                else:
                                    continue
                                
                                revenue_data.append((year, float(revenue)))
                            except Exception as e:
                                continue
            
            # Alternative: Try accessing facts as a dictionary/object
            if not revenue_data:
                # Try to access revenue facts directly
                try:
                    revenue_facts = facts.get_revenue()
                    print(f"  get_revenue() returned: {type(revenue_facts)} = {revenue_facts}")
                    
                    # If it's a float, that's just the latest value
                    # We need historical data, so try accessing the underlying data
                    if isinstance(revenue_facts, float):
                        # Try to get historical data from the facts object
                        if hasattr(facts, 'get_revenue'):
                            # Check if there's a way to get historical values
                            pass
                except:
                    pass
            
            # Check if it's a dataframe
            if hasattr(revenue_facts, 'dataframe'):
                df = revenue_facts.dataframe
                print(f"  DataFrame shape: {df.shape}")
                print(f"  DataFrame columns: {df.columns.tolist()}")
                
                # Filter for annual (10-K) data
                if 'form' in df.columns:
                    annual_df = df[df['form'] == '10-K'].copy()
                else:
                    annual_df = df.copy()
                
                # Look for date and value columns
                date_col = None
                value_col = None
                
                for col in annual_df.columns:
                    if 'end' in col.lower() or 'date' in col.lower():
                        date_col = col
                    if 'value' in col.lower() or 'val' in col.lower():
                        value_col = col
                
                if date_col and value_col:
                    for _, row in annual_df.iterrows():
                        try:
                            end_date = row[date_col]
                            revenue = row[value_col]
                            
                            # Parse year
                            if isinstance(end_date, str):
                                year = int(end_date.split('-')[0])
                            elif hasattr(end_date, 'year'):
                                year = end_date.year
                            else:
                                continue
                            
                            if revenue and revenue > 0:
                                revenue_data.append((year, revenue))
                        except Exception as e:
                            continue
                
                # If no date/value columns, try to use index or other columns
                if not revenue_data and len(annual_df) > 0:
                    # Try common column names
                    for col in annual_df.columns:
                        if 'revenue' in col.lower() or 'revenues' in col.lower():
                            # This might be the value column
                            for idx, row in annual_df.iterrows():
                                try:
                                    revenue = row[col]
                                    if revenue and revenue > 0:
                                        # Try to get year from index or other columns
                                        year = None
                                        for date_col in annual_df.columns:
                                            if 'end' in date_col.lower() or 'date' in date_col.lower():
                                                end_date = row[date_col]
                                                if isinstance(end_date, str):
                                                    year = int(end_date.split('-')[0])
                                                    break
                                        
                                        if year:
                                            revenue_data.append((year, revenue))
                                except:
                                    continue
            
            # If revenue_facts has values attribute
            elif hasattr(revenue_facts, 'values'):
                print(f"  Found values attribute with {len(revenue_facts.values)} items")
                for item in revenue_facts.values:
                    try:
                        if hasattr(item, 'end') and hasattr(item, 'value'):
                            end_date = item.end
                            revenue = item.value
                            
                            if isinstance(end_date, str):
                                year = int(end_date.split('-')[0])
                            elif hasattr(end_date, 'year'):
                                year = end_date.year
                            else:
                                continue
                            
                            if revenue and revenue > 0:
                                revenue_data.append((year, revenue))
                    except Exception as e:
                        continue
            
        except Exception as e:
            print(f"  Error getting revenue from facts: {e}")
            import traceback
            traceback.print_exc()
        
        # Remove duplicates and sort
        if revenue_data:
            year_dict = {}
            for year, revenue in revenue_data:
                if year not in year_dict or revenue > year_dict[year]:
                    year_dict[year] = revenue
            revenue_data = sorted(year_dict.items())
        
        return revenue_data
        
    except Exception as e:
        print(f"Error getting data for {ticker}: {e}")
        import traceback
        traceback.print_exc()
        return []

def calculate_cagr(revenue_data, years=3):
    """
    Calculate Compound Annual Growth Rate (CAGR) from revenue data.
    
    Args:
        revenue_data: List of (year, revenue) tuples
        years: Number of years to calculate CAGR over
    
    Returns:
        CAGR as a percentage, or None if insufficient data
    """
    if len(revenue_data) < 2:
        return None
    
    # Get the most recent and oldest data points
    # Assuming we want the last N years
    if len(revenue_data) >= years + 1:
        # Get last (years+1) data points
        recent_data = revenue_data[-(years+1):]
    else:
        # Use all available data
        recent_data = revenue_data
    
    if len(recent_data) < 2:
        return None
    
    # Get first and last revenue values
    first_year, first_revenue = recent_data[0]
    last_year, last_revenue = recent_data[-1]
    
    # Calculate number of years
    num_years = last_year - first_year
    
    if num_years <= 0 or first_revenue <= 0:
        return None
    
    # Calculate CAGR: (Ending Value / Beginning Value)^(1/Years) - 1
    cagr = ((last_revenue / first_revenue) ** (1.0 / num_years) - 1) * 100
    
    return cagr

def main():
    """Calculate CAGR for MCHP and LSCC."""
    tickers = ['MCHP', 'LSCC']
    
    print("Calculating 3-Year CAGR from EDGAR data...")
    print("=" * 60)
    
    results = {}
    
    for ticker in tickers:
        print(f"\n{ticker}:")
        print("-" * 60)
        
        # Get revenue history
        revenue_data = get_revenue_history(ticker, years=4)
        
        if revenue_data:
            print(f"  Found {len(revenue_data)} years of revenue data:")
            for year, revenue in revenue_data:
                print(f"    {year}: ${revenue/1e6:.1f}M")
            
            # Calculate CAGR
            cagr = calculate_cagr(revenue_data, years=3)
            
            if cagr is not None:
                results[ticker] = {
                    'cagr': cagr,
                    'revenue_data': revenue_data
                }
                print(f"\n  3-Year CAGR: {cagr:.2f}%")
            else:
                print(f"\n  Could not calculate CAGR (insufficient data)")
                results[ticker] = {'cagr': None, 'revenue_data': revenue_data}
        else:
            print(f"  No revenue data found")
            results[ticker] = {'cagr': None, 'revenue_data': []}
    
    # Save results
    output_file = Path(__file__).parent.parent / 'data' / 'cagr_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print(f"Results saved to: {output_file}")
    
    return results

if __name__ == '__main__':
    main()

