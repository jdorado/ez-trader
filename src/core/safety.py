import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any

class CorporateActionChecker:
    """
    Checks for corporate actions (Splits, Earnings) that might distort data or introduce binary risk.
    """
    
    def __init__(self):
        pass

    def check_safety(self, ticker: str) -> Dict[str, Any]:
        """
        Checks if a ticker is safe to trade.
        Returns: {'safe': bool, 'reason': str}
        """
        try:
            t = yf.Ticker(ticker)
            
            # 1. Check for Recent Splits (Last 30 days)
            # Splits often cause data glitches in feeds for a few days/weeks
            splits = t.splits
            if not splits.empty:
                last_split_date = splits.index[-1].to_pydatetime().replace(tzinfo=None)
                days_since_split = (datetime.now() - last_split_date).days
                if days_since_split < 30:
                    return {'safe': False, 'reason': f"Recent Split on {last_split_date.date()} ({days_since_split} days ago)"}

            # 2. Check for Upcoming Earnings (Next 7 days)
            # Binary risk event. Avoid unless specifically targeting earnings.
            calendar = t.calendar
            if calendar and 'Earnings Date' in calendar:
                earnings_dates = calendar['Earnings Date']
                # Handle list of dates
                for date in earnings_dates:
                    # Convert to datetime if it's a date object
                    if hasattr(date, 'date'):
                        # It's already a date/datetime
                        check_date = date
                    else:
                        continue
                        
                    # Normalize to datetime for comparison
                    if isinstance(check_date, datetime):
                        check_date = check_date.replace(tzinfo=None)
                    else:
                        check_date = datetime.combine(check_date, datetime.min.time())

                    days_to_earnings = (check_date - datetime.now()).days
                    if 0 <= days_to_earnings <= 7:
                         return {'safe': False, 'reason': f"Earnings upcoming on {check_date.date()} ({days_to_earnings} days)"}

            return {'safe': True, 'reason': "OK"}

        except Exception as e:
            # If we can't verify, warn but maybe don't block? Or block to be safe?
            # For aggressive 100x, maybe block.
            return {'safe': False, 'reason': f"Error checking safety: {e}"}
