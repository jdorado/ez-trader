import datetime
import calendar
import pandas as pd
from typing import Dict, Any, List, Optional
from src.data.yfinance_loader import YahooFinanceLoader
from src.utils.logger import logger

class MacroContext:
    """
    Analyzes macroeconomic context, including:
    - OPEX (Options Expiration) Cycles
    - Earnings Calendars
    - Macro Proxies (Rates, Dollar, VIX)
    """
    
    def __init__(self):
        self.loader = YahooFinanceLoader()
        
    def get_context(self) -> Dict[str, Any]:
        """Returns a summary of the current macro context."""
        today = datetime.date.today()
        
        context = {
            'date': today.strftime("%Y-%m-%d"),
            'is_opex': self.is_monthly_opex(today),
            'rates_10y': self._get_rate_proxy(),
            'dxy': self._get_dollar_proxy(),
            'vix': self._get_vix(),
            'earnings_today': [] # TODO: Implement earnings fetcher
        }
        
        context['risk_level'] = self._calculate_risk_level(context)
        return context

    def is_monthly_opex(self, date: datetime.date) -> bool:
        """
        Checks if the given date is a Monthly OPEX (3rd Friday of the month).
        """
        if date.weekday() != 4: # Friday is 4
            return False
            
        # Get all Fridays in the month
        c = calendar.Calendar(firstweekday=calendar.MONDAY)
        monthcal = c.monthdatescalendar(date.year, date.month)
        fridays = [day for week in monthcal for day in week if day.weekday() == 4 and day.month == date.month]
        
        if len(fridays) >= 3:
            return date == fridays[2] # 3rd Friday
            
        return False

    def _get_rate_proxy(self) -> float:
        """Fetches 10-Year Treasury Yield (^TNX)."""
        try:
            price = self.loader.get_latest_price("^TNX")
            return price
        except:
            return 0.0

    def _get_dollar_proxy(self) -> float:
        """Fetches US Dollar Index (DX-Y.NYB)."""
        try:
            # Yahoo often uses DX-Y.NYB or similar
            price = self.loader.get_latest_price("DX-Y.NYB")
            if price == 0:
                 price = self.loader.get_latest_price("DX=F") # Futures fallback
            return price
        except:
            return 0.0
            
    def _get_vix(self) -> float:
        """Fetches VIX."""
        try:
            return self.loader.get_latest_price("^VIX")
        except:
            return 0.0

    def _calculate_risk_level(self, context: Dict[str, Any]) -> str:
        """Determines High/Medium/Low risk based on context."""
        risk = "LOW"
        reasons = []
        
        if context['is_opex']:
            risk = "HIGH"
            reasons.append("Monthly OPEX")
            
        if context['vix'] > 20:
            risk = "HIGH" if context['vix'] > 30 else "MEDIUM"
            reasons.append(f"VIX {context['vix']:.2f}")
            
        if context['rates_10y'] > 4.5: # Arbitrary high rate threshold
            risk = "MEDIUM"
            reasons.append(f"Rates {context['rates_10y']:.2f}%")
            
        return f"{risk} ({', '.join(reasons)})" if reasons else risk
