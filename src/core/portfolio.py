from typing import Dict

class PortfolioManager:
    """Manages portfolio state, risk, and PnL."""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.cash = initial_capital
        self.positions: Dict[str, int] = {} # Ticker -> Quantity
        self.initial_capital = initial_capital

    def update_position(self, ticker: str, quantity: int, price: float, action: str):
        """
        Update position after a trade.
        
        Args:
            ticker: Symbol.
            quantity: Number of shares.
            price: Execution price.
            action: 'BUY' or 'SELL'.
        """
        cost = quantity * price
        if action == 'BUY':
            self.cash -= cost
            self.positions[ticker] = self.positions.get(ticker, 0) + quantity
        elif action == 'SELL':
            self.cash += cost
            self.positions[ticker] = self.positions.get(ticker, 0) - quantity
            if self.positions[ticker] == 0:
                del self.positions[ticker]

    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value based on current prices."""
        holdings_value = 0.0
        for ticker, qty in self.positions.items():
            price = current_prices.get(ticker, 0.0)
            holdings_value += price * qty
        return self.cash + holdings_value

    def get_pnl(self, current_prices: Dict[str, float]) -> float:
        """Calculate total PnL."""
        return self.get_total_value(current_prices) - self.initial_capital
