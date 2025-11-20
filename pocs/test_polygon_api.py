#!/usr/bin/env python3
"""
Simple POC: Test Polygon.io API connectivity
Showcases basic API usage with a few simple endpoints.
"""

import os
import sys
import json
import asyncio
import aiohttp
from typing import Dict


API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL_V3 = "https://api.polygon.io/v3"
BASE_URL_V2 = "https://api.polygon.io/v2"


async def test_universal_snapshot(session: aiohttp.ClientSession) -> bool:
    """Test universal snapshot endpoint - simple and reliable."""
    print("\n" + "="*60)
    print("Testing Universal Snapshot (v3)...")
    print("="*60)
    
    try:
        endpoint = f"{BASE_URL_V3}/snapshot"
        params = {
            "apiKey": API_KEY,
            "ticker.any_of": "AAPL,MSFT,GOOGL",
            "limit": 3
        }
        
        print(f"Request: GET {endpoint}")
        print(f"Symbols: AAPL, MSFT, GOOGL")
        
        async with session.get(endpoint, params=params, timeout=30) as response:
            if response.status == 200:
                data = await response.json()
                status = data.get('status', 'N/A')
                results = data.get('results', [])
                
                print(f"\n✅ Status: {status}")
                print(f"✅ Results: {len(results)} snapshot(s) received")
                
                if results:
                    print("\nFirst snapshot:")
                    first = results[0]
                    # Handle different response structures
                    if isinstance(first, dict):
                        ticker = first.get('ticker', 'N/A')
                        if isinstance(ticker, dict):
                            ticker = ticker.get('ticker', 'N/A')
                        # Try to find price in various locations
                        price = first.get('session', {}).get('price') or first.get('last_quote', {}).get('last', {}).get('price') or first.get('value', 'N/A')
                        print(f"  Ticker: {ticker}")
                        print(f"  Price: ${price}" if isinstance(price, (int, float)) else f"  Data: {json.dumps(first, indent=2)[:200]}")
                    else:
                        print(f"  Data: {str(first)[:200]}")
                
                return True
            else:
                text = await response.text()
                print(f"❌ Failed: Status {response.status}")
                print(f"Response: {text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_candles(session: aiohttp.ClientSession) -> bool:
    """Test candles/OHLCV endpoint."""
    print("\n" + "="*60)
    print("Testing Candles/OHLCV (v2)...")
    print("="*60)
    
    try:
        # Get last 5 days of daily candles for SPY
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        endpoint = f"{BASE_URL_V2}/aggs/ticker/SPY/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        params = {
            "apiKey": API_KEY,
            "adjusted": "true",
            "sort": "asc",
            "limit": 5
        }
        
        print(f"Request: GET {endpoint}")
        print(f"Symbol: SPY (last 5 days)")
        
        async with session.get(endpoint, params=params, timeout=30) as response:
            if response.status == 200:
                data = await response.json()
                status = data.get('status', 'N/A')
                results = data.get('results', [])
                
                print(f"\n✅ Status: {status}")
                print(f"✅ Results: {len(results)} candle(s) received")
                
                if results:
                    print("\nLatest candle:")
                    latest = results[-1]
                    print(f"  Date: {datetime.fromtimestamp(latest.get('t', 0) / 1000).strftime('%Y-%m-%d')}")
                    print(f"  Open: ${latest.get('o', 0):.2f}")
                    print(f"  High: ${latest.get('h', 0):.2f}")
                    print(f"  Low: ${latest.get('l', 0):.2f}")
                    print(f"  Close: ${latest.get('c', 0):.2f}")
                    print(f"  Volume: {latest.get('v', 0):,}")
                
                return True
            else:
                text = await response.text()
                print(f"❌ Failed: Status {response.status}")
                print(f"Response: {text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run API tests."""
    print("\n" + "="*60)
    print("Polygon.io API POC Test")
    print("="*60)
    
    if not API_KEY:
        print("\n❌ ERROR: POLYGON_API_KEY environment variable not set")
        print("Set it with: export POLYGON_API_KEY=your_key_here")
        print("Or load from .env file")
        sys.exit(1)
    
    print(f"\nUsing API key: {API_KEY[:10]}...{API_KEY[-4:]}")
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Universal snapshot
        test1 = await test_universal_snapshot(session)
        
        # Small delay between requests
        await asyncio.sleep(0.5)
        
        # Test 2: Candles
        test2 = await test_candles(session)
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Universal Snapshot: {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f"Candles/OHLCV:      {'✅ PASSED' if test2 else '❌ FAILED'}")
        
        if test1 and test2:
            print("\n🎉 All tests passed! Polygon.io API is working correctly.")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

