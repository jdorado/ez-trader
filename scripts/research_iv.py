import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.options_loader import OptionsLoader
from src.data.yfinance_loader import YahooFinanceLoader

def research_iv(ticker: str):
    print(f"--- Researching IV for {ticker} ---")
    
    # 1. Get Price Data for HV
    loader = YahooFinanceLoader()
    data = loader.get_historical_data(ticker, start_date="2024-01-01")
    
    # Ensure Series
    close_prices = data['Close']
    if isinstance(close_prices, pd.DataFrame):
        close_prices = close_prices.iloc[:, 0]
        
    returns = close_prices.pct_change().dropna()
    hv_20 = returns.rolling(window=20).std().iloc[-1] * np.sqrt(252) # Annualized
    
    # Ensure float
    if isinstance(hv_20, pd.Series):
        hv_20 = hv_20.iloc[0]
        
    print(f"HV (20-day Annualized): {hv_20:.2%}")
    
    # 2. Get Options Data for IV
    opt_loader = OptionsLoader()
    expiry = opt_loader.get_nearest_expiration(ticker, min_days=10)
    print(f"Nearest Expiry (>10 days): {expiry}")
    
    if not expiry:
        print("No expiry found.")
        return

    chain = opt_loader.get_option_chain(ticker, expiry)
    calls = chain['calls']
    
    if calls.empty:
        print("No calls found.")
        return
        
    # Check columns
    print(f"Columns: {calls.columns.tolist()}")
    
    if 'impliedVolatility' not in calls.columns:
        print("CRITICAL: 'impliedVolatility' column MISSING.")
        return
        
    # Find ATM Options
    avg_iv = opt_loader.get_atm_iv(ticker, expiry)
    print(f"ATM IV (via get_atm_iv): {avg_iv:.2%}")
    
    # Compare
    print(f"IV / HV Ratio: {avg_iv / hv_20:.2f}")
    
    if avg_iv < hv_20:
        print("CONCLUSION: Options are CHEAP (IV < HV). Good for Buying.")
    else:
        print("CONCLUSION: Options are EXPENSIVE (IV > HV). Be careful Buying.")

if __name__ == "__main__":
    research_iv("TXN")
