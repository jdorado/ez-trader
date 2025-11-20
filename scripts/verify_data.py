import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader
from src.data.polygon_loader import PolygonLoader

def verify_data():
    load_dotenv()
    
    print("--- Verifying Data Sources ---")
    
    # 1. Verify Yahoo Finance
    print("\n1. Yahoo Finance:")
    yf_loader = YahooFinanceLoader()
    ticker = "AAPL"
    
    print(f"Fetching latest price for {ticker}...")
    price = yf_loader.get_latest_price(ticker)
    print(f"Latest Price: {price}")
    
    print(f"Fetching historical data for {ticker}...")
    hist = yf_loader.get_historical_data(ticker, start_date="2023-01-01", end_date="2023-01-10")
    print(f"Historical Data Shape: {hist.shape}")
    if not hist.empty:
        print("Yahoo Finance: SUCCESS")
    else:
        print("Yahoo Finance: FAILED (No data)")

    # 2. Verify Polygon.io
    print("\n2. Polygon.io:")
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("WARNING: POLYGON_API_KEY not found in .env. Skipping real API call.")
        poly_loader = PolygonLoader(api_key="DUMMY_KEY")
    else:
        poly_loader = PolygonLoader(api_key=api_key)
        
    print(f"Fetching latest price for {ticker} (Skeleton/API)...")
    price_poly = poly_loader.get_latest_price(ticker)
    print(f"Latest Price: {price_poly}")
    
    if price_poly > 0:
        print("Polygon.io: SUCCESS (Price fetched)")
    elif api_key:
        print("Polygon.io: FAILED (Price 0.0)")
    else:
        print("Polygon.io: SKIPPED (No Key)")

if __name__ == "__main__":
    verify_data()
