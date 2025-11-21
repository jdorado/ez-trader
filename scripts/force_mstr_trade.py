import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader
from src.data.options_loader import OptionsLoader
from src.strategies.volatility import VolatilityStrategy
from src.core.market_regime import MarketRegime
from src.utils.trade_memo import TradeMemoGenerator
from src.utils.logger import logger

def force_mstr_trade():
    ticker = "MSTR"
    logger.info(f"--- Forcing Trade Generation for {ticker} ---")
    
    # 1. Load Data
    loader = YahooFinanceLoader()
    opt_loader = OptionsLoader()
    memo_gen = TradeMemoGenerator()
    
    data = loader.get_historical_data(ticker, start_date="2023-01-01")
    
    # 2. Run Strategy (Just to get context, but we will force signal)
    strategy = VolatilityStrategy(ticker, z_score_threshold=1.5)
    strategy.on_data({ticker: data})
    
    # Force Signal Construction
    logger.info("Forcing Signal Construction (Bypassing Strategy Threshold)...")
    sig = {
        'ticker': ticker,
        'action': 'SELL', # Assuming we want to short the drop
        'allocation': 1000.0,
        'strategy': 'VolBreakout (Manual)'
    }
    logger.info(f"Forced Signal: {sig}")
    
    # 3. Smart Contract Selection (Manual Implementation for this script)
    # We want the $185 Put (or similar)
    expiry = opt_loader.get_nearest_expiration(ticker, min_days=2)
    chain = opt_loader.get_option_chain(ticker, expiry)
    puts = chain['puts']
    price = loader.get_latest_price(ticker)
    
    # Filter OTM
    otm_puts = puts[puts['strike'] < price].sort_values('strike', ascending=False)
    
    selected_contract = None
    allocation = sig['allocation']
    
    for _, row in otm_puts.iterrows():
        cost = row['lastPrice'] * 100
        if cost <= allocation:
            selected_contract = row
            break
            
    if selected_contract is not None:
        # Update Signal
        sig['contract'] = selected_contract['contractSymbol']
        sig['expiry'] = expiry
        sig['strike'] = selected_contract['strike']
        sig['option_price'] = selected_contract['lastPrice']
        sig['quantity'] = int(allocation // (selected_contract['lastPrice'] * 100))
        sig['option_type'] = 'put'
        
        logger.info(f"Selected Contract: {sig['contract']} @ ${sig['option_price']}")
        
        # 4. Generate Memo
        # Need regime for memo
        regime_analyzer = MarketRegime()
        regime = regime_analyzer.analyze_regime()
        
        memo_path = memo_gen.generate_memo(sig, regime)
        logger.info(f"📝 Memo Generated: {memo_path}")
        
        logger.tweet(f"AGGRESSIVE PLAY: {sig['action']} {sig['ticker']} | Vol Breakout | Buy {sig['expiry']} ${sig['strike']} {sig['option_type'].upper()} @ ${sig['option_price']:.2f} | Qty: {sig['quantity']} | Alloc: ${sig['allocation']:.2f}")
        logger.tweet(f"👉 Review Memo: {memo_path}")
        
    else:
        logger.error("Could not find affordable contract.")

if __name__ == "__main__":
    force_mstr_trade()
