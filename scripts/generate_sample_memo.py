from src.utils.trade_memo import TradeMemoGenerator
from src.core.market_regime import MarketRegime, RegimeState

# Simulate a valid signal
signal = {
    'ticker': 'AMD',
    'action': 'BUY',
    'strategy': 'VolBreakout',
    'expiry': '2025-11-28',
    'strike': 150.0,
    'option_type': 'call',
    'option_price': 2.50,
    'quantity': 4,
    'allocation': 1000.0
}

# Simulate Market Regime
regime = {
    'state': RegimeState.BULLISH,
    'details': {'vix': 18.5, 'trend': 'Uptrend'}
}

generator = TradeMemoGenerator()
path = generator.generate_memo(signal, regime)

print(f"Sample Memo Generated: {path}")
