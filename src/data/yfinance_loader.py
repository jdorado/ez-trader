import yfinance as yf
import pandas as pd
from typing import Optional
from src.data.data_loader import DataLoader
import threading

# Global lock for yfinance calls - yfinance has internal state that's not thread-safe
_yf_lock = threading.Lock()

class YahooFinanceLoader(DataLoader):
    """Data loader using yfinance."""

    def get_historical_data(self, ticker: str, start_date: str, end_date: Optional[str] = None, interval: str = "1d") -> pd.DataFrame:
        try:
            # Lock required due to yfinance's internal caching, not GIL
            with _yf_lock:
                data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False, auto_adjust=False)
            
            # Flatten MultiIndex columns if present (e.g. (Price, Ticker) -> Price)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            if data.empty:
                print(f"Warning: No data found for {ticker}")
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker} from Yahoo Finance: {e}")
            return pd.DataFrame()

    def get_latest_price(self, ticker: str) -> float:
        try:
            ticker_obj = yf.Ticker(ticker)
            # Try fast_info first, then history
            price = ticker_obj.fast_info.last_price
            if price is None:
                 data = ticker_obj.history(period="1d")
                 if not data.empty:
                     price = data['Close'].iloc[-1]
            return price if price else 0.0
        except Exception as e:
            print(f"Error fetching latest price for {ticker}: {e}")
            return 0.0
