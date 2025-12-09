#!/usr/bin/env python3
"""
XBRL Facts Explorer for Investment Banking Analysis
Explores available XBRL tags to understand how to extract financial metrics
"""

import sys
import os
import json
from collections import defaultdict

# Add the pipx edgartools site-packages to path
pipx_site_packages = "/Users/joshuagao/.local/pipx/venvs/edgartools/lib/python3.14/site-packages"
sys.path.insert(0, pipx_site_packages)

try:
    from edgar import Company, set_identity
    set_identity("Investment Banking Analysis joshua.gao@yale.edu")
    print("✓ XBRL Facts Explorer initialized")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

def explore_company_facts(ticker, company_name):
    """Explore XBRL facts for a company to understand available tags"""
    print(f"\n{'='*60}")
    print(f"EXPLORING XBRL FACTS FOR {ticker} - {company_name}")
    print('='*60)
    
    try:
        company = Company(ticker)
        print(f"Company: {company.name}")
        
        # Get facts
        facts = company.get_facts()
        if not facts:
            print("No facts available")
            return
        
        print(f"Total facts available: {len(facts) if hasattr(facts, '__len__') else 'unknown'}")
        
        # Explore the structure of facts
        print(f"\nFacts object type: {type(facts)}")
        print(f"Facts object attributes: {dir(facts)[:10]}...")  # Show first 10 attributes
        
        # Try to find common financial statement tags
        revenue_related = []
        profit_related = []
        asset_related = []
        equity_related = []
        share_related = []
        
        # Get all available attributes/tags
        all_attrs = [attr for attr in dir(facts) if not attr.startswith('_')]
        print(f"\nFound {len(all_attrs)} available XBRL tags")
        
        # Search for key financial metrics
        for attr in all_attrs:
            attr_lower = attr.lower()
            
            # Revenue related
            if any(term in attr_lower for term in ['revenue', 'sales']):
                revenue_related.append(attr)
            
            # Profit/Income related
            elif any(term in attr_lower for term in ['income', 'profit', 'earnings', 'loss']):
                profit_related.append(attr)
            
            # Assets related
            elif any(term in attr_lower for term in ['asset', 'cash']):
                asset_related.append(attr)
            
            # Equity related
            elif any(term in attr_lower for term in ['equity', 'stockholder']):
                equity_related.append(attr)
            
            # Share related
            elif any(term in attr_lower for term in ['share', 'outstanding', 'eps']):
                share_related.append(attr)
        
        # Display findings
        print(f"\n🔍 REVENUE RELATED TAGS ({len(revenue_related)}):")
        for tag in revenue_related[:10]:  # Show first 10
            print(f"  • {tag}")
        
        print(f"\n🔍 PROFIT/INCOME RELATED TAGS ({len(profit_related)}):")
        for tag in profit_related[:10]:
            print(f"  • {tag}")
        
        print(f"\n🔍 ASSET RELATED TAGS ({len(asset_related)}):")
        for tag in asset_related[:10]:
            print(f"  • {tag}")
        
        print(f"\n🔍 EQUITY RELATED TAGS ({len(equity_related)}):")
        for tag in equity_related[:10]:
            print(f"  • {tag}")
        
        print(f"\n🔍 SHARE RELATED TAGS ({len(share_related)}):")
        for tag in share_related[:10]:
            print(f"  • {tag}")
        
        # Try to get actual values from a few promising tags
        print(f"\n🎯 SAMPLE VALUES FROM PROMISING TAGS:")
        
        sample_tags = []
        if revenue_related:
            sample_tags.extend(revenue_related[:2])
        if profit_related:
            sample_tags.extend(profit_related[:2])
        if asset_related:
            sample_tags.extend(asset_related[:2])
        
        for tag in sample_tags:
            try:
                fact = getattr(facts, tag)
                if hasattr(fact, 'values') and fact.values:
                    latest_value = fact.values[0]
                    print(f"  {tag}: {latest_value.value} (Period: {getattr(latest_value, 'period', 'N/A')})")
                else:
                    print(f"  {tag}: No values available")
            except Exception as e:
                print(f"  {tag}: Error accessing - {e}")
        
        # Return the findings for use
        return {
            'revenue_tags': revenue_related,
            'profit_tags': profit_related,
            'asset_tags': asset_related,
            'equity_tags': equity_related,
            'share_tags': share_related,
            'total_tags': len(all_attrs)
        }
        
    except Exception as e:
        print(f"❌ Error exploring {ticker}: {e}")
        return None

def main():
    """Explore XBRL facts for all companies"""
    companies = {
        'NVDA': 'NVIDIA Corporation',
        'MCHP': 'Microchip Technology Inc',
        'AMD': 'Advanced Micro Devices Inc',
        'LSCC': 'Lattice Semiconductor Corp'
    }
    
    all_findings = {}
    
    for ticker, name in companies.items():
        findings = explore_company_facts(ticker, name)
        if findings:
            all_findings[ticker] = findings
    
    # Save findings
    with open('xbrl_tag_analysis.json', 'w') as f:
        json.dump(all_findings, f, indent=2, default=str)
    
    print(f"\n💾 XBRL tag analysis saved to: xbrl_tag_analysis.json")
    print("\nThis analysis will help identify the correct XBRL tags for financial metrics extraction.")
    
    return 0

if __name__ == "__main__":
    exit(main())