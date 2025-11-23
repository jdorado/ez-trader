import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time


class ScreenerCriteria(Enum):
    """Available screening criteria"""
    PRICE_MIN = "price_min"
    PRICE_MAX = "price_max"
    MARKET_CAP_MIN = "market_cap_min"
    MARKET_CAP_MAX = "market_cap_max"
    VOLUME_MIN = "volume_min"
    PE_RATIO_MIN = "pe_ratio_min"
    PE_RATIO_MAX = "pe_ratio_max"
    DIVIDEND_YIELD_MIN = "dividend_yield_min"
    DIVIDEND_YIELD_MAX = "dividend_yield_max"
    FIFTY_TWO_WEEK_HIGH_MIN = "fifty_two_week_high_min"
    FIFTY_TWO_WEEK_LOW_MAX = "fifty_two_week_low_max"
    BETA_MIN = "beta_min"
    BETA_MAX = "beta_max"


@dataclass
class StockMetrics:
    """Stock metrics for screening"""
    ticker: str
    price: float
    market_cap: Optional[float]
    volume: Optional[int]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    beta: Optional[float]
    sector: Optional[str]
    industry: Optional[str]


class YahooFinanceScreener:
    """Stock screener using Yahoo Finance data"""

    def __init__(self, tickers: List[str] = None):
        self.tickers = tickers or []
        self.metrics_cache = {}

    def add_tickers(self, tickers: List[str]):
        """Add tickers to the screening universe"""
        self.tickers.extend(tickers)
        self.tickers = list(set(self.tickers))  # Remove duplicates

    def fetch_stock_metrics(self, ticker: str) -> Optional[StockMetrics]:
        """Fetch comprehensive metrics for a single ticker"""
        try:
            stock = yf.Ticker(ticker)

            # Get basic info
            info = stock.info

            # Get current price
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not price:
                # Try fast_info as fallback
                fast_info = stock.fast_info
                price = fast_info.last_price

            if not price:
                return None

            # Extract metrics
            metrics = StockMetrics(
                ticker=ticker,
                price=price,
                market_cap=info.get('marketCap'),
                volume=info.get('volume') or info.get('regularMarketVolume'),
                pe_ratio=info.get('trailingPE') or info.get('forwardPE'),
                dividend_yield=info.get('dividendYield'),
                fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
                fifty_two_week_low=info.get('fiftyTwoWeekLow'),
                beta=info.get('beta'),
                sector=info.get('sector'),
                industry=info.get('industry')
            )

            return metrics

        except Exception as e:
            print(f"Error fetching metrics for {ticker}: {e}")
            return None

    def fetch_all_metrics(self, batch_size: int = 10, delay: float = 0.1) -> Dict[str, StockMetrics]:
        """Fetch metrics for all tickers with rate limiting"""
        metrics = {}

        for i, ticker in enumerate(self.tickers):
            if i > 0 and i % batch_size == 0:
                print(f"Processed {i}/{len(self.tickers)} tickers...")
                time.sleep(delay)

            stock_metrics = self.fetch_stock_metrics(ticker)
            if stock_metrics:
                metrics[ticker] = stock_metrics
                self.metrics_cache[ticker] = stock_metrics

        print(f"Successfully fetched metrics for {len(metrics)}/{len(self.tickers)} tickers")
        return metrics

    def apply_filters(self, metrics: Dict[str, StockMetrics], filters: Dict[str, Tuple[float, float]]) -> List[StockMetrics]:
        """Apply filtering criteria to the metrics"""
        filtered_stocks = []

        for ticker, stock in metrics.items():
            include_stock = True

            for criteria, (min_val, max_val) in filters.items():
                value = self._get_metric_value(stock, criteria)

                if value is None:
                    # If we can't get the metric, exclude the stock
                    include_stock = False
                    break

                if min_val is not None and value < min_val:
                    include_stock = False
                    break

                if max_val is not None and value > max_val:
                    include_stock = False
                    break

            if include_stock:
                filtered_stocks.append(stock)

        return filtered_stocks

    def _get_metric_value(self, stock: StockMetrics, criteria: str) -> Optional[float]:
        """Get the value for a specific criteria from stock metrics"""
        mapping = {
            ScreenerCriteria.PRICE_MIN.value: stock.price,
            ScreenerCriteria.PRICE_MAX.value: stock.price,
            ScreenerCriteria.MARKET_CAP_MIN.value: stock.market_cap,
            ScreenerCriteria.MARKET_CAP_MAX.value: stock.market_cap,
            ScreenerCriteria.VOLUME_MIN.value: stock.volume,
            ScreenerCriteria.PE_RATIO_MIN.value: stock.pe_ratio,
            ScreenerCriteria.PE_RATIO_MAX.value: stock.pe_ratio,
            ScreenerCriteria.DIVIDEND_YIELD_MIN.value: stock.dividend_yield,
            ScreenerCriteria.DIVIDEND_YIELD_MAX.value: stock.dividend_yield,
            ScreenerCriteria.FIFTY_TWO_WEEK_HIGH_MIN.value: stock.fifty_two_week_high,
            ScreenerCriteria.FIFTY_TWO_WEEK_LOW_MAX.value: stock.fifty_two_week_low,
            ScreenerCriteria.BETA_MIN.value: stock.beta,
            ScreenerCriteria.BETA_MAX.value: stock.beta,
        }

        return mapping.get(criteria)

    def screen_stocks(self, filters: Dict[str, Tuple[float, float]]) -> pd.DataFrame:
        """Main screening method that fetches metrics and applies filters"""
        print(f"Screening {len(self.tickers)} tickers with filters: {filters}")

        # Fetch metrics
        metrics = self.fetch_all_metrics()

        # Apply filters
        filtered_stocks = self.apply_filters(metrics, filters)

        # Convert to DataFrame
        if filtered_stocks:
            data = []
            for stock in filtered_stocks:
                data.append({
                    'Ticker': stock.ticker,
                    'Price': stock.price,
                    'Market Cap': stock.market_cap,
                    'Volume': stock.volume,
                    'P/E Ratio': stock.pe_ratio,
                    'Dividend Yield': stock.dividend_yield,
                    '52W High': stock.fifty_two_week_high,
                    '52W Low': stock.fifty_two_week_low,
                    'Beta': stock.beta,
                    'Sector': stock.sector,
                    'Industry': stock.industry
                })

            df = pd.DataFrame(data)
            df = df.sort_values('Market Cap', ascending=False, na_position='last')
            return df
        else:
            return pd.DataFrame()

    def get_popular_filters(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Return predefined filter sets for common screening strategies"""
        return {
            'large_cap_dividend': {
                ScreenerCriteria.PRICE_MIN.value: (10, None),
                ScreenerCriteria.MARKET_CAP_MIN.value: (10e9, None),  # $10B+
                ScreenerCriteria.DIVIDEND_YIELD_MIN.value: (0.02, None),  # 2%+
            },
            'growth_stocks': {
                ScreenerCriteria.PRICE_MIN.value: (5, None),
                ScreenerCriteria.MARKET_CAP_MIN.value: (1e9, None),  # $1B+
                ScreenerCriteria.PE_RATIO_MAX.value: (None, 30),  # P/E < 30
                ScreenerCriteria.BETA_MIN.value: (1.0, None),  # Beta > 1.0
            },
            'value_stocks': {
                ScreenerCriteria.PRICE_MIN.value: (5, None),
                ScreenerCriteria.MARKET_CAP_MIN.value: (500e6, None),  # $500M+
                ScreenerCriteria.PE_RATIO_MAX.value: (None, 15),  # P/E < 15
            },
            'high_volume': {
                ScreenerCriteria.PRICE_MIN.value: (1, None),
                ScreenerCriteria.VOLUME_MIN.value: (1e6, None),  # 1M+ daily volume
            },
            'near_52w_low': {
                ScreenerCriteria.PRICE_MIN.value: (5, None),
                ScreenerCriteria.FIFTY_TWO_WEEK_LOW_MAX.value: (None, 1.05),  # Within 5% of 52W low
            }
        }
