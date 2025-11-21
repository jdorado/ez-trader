from src.data.yfinance_loader import YahooFinanceLoader
from src.strategies.volatility import VolatilityStrategy
import pandas as pd

ticker = "CVNA"
print(f"--- Debugging {ticker} Z-Score ---")

# 1. Load Data
loader = YahooFinanceLoader()
data = loader.get_historical_data(ticker, start_date="2023-01-01")
print(f"Data Rows: {len(data)}")
print(data.tail())

# 2. Run Strategy
strategy = VolatilityStrategy(ticker, z_score_threshold=1.5)
strategy.on_data({ticker: data})
signals = strategy.generate_signals()

# 3. Inspect Internals
try:
    print(f"\n--- Internal Indicators ---")
    print(f"Last Z-Score: {strategy.last_z_score:.4f}")
    print(f"Last Volatility: {strategy.last_volatility:.4f}")
except AttributeError:
    print("Could not access internal indicators.")

print(f"\nSignals Generated: {signals}")
