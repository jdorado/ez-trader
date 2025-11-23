import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import concurrent.futures
from src.data.yfinance_loader import YahooFinanceLoader
from src.data.options_loader import OptionsLoader
import pandas as pd
import numpy as np

def fetch_ticker_isolated(ticker: str):
    """
    Fetch ticker data in an isolated process.
    This function must be picklable (no nested functions, no lambdas).
    """
    # Create fresh instances in this process
    loader = YahooFinanceLoader()
    opt_loader = OptionsLoader()
    
    try:
        # Fetch historical data
        data = loader.get_historical_data(ticker, start_date="2024-01-01")
        if data.empty:
            return None
        
        close_prices = data['Close']
        if isinstance(close_prices, pd.DataFrame):
            close_prices = close_prices.iloc[:, 0]
        
        current_price = float(close_prices.iloc[-1])
        volume = int(data['Volume'].iloc[-1]) if 'Volume' in data.columns else 0
        
        # Calculate volatility
        returns = close_prices.pct_change().dropna()
        rolling_std = returns.rolling(window=20).std().iloc[-1]
        
        if isinstance(rolling_std, pd.Series):
            rolling_std = float(rolling_std.iloc[0])
        else:
            rolling_std = float(rolling_std)
        
        hv = rolling_std * np.sqrt(252)
        
        return {
            'ticker': ticker,
            'price': round(current_price, 2),
            'volume': volume,
            'hv': round(hv, 4)
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def test_process_pool():
    """Test using ProcessPoolExecutor for true parallelism"""
    tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN']
    
    print("Testing ProcessPoolExecutor (true parallel)...")
    print("="*60)
    
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        future_to_ticker = {executor.submit(fetch_ticker_isolated, ticker): ticker for ticker in tickers}
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            result = future.result()
            if result:
                results.append(result)
    
    print("\nResults:")
    for r in sorted(results, key=lambda x: x['ticker']):
        print(f"{r['ticker']:<6} Price: ${r['price']:>8.2f}  Volume: {r['volume']:>12,}  HV: {r['hv']:.4f}")
    
    # Verify uniqueness
    prices = [r['price'] for r in results]
    volumes = [r['volume'] for r in results]
    
    if len(set(prices)) == len(prices) and len(set(volumes)) == len(volumes):
        print("\n✅ SUCCESS: All tickers have unique data with ProcessPoolExecutor!")
        return True
    else:
        print("\n❌ FAILED: Still seeing duplicates")
        return False


if __name__ == "__main__":
    success = test_process_pool()
    sys.exit(0 if success else 1)
