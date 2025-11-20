import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader
from src.strategies.sma_crossover import SMACrossoverStrategy
from src.utils.logger import logger

def run_daily_analysis():
    logger.info("--- Starting Daily Analysis ---")
    
    # 1. Load Data
    loader = YahooFinanceLoader()
    tickers = ["SPY", "QQQ", "IWM", "AAPL", "NVDA", "TSLA"] # Watchlist
    
    logger.info(f"Analyzing tickers: {tickers}")
    
    # 2. Run Strategies
    opportunities = []
    
    for ticker in tickers:
        try:
            # Fetch enough data for 200 SMA
            data = loader.get_historical_data(ticker, start_date="2023-01-01") # Adjust date dynamically in real app
            if data.empty:
                continue
                
            strategy = SMACrossoverStrategy(ticker)
            # Feed data to strategy
            strategy.on_data({ticker: data})
            
            signals = strategy.generate_signals()
            if signals:
                for signal in signals:
                    opportunities.append(signal)
                    logger.info(f"SIGNAL FOUND: {signal}")
                    logger.tweet(f"Daily Scan: {signal['action']} Signal for ${signal['ticker']} (SMA Crossover)")
            else:
                logger.info(f"No signal for {ticker}")
                
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")

    # 3. Report
    from src.utils.report_generator import ReportGenerator
    
    # Mock portfolio summary for now (since we aren't persisting state yet)
    portfolio_summary = {
        'total_value': 10000.0,
        'cash': 10000.0,
        'pnl': 0.0,
        'positions': {}
    }
    
    generator = ReportGenerator()
    report_path = generator.generate_daily_report(opportunities, portfolio_summary)
    logger.info(f"Daily report saved to: {report_path}")

    if not opportunities:
        logger.info("No opportunities found today.")
        logger.tweet("Daily Scan: No new signals generated today. Monitoring market conditions.")
    
    logger.info("--- Daily Analysis Complete ---")

if __name__ == "__main__":
    run_daily_analysis()
