import sys
import os
import yfinance as yf
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def research_universe():
    print("--- Researching Systematic Universe Discovery ---")
    
    # Method 1: Wikipedia Scraping for Nasdaq 100
    # This is a common, robust way to get index constituents for free
    print("\n1. Testing Wikipedia Scraper (Nasdaq 100)...")
    try:
        url = "https://en.wikipedia.org/wiki/Nasdaq-100"
        tables = pd.read_html(url)
        # The constituents table is usually the 5th one (index 4), but it varies. 
        # We look for 'Ticker' or 'Symbol' column.
        
        nasdaq_df = None
        for table in tables:
            if 'Ticker' in table.columns:
                nasdaq_df = table
                break
            elif 'Symbol' in table.columns:
                nasdaq_df = table
                break
                
        if nasdaq_df is not None:
            tickers = nasdaq_df['Ticker'].tolist() if 'Ticker' in nasdaq_df.columns else nasdaq_df['Symbol'].tolist()
            print(f"SUCCESS: Found {len(tickers)} tickers from Wikipedia.")
            print(f"Sample: {tickers[:10]}")
        else:
            print("FAILED: Could not find constituents table on Wikipedia.")
            
    except Exception as e:
        print(f"FAILED: Wikipedia scrape error: {e}")

    # Method 2: YFinance Sector/Industry (Limited)
    # YFinance doesn't have a direct "Screener" API exposed easily in the python wrapper without some hacks.
    
    # Method 3: Check Polygon (if configured)
    # We'll check if the env var is set
    api_key = os.environ.get("POLYGON_API_KEY")
    if api_key:
        print("\n3. Testing Polygon API...")
        print("Polygon Key Found. (Not implementing full call yet, just checking availability)")
    else:
        print("\n3. Polygon API Key NOT found in env.")

if __name__ == "__main__":
    research_universe()
