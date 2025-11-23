import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env
load_dotenv()

from src.data.polygon_loader import PolygonLoader
from src.data.stock_screener import YahooFinanceScreener, ScreenerCriteria

def run_systematic_scan():
    print("--- 🔄 Starting Systematic Universe Scan ---")
    
    # 1. Discovery (Polygon/Massive)
    print("\n1. Discovery Phase (Polygon/Massive)...")
    poly_loader = PolygonLoader()
    if not poly_loader.api_key:
        print("ERROR: POLYGON_API_KEY not found.")
        return

    # Fetch top 100 tickers
    raw_tickers = poly_loader.fetch_universe(limit=100)
    if not raw_tickers:
        print("No tickers found. Aborting.")
        return
        
    print(f"Discovered {len(raw_tickers)} candidates.")
    
    # 2. Screening (YFinance)
    print("\n2. Screening Phase (YFinance)...")
    screener = YahooFinanceScreener(tickers=raw_tickers)
    
    # Define Aggressive Criteria
    # - High Beta (> 1.0)
    # - Liquid (> 1M Volume)
    # - Price > $5 (Avoid penny stocks)
    filters = {
        ScreenerCriteria.BETA_MIN.value: (1.0, None),
        ScreenerCriteria.VOLUME_MIN.value: (1_000_000, None),
        ScreenerCriteria.PRICE_MIN.value: (5.0, None)
    }
    
    print(f"Applying Filters: {filters}")
    results_df = screener.screen_stocks(filters)
    
    if not results_df.empty:
        print(f"\n✅ Found {len(results_df)} High-Quality Candidates:")
        print(results_df[['Ticker', 'Price', 'Beta', 'Volume']].head(20))
        
        # Save to report
        output_path = "reports/systematic_universe.csv"
        results_df.to_csv(output_path, index=False)
        print(f"\nSaved to {output_path}")
    else:
        print("\n❌ No tickers matched the criteria.")

if __name__ == "__main__":
    run_systematic_scan()
