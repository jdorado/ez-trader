import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.stock_screener import YahooFinanceScreener, ScreenerCriteria


def demo_screener():
    """Demonstrate Yahoo Finance stock screener capabilities"""
    print("🎯 Yahoo Finance Stock Screener POC Demo")
    print("=" * 50)

    # Test with major tech stocks
    tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'NFLX', 'GOOGL', 'META']
    screener = YahooFinanceScreener(tickers)

    print(f"📊 Screening {len(tickers)} stocks: {', '.join(tickers)}\n")

    # Demo 1: Large Cap Tech Stocks
    print("1️⃣ Large Cap Tech Stocks (Market Cap > $500B)")
    filters = {
        ScreenerCriteria.MARKET_CAP_MIN.value: (500e9, None),  # $500B+
    }
    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"✅ Found {len(results)} matches:")
        for _, row in results.iterrows():
            print(f"   {row['Ticker']}: ${row['Price']:.2f}, Market Cap: ${row['Market Cap']/1e9:.1f}B")
    else:
        print("❌ No matches found")

    # Demo 2: High Growth Stocks
    print("\n2️⃣ High Growth Stocks (P/E < 30, Beta > 1.0)")
    filters = {
        ScreenerCriteria.PE_RATIO_MAX.value: (None, 30),
        ScreenerCriteria.BETA_MIN.value: (1.0, None),
    }
    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"✅ Found {len(results)} matches:")
        for _, row in results.iterrows():
            print(f"   {row['Ticker']}: ${row['Price']:.2f}, Market Cap: ${row['Market Cap']/1e9:.1f}B")
    else:
        print("❌ No matches found")

    # Demo 3: Value Investing
    print("\n3️⃣ Value Stocks (Low P/E < 20)")
    filters = {
        ScreenerCriteria.PE_RATIO_MAX.value: (None, 20),
    }
    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"✅ Found {len(results)} matches:")
        for _, row in results.iterrows():
            print(f"   {row['Ticker']}: ${row['Price']:.2f}, Market Cap: ${row['Market Cap']/1e9:.1f}B")
    else:
        print("❌ No matches found")

    # Demo 4: Dividend Stocks
    print("\n4️⃣ Dividend Stocks (Yield > 0.5%)")
    filters = {
        ScreenerCriteria.DIVIDEND_YIELD_MIN.value: (0.005, None),  # 0.5%+
    }
    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"✅ Found {len(results)} matches:")
        for _, row in results.iterrows():
            print(f"   {row['Ticker']}: ${row['Price']:.2f}, Market Cap: ${row['Market Cap']/1e9:.1f}B")
    else:
        print("❌ No matches found")

    # Demo 5: Custom Combination
    print("\n5️⃣ Custom Filter: Mid-Cap, Moderate P/E")
    filters = {
        ScreenerCriteria.PRICE_MIN.value: (50, None),
        ScreenerCriteria.PRICE_MAX.value: (None, 300),
        ScreenerCriteria.PE_RATIO_MIN.value: (15, None),
        ScreenerCriteria.PE_RATIO_MAX.value: (None, 35),
    }
    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"✅ Found {len(results)} matches:")
        for _, row in results.iterrows():
            print(f"   {row['Ticker']}: ${row['Price']:.2f}, Market Cap: ${row['Market Cap']/1e9:.1f}B")
    else:
        print("❌ No matches found")

    print("\n" + "=" * 50)
    print("🎉 POC Complete! Key Features Demonstrated:")
    print("✅ Fetches real-time stock metrics from Yahoo Finance")
    print("✅ Filters by price, market cap, P/E ratio, volume, beta")
    print("✅ Supports dividend yield and 52-week high/low filters")
    print("✅ Configurable filter combinations")
    print("✅ Rate-limited API calls to avoid throttling")
    print("✅ Returns structured DataFrame results")


if __name__ == "__main__":
    demo_screener()
