from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, List, Dict, Any

class DataLoader(ABC):
    """Abstract base class for data loaders."""

    @abstractmethod
    def get_historical_data(self, ticker: str, start_date: str, end_date: Optional[str] = None, interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical data for a given ticker.
        
        Args:
            ticker: Symbol to fetch.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format. Defaults to today.
            interval: Data interval (e.g., "1d", "1h").
            
        Returns:
            DataFrame with historical data.
        """
        pass

    @abstractmethod
    def get_latest_price(self, ticker: str) -> float:
        """Fetch the latest price for a ticker."""
        pass
