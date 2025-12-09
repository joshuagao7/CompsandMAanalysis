#!/usr/bin/env python3
"""
Get current market data (stock prices, market cap) for semiconductor companies
Uses yfinance to get real-time market data
"""

import sys
import json
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    print("✅ yfinance imported successfully")
except ImportError:
    print("❌ yfinance not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "--break-system-packages"])
    import yfinance as yf
    print("✅ yfinance installed and imported")

COMPANIES = {
    'NVDA': 'NVIDIA Corporation',
    'MCHP': 'Microchip Technology Inc',
    'AMD': 'Advanced Micro Devices Inc', 
    'LSCC': 'Lattice Semiconductor Corp',
    'INTC': 'Intel Corporation'
}

def get_market_data(ticker):
    """Get current market data for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        
        # Get market cap
        market_cap = info.get('marketCap')
        
        # Get 52-week high/low
        fifty_two_week_high = info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = info.get('fiftyTwoWeekLow')
        
        # Get P/E ratio
        pe_ratio = info.get('trailingPE') or info.get('forwardPE')
        
        # Get P/B ratio
        pb_ratio = info.get('priceToBook')
        
        # Get enterprise value
        enterprise_value = info.get('enterpriseValue')
        
        # Get cash
        cash = info.get('totalCash') or info.get('cashAndCashEquivalents')
        
        return {
            'ticker': ticker,
            'current_price': current_price,
            'market_cap': market_cap,
            'enterprise_value': enterprise_value,
            'cash': cash,
            'pe_ratio': pe_ratio,
            'pb_ratio': pb_ratio,
            '52w_high': fifty_two_week_high,
            '52w_low': fifty_two_week_low,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"   ⚠️ Error getting market data for {ticker}: {e}")
        return {
            'ticker': ticker,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Get market data for all companies"""
    print("📊 FETCHING CURRENT MARKET DATA")
    print("="*80)
    
    market_data = {}
    
    for ticker, company_name in COMPANIES.items():
        print(f"\n🔍 Fetching market data for {ticker} - {company_name}...")
        data = get_market_data(ticker)
        market_data[ticker] = data
        
        if 'error' not in data:
            print(f"   ✅ Price: ${data.get('current_price', 'N/A'):,.2f}")
            print(f"   ✅ Market Cap: ${data.get('market_cap', 0)/1e9:,.1f}B" if data.get('market_cap') else "   ⚠️ Market Cap: N/A")
            print(f"   ✅ P/E: {data.get('pe_ratio', 'N/A')}")
        else:
            print(f"   ❌ Failed: {data.get('error')}")
    
    # Save to JSON
    output_file = 'data/market_data.json'
    with open(output_file, 'w') as f:
        json.dump(market_data, f, indent=2, default=str)
    
    print(f"\n✅ Market data saved to {output_file}")
    
    # Create summary table
    print("\n📊 MARKET DATA SUMMARY")
    print("="*80)
    
    summary_data = []
    for ticker, data in market_data.items():
        if 'error' not in data:
            summary_data.append({
                'Ticker': ticker,
                'Company': COMPANIES[ticker],
                'Stock Price ($)': f"${data.get('current_price', 0):,.2f}" if data.get('current_price') else 'N/A',
                'Market Cap ($B)': f"${data.get('market_cap', 0)/1e9:,.1f}B" if data.get('market_cap') else 'N/A',
                'Enterprise Value ($B)': f"${data.get('enterprise_value', 0)/1e9:,.1f}B" if data.get('enterprise_value') else 'N/A',
                'P/E Ratio': f"{data.get('pe_ratio', 'N/A'):.1f}" if isinstance(data.get('pe_ratio'), (int, float)) else 'N/A',
                'P/B Ratio': f"{data.get('pb_ratio', 'N/A'):.2f}" if isinstance(data.get('pb_ratio'), (int, float)) else 'N/A',
            })
    
    if summary_data:
        df = pd.DataFrame(summary_data)
        print(df.to_string(index=False))
        
        # Save CSV
        csv_file = 'tables/csv/comps/market_performance.csv'
        df.to_csv(csv_file, index=False)
        print(f"\n✅ Summary table saved to {csv_file}")
    
    return market_data

if __name__ == "__main__":
    main()

