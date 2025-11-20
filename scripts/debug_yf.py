import yfinance as yf

ticker = "NFLX"
t = yf.Ticker(ticker)

print("--- Info Keys ---")
# print(t.info.keys()) # Too verbose
print(f"RegularMarketPrice: {t.info.get('regularMarketPrice')}")
print(f"CurrentPrice: {t.info.get('currentPrice')}")
print(f"PreviousClose: {t.info.get('previousClose')}")
print(f"Open: {t.info.get('open')}")

print("\n--- Fast Info ---")
try:
    print(f"Last Price: {t.fast_info['last_price']}")
except Exception as e:
    print(f"Fast Info Error: {e}")

print("\n--- History (1d) ---")
hist = t.history(period="1d")
print(hist)
