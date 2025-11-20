from src.data.yfinance_loader import YahooFinanceLoader
from src.data.options_loader import OptionsLoader

loader = YahooFinanceLoader()
opt_loader = OptionsLoader()

ticker = "NFLX"
price = loader.get_latest_price(ticker)
print(f"NFLX Price: {price}")

expiry = opt_loader.get_nearest_expiration(ticker, min_days=2)
print(f"Expiry: {expiry}")

if expiry:
    chain = opt_loader.get_option_chain(ticker, expiry)
    puts = chain['puts']
    
    # Check the $500 strike
    target = puts[puts['strike'] == 500.0]
    if not target.empty:
        print("Target Option Found:")
        print(target[['contractSymbol', 'strike', 'lastPrice', 'volume', 'openInterest']])
    else:
        print("Target Strike $500 not found in chain.")
        
    # Check what the system thought was ATM
    puts['abs_diff'] = abs(puts['strike'] - price)
    atm = puts.sort_values('abs_diff').iloc[0]
    print(f"Actual ATM Strike: {atm['strike']} (Price: {atm['lastPrice']})")
