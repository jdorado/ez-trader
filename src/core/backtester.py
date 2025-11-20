import pandas as pd
from typing import List, Dict, Any
from src.core.strategy import Strategy
from src.data.data_loader import DataLoader

class Backtester:
    """Engine for backtesting strategies."""
    
    def __init__(self, strategy: Strategy, data_loader: DataLoader, initial_capital: float = 10000.0):
        self.strategy = strategy
        self.data_loader = data_loader
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.portfolio_value = []
        self.trades = []

    def run(self, tickers: List[str], start_date: str, end_date: str, interval: str = "1d"):
        """
        Run the backtest.
        
        Args:
            tickers: List of tickers to test.
            start_date: Start date.
            end_date: End date.
            interval: Data interval.
        """
        print(f"Starting backtest for {self.strategy.name} on {tickers}...")
        
        # 1. Fetch Data
        data_map = {}
        for ticker in tickers:
            df = self.data_loader.get_historical_data(ticker, start_date, end_date, interval)
            data_map[ticker] = df
            
        # 2. Simulate Loop (Simplified for now: just iterating day by day across all tickers)
        # In a real event-driven backtester, we'd align timestamps.
        # Here we assume daily data and just iterate through the index of the first ticker for simplicity of the skeleton.
        
        if not data_map or not tickers:
            print("No data to backtest.")
            return

        # Align indices (intersection)
        common_index = data_map[tickers[0]].index
        for ticker in tickers[1:]:
            common_index = common_index.intersection(data_map[ticker].index)
            
        for date in common_index:
            # Slice data for this date (simulating 'current' data)
            # In reality, we'd pass the window up to this date
            current_data = {}
            for ticker in tickers:
                # We give the strategy data up to this point to avoid lookahead bias? 
                # Or just the current bar? usually full history up to now.
                current_data[ticker] = data_map[ticker].loc[:date]
            
            self.strategy.on_data(current_data)
            signals = self.strategy.generate_signals()
            self._execute_signals(signals, date, data_map)
            
            self._update_portfolio_value(date, data_map)

        print(f"Backtest complete. Final Capital: {self.current_capital}")

    def _execute_signals(self, signals: List[Dict[str, Any]], date, data_map):
        """Execute signals (simulated)."""
        for signal in signals:
            ticker = signal['ticker']
            action = signal['action']
            quantity = signal['quantity']
            
            price = data_map[ticker].loc[date]['Close'] # Assuming execution at Close
            if isinstance(price, pd.Series):
                price = price.iloc[0]

            
            cost = price * quantity
            if action == 'BUY':
                if self.current_capital >= cost:
                    self.current_capital -= cost
                    self.strategy.update_position(ticker, quantity)
                    self.trades.append({'date': date, 'ticker': ticker, 'action': 'BUY', 'price': price, 'quantity': quantity})
            elif action == 'SELL':
                # Check if we have position
                current_pos = self.strategy.positions.get(ticker, 0)
                if current_pos >= quantity:
                    self.current_capital += cost
                    self.strategy.update_position(ticker, -quantity)
                    self.trades.append({'date': date, 'ticker': ticker, 'action': 'SELL', 'price': price, 'quantity': quantity})

    def _update_portfolio_value(self, date, data_map):
        """Calculate total portfolio value."""
        holdings_value = 0.0
        for ticker, qty in self.strategy.positions.items():
            price = data_map[ticker].loc[date]['Close']
            if isinstance(price, pd.Series):
                price = price.iloc[0]
            holdings_value += price * qty
        
        total_value = self.current_capital + holdings_value
        self.portfolio_value.append({'date': date, 'value': total_value})
