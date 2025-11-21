import sys
import os
import pandas as pd
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader

def verify_ticker(ticker):
    print(f"--- Verifying Z-Score for {ticker} ---")
    
    loader = YahooFinanceLoader()
    # Fetch enough data for 20-day lookback
    data = loader.get_historical_data(ticker, start_date="2024-01-01")
    
    if data.empty:
        print(f"ERROR: No data found for {ticker}")
        return

    close_prices = data['Close']
    
    # Handle multi-index columns if present
    if isinstance(close_prices, pd.DataFrame):
        close_prices = close_prices.iloc[:, 0]
    
    returns = close_prices.pct_change().dropna()
    
    lookback = 20
    rolling_std = returns.rolling(window=lookback).std().iloc[-1]
    rolling_mean = returns.rolling(window=lookback).mean().iloc[-1]
    current_return = returns.iloc[-1]
    
    z_score = (current_return - rolling_mean) / rolling_std
    
    print(f"Ticker: {ticker}")
    print(f"Current Price: {close_prices.iloc[-1]:.2f}")
    print(f"Current Return: {current_return:.4f}")
    print(f"Rolling Mean (20d): {rolling_mean:.4f}")
    print(f"Rolling Vol (20d): {rolling_std:.4f}")
    print(f"Calculated Z-Score: {z_score:.4f}")
    
    if abs(z_score) > 1.5:
        print("VERIFICATION PASSED: Z-Score > 1.5")
    else:
        print("VERIFICATION FAILED: Z-Score < 1.5")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", help="Ticker symbol to verify")
    args = parser.parse_args()
    
    verify_ticker(args.ticker)
