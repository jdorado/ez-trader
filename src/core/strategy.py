from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List, Optional

class Strategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        self.name = name
        self.params = params or {}
        self.positions = {} # Ticker -> Quantity

    @abstractmethod
    def on_data(self, data: Dict[str, pd.DataFrame]):
        """
        Called when new data is available.
        
        Args:
            data: Dictionary mapping tickers to their latest DataFrame (OHLCV).
        """
        pass

    @abstractmethod
    def generate_signals(self) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on current state.
        
        Returns:
            List of signal dictionaries (e.g., {'ticker': 'AAPL', 'action': 'BUY', 'quantity': 10})
        """
        pass
    
    def update_position(self, ticker: str, quantity: int):
        """Update current position for a ticker."""
        self.positions[ticker] = self.positions.get(ticker, 0) + quantity
