import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader
from src.core.backtester import Backtester
from src.strategies.buy_and_hold import BuyAndHoldStrategy
from src.strategies.sma_crossover import SMACrossoverStrategy
from src.utils.logger import logger

def run_backtests():
    logger.info("Starting Backtests...")
    
    loader = YahooFinanceLoader()
    ticker = "SPY"
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    # 1. Buy and Hold
    logger.info(f"--- Backtesting Buy and Hold ({ticker}) ---")
    bh_strategy = BuyAndHoldStrategy(ticker)
    bh_backtester = Backtester(bh_strategy, loader)
    bh_backtester.run([ticker], start_date, end_date)
    
    final_val = bh_backtester.portfolio_value[-1]['value']
    logger.info(f"Buy and Hold Final Value: ${final_val:.2f}")
    logger.tweet(f"Backtest Result: Buy & Hold {ticker} turned $10k into ${final_val:.2f}")

    # 2. SMA Crossover
    logger.info(f"--- Backtesting SMA Crossover ({ticker}) ---")
    sma_strategy = SMACrossoverStrategy(ticker, short_window=50, long_window=200)
    sma_backtester = Backtester(sma_strategy, loader)
    sma_backtester.run([ticker], start_date, end_date)
    
    final_val_sma = sma_backtester.portfolio_value[-1]['value']
    logger.info(f"SMA Crossover Final Value: ${final_val_sma:.2f}")
    logger.tweet(f"Backtest Result: SMA Crossover {ticker} turned $10k into ${final_val_sma:.2f}")

if __name__ == "__main__":
    run_backtests()
