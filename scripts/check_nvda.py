import yfinance as yf
ticker = yf.Ticker('NVDA')
price = ticker.fast_info.last_price
print(f"NVDA Current Price: ${price:.2f}")
