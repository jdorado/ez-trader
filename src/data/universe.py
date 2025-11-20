from typing import List

class UniverseLoader:
    """
    Manages lists of tickers for scanning.
    """
    
    @staticmethod
    def get_high_beta_tickers() -> List[str]:
        """
        Returns a manually curated list of high-beta / volatile tickers.
        """
        return ["NVDA", "TSLA", "AMD", "COIN", "MSTR", "MARA", "PLTR", "NET", "ROKU", "SQ", "SHOP", "AFRM", "UPST"]

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
    def get_combined_universe() -> List[str]:
        """
        Returns unique tickers from all lists.
        """
        tickers = set(UniverseLoader.get_high_beta_tickers() + UniverseLoader.get_nasdaq_100())
        return list(tickers)
