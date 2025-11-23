import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader
from src.data.options_loader import OptionsLoader
from src.strategies.volatility import VolatilityStrategy
from src.core.safety import CorporateActionChecker
from src.utils.logger import logger

def test_aapl():
    ticker = "AAPL"
    logger.info(f"=== Testing {ticker} ===")
    
    # 1. Test Data Loader
    logger.info("1. Testing YahooFinanceLoader...")
    loader = YahooFinanceLoader()
    data = loader.get_historical_data(ticker, start_date="2023-01-01")
    logger.info(f"   Data shape: {data.shape}")
    logger.info(f"   Columns: {data.columns.tolist()}")
    logger.info(f"   Data['Close'] type: {type(data['Close'])}")
    logger.info(f"   Last 3 rows:\n{data.tail(3)}")
    
    # 2. Test Latest Price
    logger.info("\n2. Testing get_latest_price...")
    price = loader.get_latest_price(ticker)
    logger.info(f"   Latest price: ${price:.2f}")
    
    # 3. Test Safety Checker
    logger.info("\n3. Testing CorporateActionChecker...")
    safety_checker = CorporateActionChecker()
    safety = safety_checker.check_safety(ticker)
    logger.info(f"   Safe: {safety['safe']}")
    logger.info(f"   Reason: {safety.get('reason', 'N/A')}")
    
    # 4. Test Volatility Strategy
    logger.info("\n4. Testing VolatilityStrategy...")
    strategy = VolatilityStrategy(ticker, lookback_window=20, z_score_threshold=1.5)
    strategy.on_data({ticker: data})
    signals = strategy.generate_signals()
    logger.info(f"   Signals generated: {len(signals)}")
    if signals:
        logger.info(f"   Signal details: {signals[0]}")
    
    # 5. Test Options Loader
    logger.info("\n5. Testing OptionsLoader...")
    opt_loader = OptionsLoader()
    expiry = opt_loader.get_nearest_expiration(ticker, min_days=2)
    logger.info(f"   Nearest expiry: {expiry}")
    
    if expiry:
        chain = opt_loader.get_option_chain(ticker, expiry)
        logger.info(f"   Calls: {len(chain['calls'])} options")
        logger.info(f"   Puts: {len(chain['puts'])} options")
        
        if not chain['calls'].empty:
            logger.info(f"   Sample call:\n{chain['calls'].head(1)}")
        
        iv = opt_loader.get_atm_iv(ticker, expiry)
        logger.info(f"   ATM IV: {iv:.2%}")
    
    logger.info("\n=== All tests completed successfully ===")

if __name__ == "__main__":
    test_aapl()
