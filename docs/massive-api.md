# Polygon.io API Guide

This guide explains how to use the Polygon.io API for fetching market data when an agent needs data for processing.

## Overview

Polygon.io provides comprehensive access to historical and real-time market data from major U.S. exchanges. The API supports:
- **REST API**: For one-time queries and filtered data requests (v2 and v3 endpoints)
- **WebSocket API**: For real-time streaming market data
- **Flat Files**: For downloadable historical data in CSV format

## Authentication

All API requests require authentication using an API key stored in the `POLYGON_API_KEY` environment variable.

### REST API Authentication

Authenticate REST requests by including the API key as a query parameter:

```
?apiKey=YOUR_API_KEY
```

## REST API Usage

### Base URLs

- **REST API v3**: `https://api.polygon.io/v3/`
- **REST API v2**: `https://api.polygon.io/v2/`

### Making Requests

All REST endpoints return data in a structured JSON format with the following common fields:
- `status`: Request status (`OK`, `DELAYED`, or `ERROR`)
- `results`: Array of data records
- `request_id`: Unique request identifier (v3)
- `count`: Number of results (some endpoints)

### Example: Universal Snapshot (v3)

```bash
curl "https://api.polygon.io/v3/snapshot?ticker.any_of=AAPL,MSFT&apiKey=${POLYGON_API_KEY}"
```

### Example: Candles/OHLCV (v2)

```bash
curl "https://api.polygon.io/v2/aggs/ticker/SPY/range/1/day/2025-11-15/2025-11-20?apiKey=${POLYGON_API_KEY}"
```

### Common Endpoints

**v3 Endpoints:**
- **Universal Snapshot**: `/v3/snapshot` - Get snapshots across asset classes (stocks, options, forex, crypto)
- **Options Snapshot**: `/v3/snapshot/options/{ticker}` - Get options snapshot for a symbol

**v2 Endpoints:**
- **Aggregates/Candles**: `/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}` - OHLCV data
- **Trades**: `/v2/ticks/stocks/trades/{ticker}/{date}` - Trade data
- **Quotes**: `/v2/ticks/stocks/nbbo/{ticker}/{date}` - Quote data

### Response Format Examples

**Universal Snapshot Response:**
```json
{
  "status": "OK",
  "request_id": "abc123",
  "results": [
    {
      "ticker": "AAPL",
      "session": {
        "price": 150.25
      }
    }
  ]
}
```

**Candles/Aggregates Response:**
```json
{
  "status": "OK",
  "results": [
    {
      "t": 1234567890000,
      "o": 150.00,
      "h": 151.00,
      "l": 149.50,
      "c": 150.50,
      "v": 12345678
    }
  ]
}
```

**Field Explanations:**
- `t`: Timestamp (Unix milliseconds)
- `o, c, h, l`: Open, Close, High, Low prices
- `v`: Volume

## Rate Limiting

Polygon.io implements rate limiting:
- Rate limit responses return HTTP 429 status
- `Retry-After` header indicates wait time
- Implement exponential backoff for retries
- Recommended: Space requests at least 0.5 seconds apart

## Async Usage Pattern

For production use, use async requests with proper rate limiting:

```python
import aiohttp
import asyncio

async def get_data(session, endpoint, params):
    params["apiKey"] = os.getenv("POLYGON_API_KEY")
    url = f"https://api.polygon.io/{endpoint}"
    
    async with session.get(url, params=params, timeout=30) as response:
        if response.status == 200:
            return await response.json()
        elif response.status == 429:
            # Handle rate limiting
            retry_after = response.headers.get("Retry-After", "3")
            await asyncio.sleep(float(retry_after))
            # Retry logic...
        else:
            raise Exception(f"Request failed: {response.status}")
```

## Environment Setup

Set the API key as an environment variable:

```bash
export POLYGON_API_KEY=your_api_key_here
```

Or load from `.env` file:
```bash
export $(cat .env | xargs)
```

In Python:
```python
import os
api_key = os.getenv('POLYGON_API_KEY')
```

## Testing

A working POC is available in `/pocs/test_polygon_api.py` that demonstrates:
- Universal Snapshot endpoint usage
- Candles/OHLCV endpoint usage
- Proper error handling and data parsing

Run it with:
```bash
poetry run python pocs/test_polygon_api.py
```

## References

- [Polygon.io API Documentation](https://polygon.io/docs)
- [Polygon.io Python Client](https://github.com/polygon-io/client-python)
