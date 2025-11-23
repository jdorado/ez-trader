import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader
import pandas as pd

print("Imported YahooFinanceLoader")
loader = YahooFinanceLoader()
print("Created loader")
try:
    data = loader.get_historical_data("AMC", "2023-01-01")
    print("Data fetched")
    print(data.head())
except Exception as e:
    print(f"Caught exception: {e}")
    import traceback
    traceback.print_exc()
