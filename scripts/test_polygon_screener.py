import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env explicitly
load_dotenv()

from src.data.polygon_loader import PolygonLoader

def test_screener():
    print("--- Testing Polygon/Massive Screener ---")
    
    loader = PolygonLoader()
    if not loader.api_key:
        print("ERROR: POLYGON_API_KEY not found in env.")
        return

    print(f"Using Base URL: {loader.base_url}")
    
    tickers = loader.fetch_universe(limit=50)
    
    if tickers:
        print(f"\nSUCCESS: Retrieved {len(tickers)} tickers.")
        print(f"Sample: {tickers[:10]}")
    else:
        print("\nFAILED: No tickers returned.")

if __name__ == "__main__":
    test_screener()
