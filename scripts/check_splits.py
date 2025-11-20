import yfinance as yf

ticker = "NFLX"
t = yf.Ticker(ticker)
print("--- Splits ---")
print(t.splits)

print("\n--- Actions ---")
print(t.actions)

print("\n--- Calendar (Earnings) ---")
try:
    print(t.calendar)
except Exception as e:
    print(e)
