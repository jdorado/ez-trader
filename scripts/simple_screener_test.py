import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.stock_screener import YahooFinanceScreener

def test_basic_import():
    print("Testing basic screener import...")
    screener = YahooFinanceScreener()
    print("✅ Screener class imported successfully")

def test_single_stock():
    print("\nTesting single stock metrics fetch...")
    screener = YahooFinanceScreener(['AAPL'])
    metrics = screener.fetch_stock_metrics('AAPL')

    if metrics:
        print("✅ AAPL metrics fetched successfully:")
        print(f"   Price: ${metrics.price:.2f}")
        print(f"   Market Cap: {metrics.market_cap}")
        print(f"   P/E Ratio: {metrics.pe_ratio}")
        print(f"   Volume: {metrics.volume}")
    else:
        print("❌ Failed to fetch AAPL metrics")

def test_small_screen():
    print("\nTesting small screening...")
    screener = YahooFinanceScreener(['AAPL', 'MSFT', 'NVDA'])

    filters = {
        'price_min': (1, None),  # Just basic price filter
    }

    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"✅ Found {len(results)} stocks matching criteria")
        print(results[['Ticker', 'Price']].to_string(index=False))
    else:
        print("❌ No stocks matched criteria")

if __name__ == "__main__":
    test_basic_import()
    test_single_stock()
    test_small_screen()
    print("\n--- Basic functionality test complete ---")
