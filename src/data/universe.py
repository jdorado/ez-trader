from typing import List

class UniverseLoader:
    """
    Manages lists of tickers for scanning.
    """
    
    @staticmethod
    def get_high_beta_tickers() -> List[str]:
        """
        Returns a manually curated list of high-beta / volatile tickers.
        Includes lower-priced names for smaller accounts (MARA, CLSK, SOFI, etc).
        """
        return [
            "NVDA", "TSLA", "AMD", "COIN", "MSTR", # High Price
            "MARA", "PLTR", "NET", "ROKU", "SQ", "SHOP", "AFRM", "UPST", # Mid Price
            "CLSK", "RIOT", "SOFI", "HOOD", "DKNG", "OPEN", # Low Price (<$20)
            # --- Phase 2 Expansion ---
            "BITF", "HIVE", "HUT", "IBIT", # Crypto Proxies
            "XBI", "SMH", "ARKK", # Volatile ETFs
            "CVNA", "GME", "AMC", # High Short Interest / Meme
            "BABA", "PDD", "JD" # China Tech
        ]

    @staticmethod
    def get_nasdaq_100() -> List[str]:
        """
        Returns top Nasdaq 100 tickers (Top 20 for now to save API calls/time during dev).
        TODO: Fetch dynamically or expand list.
        """
        return [
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "COST", "PEP",
            "CSCO", "TMUS", "CMCSA", "INTC", "AMD", "NFLX", "QCOM", "TXN", "HON", "AMGN"
        ]
        
    @staticmethod
    def get_systematic_universe() -> List[str]:
        """
        Returns tickers from the latest systematic scan report.
        """
        import pandas as pd
        import os
        
        # Path relative to project root (assuming this runs from root or src)
        # We'll try a few common paths to be robust
        paths = [
            "reports/systematic_universe.csv",
            "../reports/systematic_universe.csv",
            "/Users/jdorado/dev/ez-stocks/reports/systematic_universe.csv"
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    if 'Ticker' in df.columns:
                        return df['Ticker'].tolist()
                except Exception as e:
                    print(f"Error reading systematic universe from {path}: {e}")
        
        return []

    @staticmethod
    def get_combined_universe() -> List[str]:
        """
        Returns unique tickers from all lists.
        """
        tickers = set(
            UniverseLoader.get_high_beta_tickers() + 
            UniverseLoader.get_nasdaq_100() +
            UniverseLoader.get_systematic_universe()
        )
        return list(tickers)
