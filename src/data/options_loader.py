import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

class OptionsLoader:
    """Data loader for Options data using yfinance."""
    
    def get_expirations(self, ticker: str) -> Tuple[str, ...]:
        """Get list of expiration dates for a ticker."""
        try:
            t = yf.Ticker(ticker)
            return t.options
        except Exception as e:
            print(f"Error fetching expirations for {ticker}: {e}")
            return ()

    def get_option_chain(self, ticker: str, expiration: str) -> Dict[str, pd.DataFrame]:
        """
        Get option chain for a specific expiration.
        Returns a dict with 'calls' and 'puts' DataFrames.
        """
        try:
            t = yf.Ticker(ticker)
            chain = t.option_chain(expiration)
            return {
                'calls': chain.calls,
                'puts': chain.puts
            }
        except Exception as e:
            print(f"Error fetching option chain for {ticker} on {expiration}: {e}")
            return {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}

    def get_nearest_expiration(self, ticker: str, min_days: int = 0) -> Optional[str]:
        """Get the nearest expiration date that is at least min_days away."""
        exps = self.get_expirations(ticker)
        if not exps:
            return None
            
        today = datetime.now().date()
        for exp in exps:
            exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
            days_to_exp = (exp_date - today).days
            if days_to_exp >= min_days:
                return exp
        return None
