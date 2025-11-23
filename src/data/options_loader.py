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

    def get_atm_iv(self, ticker: str, expiry: str) -> float:
        """
        Calculates the average Implied Volatility (IV) of the At-The-Money (ATM) options.
        Returns 0.0 if data is missing.
        """
        try:
            chain = self.get_option_chain(ticker, expiry)
            calls = chain['calls']
            puts = chain['puts']
            
            if calls.empty and puts.empty:
                return 0.0
                
            # Combine or just use calls (usually sufficient for IV proxy)
            # We'll use calls for now as we are mostly buying calls/puts directionally
            if calls.empty:
                return 0.0
                
            if 'impliedVolatility' not in calls.columns:
                return 0.0
                
            # Get current price (approximate from strike closest to ATM)
            # Ideally we pass current price, but to keep signature simple we'll infer or fetch
            # For speed, let's assume the caller might want to pass it, but here we'll just use the middle strike
            # Actually, let's fetch the price to be accurate.
            t = yf.Ticker(ticker)
            current_price = t.fast_info.last_price
            if not current_price:
                hist = t.history(period="1d")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
            
            if not current_price:
                return 0.0
                
            # Find ATM
            calls['abs_diff'] = abs(calls['strike'] - current_price)
            atm_calls = calls.sort_values('abs_diff').head(4) # Top 4 closest strikes
            
            avg_iv = atm_calls['impliedVolatility'].mean()
            return avg_iv
            
        except Exception as e:
            print(f"Error calculating ATM IV for {ticker}: {e}")
            return 0.0
