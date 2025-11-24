import requests
import pandas as pd
import os
from typing import Optional
from src.data.data_loader import DataLoader

class PolygonLoader(DataLoader):
    """Data loader using Polygon.io API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("POLYGON_API_KEY")
        self.base_url = os.getenv("POLYGON_BASE_URL", "https://api.polygon.io")

    def fetch_universe(self, limit: int = 100) -> list[str]:
        """
        Fetch top tickers by market cap (or default sort) from the API.
        """
        if not self.api_key:
            print("Polygon API Key not set.")
            return []

        url = f"{self.base_url}/v3/reference/tickers"
        params = {
            "market": "stocks",
            "active": "true",
            "limit": limit,
            "apiKey": self.api_key
        }
        
        try:
            print(f"Fetching universe from {self.base_url}...")
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                tickers = [item['ticker'] for item in results if '.' not in item['ticker']]
                print(f"Found {len(tickers)} tickers (after filtering).")
                return tickers
            else:
                print(f"Error fetching universe: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error calling API: {e}")
            return []

    def get_historical_data(self, ticker: str, start_date: str, end_date: Optional[str] = None, interval: str = "1d") -> pd.DataFrame:
        # Mapping interval to polygon format
        timespan = "day"
        multiplier = 1
        if interval == "1h":
            timespan = "hour"
        elif interval == "1m":
            timespan = "minute"
        
        # TODO: Implement full URL construction and pagination handling
        # This is a skeleton implementation
        print(f"Fetching {ticker} from Polygon (Skeleton)...")
        return pd.DataFrame()

    def get_latest_price(self, ticker: str) -> float:
        if not self.api_key:
            print("Polygon API Key not set.")
            return 0.0
            
        url = f"{self.base_url}/v2/last/trade/{ticker}?apiKey={self.api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', {}).get('p', 0.0)
            else:
                print(f"Error fetching price from Polygon: {response.text}")
                return 0.0
        except Exception as e:
            print(f"Error calling Polygon API: {e}")
            return 0.0

    def get_option_chain(self, ticker: str):
        """Fetch option chain - specific to Polygon."""
        # TODO: Implement option chain fetching
        pass
