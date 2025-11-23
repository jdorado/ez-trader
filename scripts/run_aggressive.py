import sys
import os
import concurrent.futures
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader
from src.data.options_loader import OptionsLoader
from src.strategies.volatility import VolatilityStrategy
from src.core.market_regime import MarketRegime
from src.data.universe import UniverseLoader
from src.core.safety import CorporateActionChecker
from src.core.cache_manager import CacheManager
from src.utils.logger import logger

# Global instances to be shared across threads (if thread-safe) or re-instantiated
# yfinance and our loaders should be thread-safe for read operations
loader = YahooFinanceLoader()
opt_loader = OptionsLoader()
safety_checker = CorporateActionChecker()
cache = CacheManager()

def analyze_ticker(ticker: str, multipliers: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Analyzes a single ticker for volatility breakouts.
    """
    try:
        # 0. Check Cache for Safety Result (Optimization)
        # Safety checks involve API calls, so caching them is good.
        safety_key = f"safety:{ticker}:{datetime.now().date()}"
        safety = cache.get(safety_key)
        
        if not safety:
            safety = safety_checker.check_safety(ticker)
            cache.set(safety_key, safety, ttl_seconds=3600*12) # Cache for 12 hours

        if not safety['safe']:
            # logger.warning(f"Skipping {ticker}: {safety['reason']}") # Too noisy for parallel
            return []

        # 1. Fetch Data (with Cache)
        # We'll cache the dataframe for a short period (e.g. 5 mins) to allow re-runs
        data_key = f"data:{ticker}:history"
        data = cache.get(data_key)
        
        if data is None:
            data = loader.get_historical_data(ticker, start_date="2023-01-01")
            if not data.empty:
                cache.set(data_key, data, ttl_seconds=300) # 5 min cache
        
        if data is None or data.empty:
            return []

        # 2. Run Strategy
        strategy = VolatilityStrategy(ticker, lookback_window=20, z_score_threshold=1.5)
        strategy.on_data({ticker: data})
        
        raw_signals = strategy.generate_signals()
        valid_signals = []
        
        for sig in raw_signals:
            action = sig['action']
            mult = multipliers['long'] if action == 'BUY' else multipliers['short']
            
            if mult > 0:
                sig['allocation'] *= mult
                
                # 3. Find Option (Heavy API call, do only if signal valid)
                option_type = 'call' if action == 'BUY' else 'put'
                expiry = opt_loader.get_nearest_expiration(ticker, min_days=2)
                
                if expiry:
                    chain = opt_loader.get_option_chain(ticker, expiry)
                    options_df = chain['calls'] if option_type == 'call' else chain['puts']
                    
                    if not options_df.empty:
                        current_price = loader.get_latest_price(ticker)
                        options_df['abs_diff'] = abs(options_df['strike'] - current_price)
                        atm_option = options_df.sort_values('abs_diff').iloc[0]
                        
                        contract_symbol = atm_option['contractSymbol']
                        strike = atm_option['strike']
                        last_price = atm_option['lastPrice']
                        
                        contract_cost = last_price * 100
                        allocation = sig.get('allocation', 0.0)
                        
                        # --- Smart Contract Selector ---
                        # If ATM is too expensive, look for OTM strikes
                        if contract_cost > allocation:
                            # logger.info(f"ATM too expensive (${contract_cost:.2f} > ${allocation:.2f}). Searching OTM...")
                            
                            # Filter for cheaper options
                            # For Puts: Strike < Current Price
                            # For Calls: Strike > Current Price
                            if option_type == 'call':
                                candidates = options_df[options_df['strike'] > current_price].sort_values('strike')
                            else:
                                candidates = options_df[options_df['strike'] < current_price].sort_values('strike', ascending=False)
                            
                            found_cheaper = False
                            for _, row in candidates.iterrows():
                                cost = row['lastPrice'] * 100
                                if cost > 0 and cost <= allocation:
                                    # Found a candidate!
                                    # TODO: Check Delta here if we had Greeks. For now, just take the first one (closest OTM)
                                    contract_symbol = row['contractSymbol']
                                    strike = row['strike']
                                    last_price = row['lastPrice']
                                    contract_cost = cost
                                    found_cheaper = True
                                    # logger.info(f"Found OTM Candidate: Strike {strike} @ ${last_price:.2f}")
                                    break
                            
                            if not found_cheaper:
                                # Still couldn't find one
                                continue

                        if contract_cost > 0:
                            quantity = int(allocation // contract_cost)
                            if quantity > 0:
                                # --- IV Check ---
                                # Calculate HV (Annualized)
                                returns = data['Close'].pct_change().dropna()
                                hv_series = returns.rolling(window=20).std().iloc[-1] * (252 ** 0.5)
                                
                                # Ensure float
                                hv = float(hv_series.iloc[0]) if isinstance(hv_series, pd.Series) else float(hv_series)
                                
                                # Get IV
                                iv = opt_loader.get_atm_iv(ticker, expiry)
                                
                                iv_hv_ratio = 0.0
                                if hv > 0:
                                    iv_hv_ratio = iv / hv
                                
                                logger.info(f"🔍 {ticker} IV Analysis: IV={iv:.2%} HV={hv:.2%} Ratio={iv_hv_ratio:.2f}")

                                # Filter Logic
                                if iv_hv_ratio > 1.5:
                                    logger.warning(f"⚠️ SKIPPING {ticker}: IV ({iv:.2%}) is too high relative to HV ({hv:.2%}). Ratio: {iv_hv_ratio:.2f}")
                                    continue
                                    
                                sig['contract'] = contract_symbol
                                sig['expiry'] = expiry
                                sig['strike'] = strike
                                sig['option_price'] = last_price
                                sig['quantity'] = quantity
                                sig['option_type'] = option_type
                                
                                # Add Metadata for Memo
                                sig['iv'] = iv
                                sig['hv'] = hv
                                sig['iv_hv_ratio'] = iv_hv_ratio
                                
                                valid_signals.append(sig)
        return valid_signals

    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        return []

def run_aggressive_analysis():
    logger.info("--- Starting Aggressive Strategy Analysis (Parallel) ---")
    
    # 0. Check Market Regime
    regime_analyzer = MarketRegime()
    regime = regime_analyzer.analyze_regime()
    
    logger.info(f"Market Regime: {regime['state'].value}")
    logger.info(f"Details: {regime['details']}")
    
    multipliers = regime_analyzer.get_kelly_multipliers(regime['state'])
    logger.info(f"Regime Multipliers: Long={multipliers['long']}x, Short={multipliers['short']}x")
    
    if multipliers['long'] == 0 and multipliers['short'] == 0:
        logger.warning("Market Regime is DANGEROUS (Cash Only). Aborting Aggressive Scans.")
        return

    # 1. Get Universe
    tickers = UniverseLoader.get_combined_universe()
    logger.info(f"Scanning Expanded Universe ({len(tickers)} tickers) with ThreadPool...")

    # 2. Parallel Execution
    start_time = datetime.now()
    all_signals = []
    
    # Initialize Memo Generator
    from src.utils.trade_memo import TradeMemoGenerator
    memo_gen = TradeMemoGenerator()
    
    # Use max_workers=1 to avoid rate limiting (yfinance/yahoo can be strict)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # Submit all tasks
        future_to_ticker = {executor.submit(analyze_ticker, ticker, multipliers): ticker for ticker in tickers}
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                signals = future.result()
                if signals:
                    all_signals.extend(signals)
                    for sig in signals:
                        # Generate Memo
                        memo_path = memo_gen.generate_memo(sig, regime)
                        logger.info(f"📝 Memo Generated: {memo_path}")
                        
                        logger.tweet(f"AGGRESSIVE PLAY: {sig['action']} {sig['ticker']} | Vol Breakout | Buy {sig['expiry']} ${sig['strike']} {sig['option_type'].upper()} @ ${sig['option_price']:.2f} | Qty: {sig['quantity']} | Alloc: ${sig['allocation']:.2f}")
                        logger.tweet(f"👉 Review Memo: {memo_path}")
            except Exception as exc:
                logger.error(f"{ticker} generated an exception: {exc}")

    duration = datetime.now() - start_time
    logger.info(f"--- Aggressive Analysis Complete in {duration} ---")
    logger.info(f"Total Signals Found: {len(all_signals)}")

if __name__ == "__main__":
    run_aggressive_analysis()
