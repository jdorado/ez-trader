from src.data.yfinance_loader import YahooFinanceLoader
from src.data.options_loader import OptionsLoader

loader = YahooFinanceLoader()
opt_loader = OptionsLoader()

ticker = "NFLX"
price = loader.get_latest_price(ticker)
print(f"NFLX Price: {price}")

expiry = opt_loader.get_nearest_expiration(ticker, min_days=2)
if expiry:
    chain = opt_loader.get_option_chain(ticker, expiry)
    puts = chain['puts']
    
    # Look for strikes near 110
    nearby = puts[(puts['strike'] >= 100) & (puts['strike'] <= 120)]
    print("Strikes near $110:")
    print(nearby[['contractSymbol', 'strike', 'lastPrice', 'volume', 'openInterest']])
