import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_sq():
    ticker = "SQ"
    print(f"Testing fetch for {ticker}...")
    
    try:
        # Test 1: yf.download
        print("\n--- Test 1: yf.download ---")
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        data = yf.download(ticker, start=start_date, progress=False)
        print(f"Data shape: {data.shape}")
        if not data.empty:
            print(data.tail())
        else:
            print("Data is empty!")
            
        # Test 2: yf.Ticker
        print("\n--- Test 2: yf.Ticker ---")
        sq = yf.Ticker(ticker)
        hist = sq.history(period="1mo")
        print(f"History shape: {hist.shape}")
        if not hist.empty:
            print(hist.tail())
        else:
            print("History is empty!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sq()
