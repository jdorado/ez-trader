import sys
import os
import glob
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.macro import MacroContext
from src.data.yfinance_loader import YahooFinanceLoader
from src.strategies.volatility import VolatilityStrategy
from src.utils.logger import logger

def verify_trades():
    print("--- 🔬 Final Multi-Factor Verification ---")
    
    # 1. Macro Alignment
    macro = MacroContext()
    ctx = macro.get_context()
    
    print(f"\n🌍 MACRO CONTEXT: {ctx['risk_level']}")
    print(f"   - OPEX: {ctx['is_opex']}")
    print(f"   - VIX: {ctx['vix']:.2f}")
    print(f"   - Rates: {ctx['rates_10y']:.2f}%")
    
    macro_bias = "NEUTRAL"
    if ctx['vix'] > 20 and ctx['rates_10y'] > 4.0:
        macro_bias = "BEARISH" # High Vol + High Rates = Risk Off
    elif ctx['vix'] < 15:
        macro_bias = "BULLISH"
        
    print(f"   -> MACRO BIAS: {macro_bias}")
    
    # 2. Analyze Approved Memos
    memo_dir = "memos/trades"
    memos = glob.glob(f"{memo_dir}/*.md")
    loader = YahooFinanceLoader()
    
    print(f"\n🔍 ANALYZING {len(memos)} TRADES...")
    print(f"{'TICKER':<8} {'ACTION':<6} {'TECH (Z)':<10} {'FUND (Earn)':<15} {'ALIGNMENT':<10}")
    print("-" * 60)
    
    for memo_path in memos:
        # Extract Ticker/Action from filename/content
        filename = os.path.basename(memo_path)
        parts = filename.split('_')
        if len(parts) < 3: continue
        ticker = parts[1]
        action = parts[2].replace('.md', '') # SELL or BUY
        
        # A. Technical Check (Z-Score)
        data = loader.get_historical_data(ticker, start_date="2024-01-01")
        strategy = VolatilityStrategy(ticker, z_score_threshold=1.5)
        strategy.on_data({ticker: data})
        strategy.generate_signals() # Populates last_z_score
        z_score = strategy.last_z_score
        
        tech_align = False
        if action == 'SELL' and z_score < -1.5: tech_align = True
        if action == 'BUY' and z_score > 1.5: tech_align = True
        
        # B. Fundamental/Safety Check (Earnings)
        # We use 'next_earnings' if available, or just check if recent
        # For now, we'll just check if data exists as a proxy for "tradable"
        fund_status = "OK"
        try:
            # Simple check: Is price > $5? (Penny stock filter)
            price = loader.get_latest_price(ticker)
            if price < 5: fund_status = "PENNY STOCK"
        except:
            fund_status = "NO DATA"
            
        # C. Alignment Verdict
        alignment = "❌ MISMATCH"
        if tech_align:
            if macro_bias == "BEARISH" and action == "SELL":
                alignment = "✅ STRONG"
            elif macro_bias == "BULLISH" and action == "BUY":
                alignment = "✅ STRONG"
            else:
                alignment = "⚠️ CONTRARIAN" # Valid signal but against macro
                
        print(f"{ticker:<8} {action:<6} {z_score:>8.2f}   {fund_status:<15} {alignment:<10}")

if __name__ == "__main__":
    verify_trades()
