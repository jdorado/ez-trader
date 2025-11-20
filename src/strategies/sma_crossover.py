from typing import Dict, Any, List
import pandas as pd
from src.core.strategy import Strategy

class SMACrossoverStrategy(Strategy):
    """Simple Moving Average Crossover Strategy."""
    
    def __init__(self, ticker: str, short_window: int = 20, long_window: int = 50):
        super().__init__("SMACrossover", {'short_window': short_window, 'long_window': long_window})
        self.ticker = ticker
        self.short_window = short_window
        self.long_window = long_window
        self.position = 0 # 0: Flat, 1: Long

    def on_data(self, data: Dict[str, pd.DataFrame]):
        self.data = data

    def generate_signals(self) -> List[Dict[str, Any]]:
        if self.ticker not in self.data:
            return []
            
        df = self.data[self.ticker]
        if len(df) < self.long_window:
            return []

        # Calculate SMAs
        # Note: In a real system, we'd optimize this to not recalculate everything every step
        close_prices = df['Close']
        if isinstance(close_prices, pd.DataFrame):
             close_prices = close_prices.iloc[:, 0] # Take first column if DataFrame

        short_sma = close_prices.rolling(window=self.short_window).mean().iloc[-1]
        long_sma = close_prices.rolling(window=self.long_window).mean().iloc[-1]
        
        # Previous SMAs for crossover check
        prev_short_sma = close_prices.rolling(window=self.short_window).mean().iloc[-2]
        prev_long_sma = close_prices.rolling(window=self.long_window).mean().iloc[-2]

        signals = []
        
        # Crossover Logic
        if prev_short_sma <= prev_long_sma and short_sma > long_sma:
            # Golden Cross -> BUY
            if self.position == 0:
                signals.append({'ticker': self.ticker, 'action': 'BUY', 'quantity': 10})
                self.position = 1
        
        elif prev_short_sma >= prev_long_sma and short_sma < long_sma:
            # Death Cross -> SELL
            if self.position == 1:
                signals.append({'ticker': self.ticker, 'action': 'SELL', 'quantity': 10})
                self.position = 0
                
        return signals
