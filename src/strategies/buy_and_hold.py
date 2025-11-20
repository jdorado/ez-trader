from typing import Dict, Any, List
import pandas as pd
from src.core.strategy import Strategy

class BuyAndHoldStrategy(Strategy):
    """Simple Buy and Hold Strategy."""
    
    def __init__(self, ticker: str):
        super().__init__("BuyAndHold")
        self.ticker = ticker
        self.bought = False

    def on_data(self, data: Dict[str, pd.DataFrame]):
        # No complex logic needed for buy and hold
        pass

    def generate_signals(self) -> List[Dict[str, Any]]:
        if not self.bought:
            self.bought = True
            return [{'ticker': self.ticker, 'action': 'BUY', 'quantity': 10}] # Fixed quantity for now
        return []
