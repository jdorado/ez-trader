from src.data.yfinance_loader import YahooFinanceLoader
from src.strategies.volatility import VolatilityStrategy
from src.data.options_loader import OptionsLoader
from src.core.market_regime import MarketRegime

ticker = "MSTR"
loader = YahooFinanceLoader()
opt_loader = OptionsLoader()

# 1. Check Data
print(f"--- Fetching Data for {ticker} ---")
data = loader.get_historical_data(ticker, start_date="2023-01-01")
print(f"Data Rows: {len(data)}")
if not data.empty:
    print(data.tail())

# 2. Check Strategy
print(f"\n--- Running Strategy (Threshold 1.5) ---")
strategy = VolatilityStrategy(ticker, z_score_threshold=1.5)
strategy.on_data({ticker: data})

# Access internal indicators for debugging
try:
    print(f"Price Z-Score: {strategy.last_z_score:.2f}")
    print(f"Vol (StdDev): {strategy.last_volatility:.4f}")
except AttributeError:
    print("Could not access internal indicators.")

signals = strategy.generate_signals()
print(f"Signals: {signals}")

# 3. Check Options if Signal Exists
if signals:
    print(f"\n--- Checking Options ---")
    expiry = opt_loader.get_nearest_expiration(ticker, min_days=2)
    print(f"Expiry: {expiry}")
    
    if expiry:
        chain = opt_loader.get_option_chain(ticker, expiry)
        puts = chain['puts']
        price = loader.get_latest_price(ticker)
        print(f"Current Price: {price}")
        
        # Filter for OTM Puts (Strike < Price)
        otm_puts = puts[puts['strike'] < price].sort_values('strike', ascending=False)
        
        print("\n--- OTM Puts Candidates ---")
        print(otm_puts[['contractSymbol', 'strike', 'lastPrice']].head(10))
        
        # Simulate Selector
        allocation = 1000.0
        found = False
        for _, row in otm_puts.iterrows():
            cost = row['lastPrice'] * 100
            if cost <= allocation:
                print(f"\n✅ FOUND CANDIDATE: Strike {row['strike']} @ ${row['lastPrice']} (Cost: ${cost:.2f})")
                found = True
                break
        
        if not found:
            print(f"\n❌ NO CANDIDATE FOUND under ${allocation}")
