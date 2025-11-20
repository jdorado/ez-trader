import logging
import sys
from datetime import datetime

class TradingLogger:
    """Custom logger for the trading system."""
    
    def __init__(self, name: str = "TradingBot", log_file: str = "trading.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # File Handler
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def warning(self, message: str):
        self.logger.warning(message)


    def tweet(self, message: str):
        """
        Format a message as a tweet and log it.
        In a real system, this would connect to Twitter API.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tweet_content = f"[{timestamp}] 🐦 TWEET: {message}"
        if len(message) > 280:
            self.logger.warning(f"Tweet exceeds 280 chars: {len(message)}")
        
        print("\n" + "="*40)
        print(tweet_content)
        print("="*40 + "\n")
        self.logger.info(f"TWEET GENERATED: {message}")

# Global instance
logger = TradingLogger()
