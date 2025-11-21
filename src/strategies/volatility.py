from typing import Dict, Any, List
import pandas as pd
import numpy as np
from src.core.strategy import Strategy
from src.core.risk_manager import RiskManager

class VolatilityStrategy(Strategy):
    """
    Aggressive strategy targeting high volatility breakouts.
    Uses Kelly Criterion for position sizing.
    """
    
    def __init__(self, ticker: str, lookback_window: int = 20, z_score_threshold: float = 1.5):
        super().__init__("VolatilityBreakout", {'lookback': lookback_window, 'threshold': z_score_threshold})
        self.ticker = ticker
        self.lookback = lookback_window
        self.threshold = z_score_threshold
        self.risk_manager = RiskManager(max_risk_per_trade=0.05, kelly_fraction=0.5)
        self.position = 0

    def on_data(self, data: Dict[str, pd.DataFrame]):
        self.data = data

    def generate_signals(self) -> List[Dict[str, Any]]:
        if self.ticker not in self.data:
            return []
            
        df = self.data[self.ticker]
        if len(df) < self.lookback:
            return []

        # Calculate Returns and Volatility
        close_prices = df['Close']
        if isinstance(close_prices, pd.DataFrame):
             close_prices = close_prices.iloc[:, 0]

        returns = close_prices.pct_change().dropna()
        
        # Rolling Volatility (Standard Deviation)
        rolling_std = returns.rolling(window=self.lookback).std().iloc[-1]
        rolling_mean = returns.rolling(window=self.lookback).mean().iloc[-1]
        
        # Current Return
        current_return = returns.iloc[-1]
        
        # Z-Score of current move
        if rolling_std == 0:
            return []
            
        z_score = (current_return - rolling_mean) / rolling_std
        
        # Store for debugging/reporting
        self.last_z_score = z_score
        self.last_volatility = rolling_std

        
        signals = []
        price = close_prices.iloc[-1]
        
        # Breakout Logic
        if abs(z_score) > self.threshold:
            # Significant move detected
            action = 'BUY' if z_score > 0 else 'SELL' # Directional bet
            
            # Calculate Position Size using Kelly
            # Assumptions for this strategy:
            # Win Rate: 40% (Trend following often has lower win rate but high R:R)
            # Win/Loss Ratio: 3.0 (Big wins, small losses)
            
            # Stop Loss: 2 * Volatility (e.g., if daily vol is 2%, stop is 4% away)
            stop_loss_pct = 2 * rolling_std
            
            target_allocation = self.risk_manager.get_target_allocation(
                capital=10000.0, # TODO: Pass actual capital
                stop_loss_pct=stop_loss_pct,
                win_rate=0.40,
                win_loss_ratio=3.0
            )
            
            # Pass the dollar allocation amount in the signal
            if target_allocation > 0:
                # Simple logic: If we are flat, enter. If we are opposite, flip.
                if self.position == 0:
                    signals.append({'ticker': self.ticker, 'action': action, 'allocation': target_allocation, 'strategy': 'VolBreakout'})
                    self.position = 1 if action == 'BUY' else -1
                elif self.position == 1 and action == 'SELL':
                    # Close Long, Open Short
                    signals.append({'ticker': self.ticker, 'action': 'SELL', 'allocation': target_allocation, 'strategy': 'VolBreakout'})
                    self.position = -1
                elif self.position == -1 and action == 'BUY':
                    # Close Short, Open Long
                    signals.append({'ticker': self.ticker, 'action': 'BUY', 'allocation': target_allocation, 'strategy': 'VolBreakout'})
                    self.position = 1
                    
        return signals
