import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.data_aggregator import DataAggregator
import json

# Test with a single ticker to verify all fields
print("Testing data collection for AAPL...")
aggregator = DataAggregator(use_cache=False)  # Disable cache for clean test

snapshot = aggregator.generate_market_snapshot(['AAPL'])

if snapshot['tickers']:
    ticker_data = snapshot['tickers'][0]
    print("\n" + "="*60)
    print("AAPL Data Sample:")
    print("="*60)
    print(json.dumps(ticker_data, indent=2))
    
    # Verify all expected fields
    expected_fields = [
        'ticker', 'price', 'volume', 'z_score', 'hv', 'iv', 'iv_hv_ratio',
        'beta', 'next_expiry', 'market_cap', 'pe_ratio', 'sector', 'industry',
        '52w_high', '52w_low', 'pct_from_52w_high', 'pct_from_52w_low',
        'earnings_date', 'greeks', 'open_interest'
    ]
    
    print("\n" + "="*60)
    print("Field Verification:")
    print("="*60)
    missing = []
    for field in expected_fields:
        status = "✅" if field in ticker_data else "❌"
        value = ticker_data.get(field, "MISSING")
        print(f"{status} {field}: {value}")
        if field not in ticker_data:
            missing.append(field)
    
    if missing:
        print(f"\n⚠️ Missing fields: {missing}")
    else:
        print("\n✅ All fields present!")
else:
    print("❌ Failed to fetch data")
