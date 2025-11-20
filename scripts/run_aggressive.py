import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader
from src.data.options_loader import OptionsLoader
from src.strategies.volatility import VolatilityStrategy
from src.core.market_regime import MarketRegime
from src.utils.logger import logger

def run_aggressive_analysis():
    logger.info("--- Starting Aggressive Strategy Analysis (100x Goal) ---")
    
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

    # 1. Load Data
    loader = YahooFinanceLoader()
    opt_loader = OptionsLoader()
    
    # Use UniverseLoader to get tickers
    from src.data.universe import UniverseLoader
    tickers = UniverseLoader.get_combined_universe()
    
    logger.info(f"Scanning Expanded Universe ({len(tickers)} tickers): {tickers}")
    
    for ticker in tickers:
        try:
            # Fetch Data
            data = loader.get_historical_data(ticker, start_date="2023-01-01")
            if data.empty:
                continue
                
            # Run Volatility Strategy
            strategy = VolatilityStrategy(ticker, lookback_window=20, z_score_threshold=1.5)
            
            # We need to apply the correct multiplier based on the SIGNAL direction, 
            # but we don't know the signal yet. 
            # Solution: Pass the multipliers to the strategy or apply them after signal generation.
            # For now, let's generate signals first, then resize.
            
            strategy.on_data({ticker: data})
            
            raw_signals = strategy.generate_signals()
            signals = []
            
            for sig in raw_signals:
                action = sig['action']
                mult = multipliers['long'] if action == 'BUY' else multipliers['short']
                
                if mult > 0:
                    # Adjust allocation by multiplier
                    sig['allocation'] *= mult
                    signals.append(sig)
                else:
                    logger.info(f"Skipping {action} signal on {ticker} due to Regime (Mult=0.0)")
            
            if signals:
                for signal in signals:
                    logger.info(f"🔥 SIGNAL FOUND: {signal}")
                    
                    # 2. Find Option Contract
                    action = signal['action']
                    # If BUY signal -> Call, If SELL signal -> Put
                    option_type = 'call' if action == 'BUY' else 'put'
                    
                    # Get nearest expiration (e.g., > 2 days out to avoid 0DTE risk for now)
                    expiry = opt_loader.get_nearest_expiration(ticker, min_days=2)
                    
                    if expiry:
                        logger.info(f"Targeting Expiry: {expiry}")
                        chain = opt_loader.get_option_chain(ticker, expiry)
                        options_df = chain['calls'] if option_type == 'call' else chain['puts']
                        
                        if not options_df.empty:
                            # Find ATM Option
                            current_price = loader.get_latest_price(ticker)
                            # Find strike closest to current price
                            options_df['abs_diff'] = abs(options_df['strike'] - current_price)
                            atm_option = options_df.sort_values('abs_diff').iloc[0]
                            
                            contract_symbol = atm_option['contractSymbol']
                            strike = atm_option['strike']
                            last_price = atm_option['lastPrice']
                            
                            # Calculate Quantity based on Option Price (x100 multiplier)
                            # Allocation is in Dollars. Contract Cost = Price * 100.
                            contract_cost = last_price * 100
                            allocation = signal.get('allocation', 0.0)
                            
                            if contract_cost > 0:
                                quantity = int(allocation // contract_cost)
                                # Ensure at least 1 contract if allocation allows (or maybe we skip if too expensive?)
                                if quantity == 0 and allocation > contract_cost * 0.5:
                                     # Aggressive: If we have >50% of the cash needed, maybe we take it? 
                                     # For now, strict check.
                                     pass
                            else:
                                quantity = 0
                            
                            if quantity > 0:
                                logger.tweet(f"AGGRESSIVE PLAY: {action} {ticker} | Vol Breakout | Buy {expiry} ${strike} {option_type.upper()} @ ${last_price:.2f} | Qty: {quantity} | Alloc: ${allocation:.2f}")
                            else:
                                logger.warning(f"Option too expensive for allocation. Cost: ${contract_cost:.2f}, Alloc: ${allocation:.2f}")
                        else:
                            logger.warning(f"No options found for {expiry}")
                    else:
                        logger.warning(f"No valid expiration found for {ticker}")
            else:
                logger.info(f"No volatility signal for {ticker}")
                
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")

    logger.info("--- Aggressive Analysis Complete ---")

if __name__ == "__main__":
    run_aggressive_analysis()
