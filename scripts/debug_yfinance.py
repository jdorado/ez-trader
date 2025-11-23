import yfinance as yf
import pandas as pd

ticker = "CMCSA"
print(f"Downloading {ticker} with auto_adjust=False...")
data = yf.download(ticker, start="2023-01-01", progress=False, auto_adjust=False)
print("\nData Type:", type(data))
print("\nColumns:", data.columns)
print("\nHead:\n", data.head())

try:
    close_prices = data['Close']
    print("\nclose_prices Type:", type(close_prices))
    if isinstance(close_prices, pd.DataFrame):
        print("Converting DataFrame to Series...")
        close_prices = close_prices.iloc[:, 0]
    
    print("close_prices Type after conversion:", type(close_prices))
    print("Head:\n", close_prices.head())

    returns = close_prices.pct_change().dropna()
    print("\nreturns Type:", type(returns))
    
    rolling_std = returns.rolling(window=20).std().iloc[-1]
    print("\nrolling_std:", rolling_std)
    print("rolling_std Type:", type(rolling_std))
    
    if rolling_std == 0:
        print("rolling_std is 0")
    else:
        print("rolling_std is not 0")
        
except Exception as e:
    print(f"\nError in logic: {e}")

