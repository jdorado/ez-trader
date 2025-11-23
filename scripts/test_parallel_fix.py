import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.data_aggregator import DataAggregator
import json

# Test with multiple tickers to verify parallel execution
print("Testing parallel data collection for 5 tickers...")
aggregator = DataAggregator(use_cache=False, max_workers=5)

snapshot = aggregator.generate_market_snapshot(['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN'])

print("\n" + "="*60)
print("Verification: Each ticker should have unique price/volume")
print("="*60)

for ticker_data in snapshot['tickers']:
    print(f"{ticker_data['ticker']:<6} Price: ${ticker_data['price']:>8.2f}  Volume: {ticker_data['volume']:>12,}  Z-Score: {ticker_data['z_score']:>6.2f}")

# Check for duplicates
prices = [t['price'] for t in snapshot['tickers']]
volumes = [t['volume'] for t in snapshot['tickers']]

if len(set(prices)) == len(prices) and len(set(volumes)) == len(volumes):
    print("\n✅ SUCCESS: All tickers have unique data!")
else:
    print("\n❌ FAILED: Still seeing duplicate data")
    print(f"Unique prices: {len(set(prices))}/{len(prices)}")
    print(f"Unique volumes: {len(set(volumes))}/{len(volumes)}")
