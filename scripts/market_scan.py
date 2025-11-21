import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.universe import UniverseLoader
from src.data.yfinance_loader import YahooFinanceLoader
from src.utils.logger import logger

def scan_market():
    logger.info("--- 🌍 Global Market Heatmap ---")
    
    loader = YahooFinanceLoader()
    tickers = UniverseLoader.get_combined_universe()
    
    results = []
    
    print(f"{'TICKER':<8} {'PRICE':<10} {'CHG %':<8} {'RANGE %':<8} {'Z-SCORE':<8} {'VOL (20d)':<10} {'STATUS':<10}")
    print("-" * 70)
    
    for ticker in tickers:
        try:
            # Fetch Data (Last 30 days to calculate Z-Score)
            df = loader.get_historical_data(ticker, start_date=(datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"))
            
            if df.empty:
                print(f"DEBUG: {ticker} - Empty DataFrame")
                continue
            
            if len(df) < 21:
                print(f"DEBUG: {ticker} - Insufficient Data ({len(df)} rows)")
                continue
                
            # Calculate Metrics
            close = df['Close']
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
                
            high = df['High']
            if isinstance(high, pd.DataFrame):
                high = high.iloc[:, 0]
                
            low = df['Low']
            if isinstance(low, pd.DataFrame):
                low = low.iloc[:, 0]
            
            # 1. Daily Return
            current_price = close.iloc[-1]
            prev_price = close.iloc[-2]
            pct_change = (current_price - prev_price) / prev_price * 100
            
            # 2. Intraday Range (High - Low) / Open
            # Using yesterday's full candle
            open_price = df['Open']
            if isinstance(open_price, pd.DataFrame):
                open_price = open_price.iloc[:, 0]
                
            daily_range_pct = (high.iloc[-1] - low.iloc[-1]) / open_price.iloc[-1] * 100
            
            # 3. Z-Score (Price Change)
            returns = close.pct_change().dropna()
            rolling_mean = returns.rolling(window=20).mean()
            rolling_std = returns.rolling(window=20).std()
            
            current_ret = returns.iloc[-1]
            mean = rolling_mean.iloc[-1]
            std = rolling_std.iloc[-1]
            
            if std > 0:
                z_score = (current_ret - mean) / std
            else:
                z_score = 0.0
                
            # 4. Volatility (Annualized)
            vol_20d = std * np.sqrt(252) * 100
            
            # Status Flag
            status = ""
            if abs(z_score) > 1.5:
                status += "🔥 Z-BREAK "
            if daily_range_pct > 5.0:
                status += "🌊 RANGE "
            if abs(pct_change) > 5.0:
                status += "🚀 MOVE "
                
            results.append({
                'Ticker': ticker,
                'Price': current_price,
                'Change': pct_change,
                'Range': daily_range_pct,
                'Z-Score': z_score,
                'Vol': vol_20d,
                'Status': status
            })
            
            # Print Row
            print(f"{ticker:<8} ${current_price:<9.2f} {pct_change:>6.2f}% {daily_range_pct:>7.2f}% {z_score:>7.2f} {vol_20d:>9.1f}% {status}")
            
        except Exception as e:
            logger.error(f"Error scanning {ticker}: {e}")
            continue

    # Summary Analysis
    df_res = pd.DataFrame(results)
    if not df_res.empty:
        # Save to CSV
        csv_path = "reports/market_scan.csv"
        df_res.to_csv(csv_path, index=False)
        print(f"\n✅ Market Scan saved to {csv_path}")
        
        print("\n--- 🏆 Top Movers (Abs Change) ---")
        df_res['AbsChange'] = df_res['Change'].abs()
        print(df_res.sort_values('AbsChange', ascending=False).head(5)[['Ticker', 'Price', 'Change', 'Status']])
        
        print("\n--- 🌪 Top Volatility (Z-Score) ---")
        df_res['AbsZ'] = df_res['Z-Score'].abs()
        print(df_res.sort_values('AbsZ', ascending=False).head(5)[['Ticker', 'Z-Score', 'Vol', 'Status']])
    else:
        print("No results found.")

if __name__ == "__main__":
    scan_market()
