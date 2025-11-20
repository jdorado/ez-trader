import yfinance as yf
import pandas as pd
from enum import Enum
from typing import Dict, Any

class RegimeState(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    VOLATILE = "VOLATILE"
    NEUTRAL = "NEUTRAL"

class MarketRegime:
    """
    Analyzes macro factors to determine the current market regime.
    Factors: VIX (Fear), TNX (Rates), SPY vs IWM (Breadth).
    """
    
    def __init__(self):
        self.tickers = {
            'VIX': '^VIX',
            'TNX': '^TNX',
            'SPY': 'SPY',
            'IWM': 'IWM'
        }

    def analyze_regime(self) -> Dict[str, Any]:
        """
        Analyze market conditions and return regime state.
        """
        data = {}
        try:
            # Fetch latest data for all tickers
            # Using download for batch fetching might be faster but individual is safer for mixed assets
            for name, ticker in self.tickers.items():
                t = yf.Ticker(ticker)
                hist = t.history(period="5d")
                if not hist.empty:
                    data[name] = hist
                else:
                    print(f"Warning: No data for {name}")
                    
        except Exception as e:
            print(f"Error fetching regime data: {e}")
            return {'state': RegimeState.NEUTRAL, 'details': 'Error fetching data'}

        if not data:
            return {'state': RegimeState.NEUTRAL, 'details': 'No data available'}

        # 1. VIX Check
        vix_level = data.get('VIX', pd.DataFrame())['Close'].iloc[-1] if 'VIX' in data else 20.0
        
        # 2. Trend Check (SPY > 200 SMA? - approximating with 5d trend for now, need longer history for real SMA)
        # For this snippet, we'll look at short term momentum
        spy_ret = 0.0
        if 'SPY' in data:
            spy_close = data['SPY']['Close']
            spy_ret = (spy_close.iloc[-1] / spy_close.iloc[0]) - 1

        # 3. Breadth Check (IWM vs SPY)
        breadth_ratio = 1.0
        if 'IWM' in data and 'SPY' in data:
            iwm_ret = (data['IWM']['Close'].iloc[-1] / data['IWM']['Close'].iloc[0]) - 1
            breadth_ratio = iwm_ret - spy_ret # Positive means small caps outperforming

        # Determine Regime
        state = RegimeState.NEUTRAL
        details = []

        if vix_level > 25:
            state = RegimeState.VOLATILE
            details.append(f"High VIX ({vix_level:.2f})")
        elif vix_level > 18:
            # Caution zone
            if spy_ret < -0.01:
                state = RegimeState.BEARISH
                details.append(f"Elevated VIX ({vix_level:.2f}) + Falling SPY")
            else:
                state = RegimeState.NEUTRAL
                details.append(f"Elevated VIX ({vix_level:.2f}) but Market Holding")
        else:
            # Low VIX
            if spy_ret > 0:
                state = RegimeState.BULLISH
                details.append(f"Low VIX ({vix_level:.2f}) + Rising SPY")
                if breadth_ratio > 0:
                    details.append("Healthy Breadth (IWM > SPY)")
                else:
                    details.append("Narrow Breadth (SPY > IWM)")
            else:
                state = RegimeState.NEUTRAL
                details.append("Low VIX but Flat/Down Market")

        return {
            'state': state,
            'vix': vix_level,
            'spy_trend': spy_ret,
            'details': "; ".join(details)
        }

    def get_kelly_multipliers(self, state: RegimeState) -> Dict[str, float]:
        """
        Get the recommended Kelly fraction multipliers for Long and Short sides.
        Returns: {'long': float, 'short': float}
        """
        if state == RegimeState.BULLISH:
            return {'long': 1.0, 'short': 0.0} # Buy Dip, Don't Short
        elif state == RegimeState.NEUTRAL:
            return {'long': 0.5, 'short': 0.5} # Choppy, trade both sides smaller
        elif state == RegimeState.VOLATILE:
            return {'long': 0.25, 'short': 0.25} # High risk, small size
        elif state == RegimeState.BEARISH:
            return {'long': 0.0, 'short': 1.0} # Puts/Shorts Only
        return {'long': 0.0, 'short': 0.0}
