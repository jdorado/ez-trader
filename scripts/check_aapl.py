import yfinance as yf

ticker = "AAPL"
t = yf.Ticker(ticker)
print(f"AAPL Price: {t.info.get('regularMarketPrice')}")
hist = t.history(period="1d")
print(hist)
