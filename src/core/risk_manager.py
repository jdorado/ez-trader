class RiskManager:
    """
    Manages risk and position sizing.
    Implements Kelly Criterion for aggressive growth.
    """
    
    def __init__(self, max_risk_per_trade: float = 0.05, kelly_fraction: float = 0.5):
        """
        Args:
            max_risk_per_trade: Maximum % of capital to risk on a single trade (stop loss amount).
            kelly_fraction: Fraction of Full Kelly to use (e.g., 0.5 for Half Kelly). 
                            Full Kelly is very volatile.
        """
        self.max_risk_per_trade = max_risk_per_trade
        self.kelly_fraction = kelly_fraction

    def calculate_kelly_bet(self, win_rate: float, win_loss_ratio: float) -> float:
        """
        Calculate Kelly Criterion percentage.
        K% = W - (1-W)/R
        Where:
        W = Win Probability
        R = Win/Loss Ratio
        """
        if win_loss_ratio <= 0:
            return 0.0
            
        kelly_pct = win_rate - ((1 - win_rate) / win_loss_ratio)
        return max(0.0, kelly_pct) * self.kelly_fraction

    def get_target_allocation(self, capital: float, stop_loss_pct: float, 
                          win_rate: float = 0.55, win_loss_ratio: float = 2.0) -> float:
        """
        Calculate target dollar allocation for the trade.
        
        Args:
            capital: Available capital.
            stop_loss_pct: Percentage distance to stop loss (e.g., 0.10 for 10%).
            win_rate: Estimated win rate of the strategy.
            win_loss_ratio: Estimated risk/reward ratio.
            
        Returns:
            Float: Dollar amount to allocate to this trade.
        """
        # 1. Calculate Kelly Size (Optimal % of bankroll to bet)
        kelly_pct = self.calculate_kelly_bet(win_rate, win_loss_ratio)
        
        # 2. Cap by max risk constraint
        # PositionSize * StopLossPct <= Capital * MaxRiskPerTrade
        # PositionSize <= (Capital * MaxRiskPerTrade) / StopLossPct
        
        # Convert Kelly % to raw dollar amount
        kelly_dollar_allocation = capital * kelly_pct
        
        # Risk-based dollar allocation
        risk_dollar_allocation = (capital * self.max_risk_per_trade) / stop_loss_pct if stop_loss_pct > 0 else 0
        
        # Take the smaller of the two
        allocation = min(kelly_dollar_allocation, risk_dollar_allocation)
        
        return allocation
