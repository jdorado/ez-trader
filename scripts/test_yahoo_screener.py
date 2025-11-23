import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.stock_screener import YahooFinanceScreener, ScreenerCriteria
from src.data.universe import UniverseLoader


def test_basic_screener():
    """Test basic screener functionality"""
    print("--- 🧐 Yahoo Finance Stock Screener POC ---")

    # Get a sample universe
    tickers = UniverseLoader.get_combined_universe()[:10]  # Limit for testing to avoid timeouts
    print(f"Testing with {len(tickers)} tickers: {tickers}")

    # Initialize screener
    screener = YahooFinanceScreener(tickers)

    # Test 1: Large cap dividend stocks
    print("\n--- 📊 Test 1: Large Cap Dividend Stocks ---")
    filters = {
        ScreenerCriteria.PRICE_MIN.value: (10, None),  # Min $10
        ScreenerCriteria.MARKET_CAP_MIN.value: (10e9, None),  # Min $10B market cap
        ScreenerCriteria.DIVIDEND_YIELD_MIN.value: (0.02, None),  # Min 2% dividend yield
    }

    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"Found {len(results)} matching stocks:")
        print(results[['Ticker', 'Price', 'Market Cap', 'Dividend Yield']].to_string(index=False))
    else:
        print("No stocks matched the criteria")

    # Test 2: Growth stocks
    print("\n--- 📈 Test 2: Growth Stocks ---")
    filters = {
        ScreenerCriteria.PRICE_MIN.value: (5, None),  # Min $5
        ScreenerCriteria.MARKET_CAP_MIN.value: (1e9, None),  # Min $1B
        ScreenerCriteria.PE_RATIO_MAX.value: (None, 30),  # P/E < 30
        ScreenerCriteria.BETA_MIN.value: (1.0, None),  # Beta > 1.0
    }

    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"Found {len(results)} matching stocks:")
        print(results[['Ticker', 'Price', 'P/E Ratio', 'Beta']].to_string(index=False))
    else:
        print("No stocks matched the criteria")

    # Test 3: Value stocks
    print("\n--- 💰 Test 3: Value Stocks ---")
    filters = {
        ScreenerCriteria.PRICE_MIN.value: (5, None),  # Min $5
        ScreenerCriteria.MARKET_CAP_MIN.value: (500e6, None),  # Min $500M
        ScreenerCriteria.PE_RATIO_MAX.value: (None, 15),  # P/E < 15
    }

    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"Found {len(results)} matching stocks:")
        print(results[['Ticker', 'Price', 'P/E Ratio', 'Market Cap']].to_string(index=False))
    else:
        print("No stocks matched the criteria")

    # Test 4: High volume stocks
    print("\n--- 📊 Test 4: High Volume Stocks ---")
    filters = {
        ScreenerCriteria.PRICE_MIN.value: (1, None),  # Min $1
        ScreenerCriteria.VOLUME_MIN.value: (1e6, None),  # Min 1M daily volume
    }

    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"Found {len(results)} matching stocks:")
        print(results[['Ticker', 'Price', 'Volume']].to_string(index=False))
    else:
        print("No stocks matched the criteria")


def test_custom_filters():
    """Test custom filter combinations"""
    print("\n--- 🎯 Test 5: Custom Filters (Mid-cap, Moderate P/E) ---")

    # Custom filter: Mid-cap stocks with moderate P/E
    tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'NFLX', 'GOOGL', 'META']
    screener = YahooFinanceScreener(tickers)

    filters = {
        ScreenerCriteria.PRICE_MIN.value: (50, None),  # Min $50
        ScreenerCriteria.PRICE_MAX.value: (None, 500),  # Max $500
        ScreenerCriteria.MARKET_CAP_MIN.value: (50e9, None),  # Min $50B
        ScreenerCriteria.MARKET_CAP_MAX.value: (None, 2e12),  # Max $2T
        ScreenerCriteria.PE_RATIO_MIN.value: (10, None),  # Min P/E 10
        ScreenerCriteria.PE_RATIO_MAX.value: (None, 40),  # Max P/E 40
    }

    results = screener.screen_stocks(filters)
    if not results.empty:
        print(f"Found {len(results)} matching stocks:")
        print(results[['Ticker', 'Price', 'Market Cap', 'P/E Ratio']].to_string(index=False))
    else:
        print("No stocks matched the criteria")


def test_predefined_filters():
    """Test using predefined filter sets"""
    print("\n--- 🔧 Test 6: Predefined Filter Sets ---")

    screener = YahooFinanceScreener(['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'NFLX', 'JNJ', 'PG'])
    filter_sets = screener.get_popular_filters()

    for filter_name, filters in filter_sets.items():
        print(f"\n--- Testing {filter_name.replace('_', ' ').title()} ---")
        results = screener.screen_stocks(filters)
        if not results.empty:
            print(f"Found {len(results)} matching stocks:")
            print(results[['Ticker', 'Price']].to_string(index=False))
        else:
            print("No stocks matched the criteria")


def benchmark_screener():
    """Benchmark the screener performance"""
    print("\n--- ⚡ Performance Benchmark ---")

    # Test with moderate universe
    tickers = UniverseLoader.get_combined_universe()[:15]  # Test with 15 tickers
    screener = YahooFinanceScreener(tickers)

    start_time = datetime.now()

    # Simple filter
    filters = {
        ScreenerCriteria.PRICE_MIN.value: (1, None),
    }

    results = screener.screen_stocks(filters)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"Screened {len(tickers)} tickers in {duration:.2f} seconds")
    print(f"Found {len(results)} matching stocks")
    print(".2f")


if __name__ == "__main__":
    try:
        test_basic_screener()
        test_custom_filters()
        test_predefined_filters()
        benchmark_screener()

        print("\n--- ✅ Yahoo Finance Screener POC Complete ---")
        print("The screener can filter stocks by various criteria including:")
        print("- Price range")
        print("- Market capitalization")
        print("- Trading volume")
        print("- P/E ratio")
        print("- Dividend yield")
        print("- 52-week high/low")
        print("- Beta (volatility)")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
