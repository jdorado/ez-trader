import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import concurrent.futures
from src.data.yfinance_loader import YahooFinanceLoader
from src.data.options_loader import OptionsLoader
from src.core.market_regime import MarketRegime
from src.core.mongo_cache import MongoCache


# Module-level function for ProcessPoolExecutor (must be picklable)
def _fetch_ticker_data_isolated(args: tuple) -> Optional[Dict[str, Any]]:
    """
    Fetch ticker data in an isolated process.
    Args is a tuple of (ticker, use_cache, cache_params)
    """
    ticker, use_cache = args
    
    # Check cache first
    if use_cache:
        try:
            cache = MongoCache()
            cached = cache.get(ticker)
            if cached:
                return cached
        except:
            pass
    
    # Create fresh instances in this process
    loader = YahooFinanceLoader()
    opt_loader = OptionsLoader()
    
    try:
        # 1. Price Data
        data = loader.get_historical_data(ticker, start_date="2024-01-01")
        if data.empty:
            return None
        
        close_prices = data['Close']
        if isinstance(close_prices, pd.DataFrame):
            close_prices = close_prices.iloc[:, 0]
        
        current_price = float(close_prices.iloc[-1])
        
        # 2. Volume
        volume = int(data['Volume'].iloc[-1]) if 'Volume' in data.columns else 0
        
        # 3. Returns and Volatility
        returns = close_prices.pct_change().dropna()
        rolling_std = returns.rolling(window=20).std().iloc[-1]
        rolling_mean = returns.rolling(window=20).mean().iloc[-1]
        current_return = returns.iloc[-1]
        
        # Ensure float
        if isinstance(rolling_std, pd.Series):
            rolling_std = float(rolling_std.iloc[0])
        else:
            rolling_std = float(rolling_std)
            
        if isinstance(rolling_mean, pd.Series):
            rolling_mean = float(rolling_mean.iloc[0])
        else:
            rolling_mean = float(rolling_mean)
            
        if isinstance(current_return, pd.Series):
            current_return = float(current_return.iloc[0])
        else:
            current_return = float(current_return)
        
        # Z-Score
        z_score = (current_return - rolling_mean) / rolling_std if rolling_std > 0 else 0
        hv = rolling_std * np.sqrt(252)  # Annualized
        
        # 4. Options Data
        expiry = opt_loader.get_nearest_expiration(ticker, min_days=2)
        iv = 0.0
        if expiry:
            iv = opt_loader.get_atm_iv(ticker, expiry)
        
        iv_hv_ratio = iv / hv if hv > 0 else 0
        
        # 5. Fundamentals & Greeks
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            
            beta = info.get('beta', 1.0)
            market_cap = info.get('marketCap', 0)
            pe_ratio = info.get('trailingPE') or info.get('forwardPE', 0)
            earnings_date = info.get('earningsDate')
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            fifty_two_wk_high = info.get('fiftyTwoWeekHigh', 0)
            fifty_two_wk_low = info.get('fiftyTwoWeekLow', 0)
            
            # Calculate distance from 52W high/low
            pct_from_high = ((current_price - fifty_two_wk_high) / fifty_two_wk_high * 100) if fifty_two_wk_high else 0
            pct_from_low = ((current_price - fifty_two_wk_low) / fifty_two_wk_low * 100) if fifty_two_wk_low else 0
            
        except Exception as e:
            beta = 1.0
            market_cap = 0
            pe_ratio = 0
            earnings_date = None
            sector = 'Unknown'
            industry = 'Unknown'
            fifty_two_wk_high = 0
            fifty_two_wk_low = 0
            pct_from_high = 0
            pct_from_low = 0
        
        # 6. Options Greeks & Open Interest
        greeks = {}
        open_interest = 0
        
        if expiry:
            try:
                chain = opt_loader.get_option_chain(ticker, expiry)
                calls = chain.get('calls', pd.DataFrame())
                
                if not calls.empty:
                    # Find ATM option
                    calls['abs_diff'] = abs(calls['strike'] - current_price)
                    atm = calls.sort_values('abs_diff').iloc[0]
                    
                    # Extract Greeks if available
                    greeks = {
                        'delta': round(float(atm.get('delta', 0.5)), 3) if 'delta' in atm else None,
                        'gamma': round(float(atm.get('gamma', 0)), 4) if 'gamma' in atm else None,
                        'theta': round(float(atm.get('theta', 0)), 4) if 'theta' in atm else None,
                        'vega': round(float(atm.get('vega', 0)), 4) if 'vega' in atm else None
                    }
                    
                    open_interest = int(atm.get('openInterest', 0))
            except Exception as e:
                pass  # Greeks not always available
        
        result = {
            'ticker': ticker,
            'price': round(current_price, 2),
            'volume': volume,
            'z_score': round(z_score, 3),
            'hv': round(hv, 4),
            'iv': round(iv, 4),
            'iv_hv_ratio': round(iv_hv_ratio, 2),
            'beta': round(beta, 2) if beta else 1.0,
            'next_expiry': expiry,
            # Fundamentals
            'market_cap': market_cap,
            'pe_ratio': round(pe_ratio, 2) if pe_ratio else None,
            'sector': sector,
            'industry': industry,
            '52w_high': round(fifty_two_wk_high, 2) if fifty_two_wk_high else None,
            '52w_low': round(fifty_two_wk_low, 2) if fifty_two_wk_low else None,
            'pct_from_52w_high': round(pct_from_high, 2),
            'pct_from_52w_low': round(pct_from_low, 2),
            'earnings_date': str(earnings_date) if earnings_date else None,
            # Options
            'greeks': greeks if greeks else None,
            'open_interest': open_interest
        }
        
        # Cache the result
        if use_cache:
            try:
                cache = MongoCache()
                cache.set(ticker, result)
            except:
                pass
        
        return result
        
    except Exception as e:
        print(f"Error aggregating data for {ticker}: {e}")
        return None


class DataAggregator:
    """
    Aggregates all market data into a comprehensive snapshot for AI analysis.
    Uses MongoDB caching and parallel execution for speed.
    """
    
    def __init__(self, use_cache: bool = True, max_workers: int = 10):
        self.loader = YahooFinanceLoader()
        self.opt_loader = OptionsLoader()
        self.regime_analyzer = MarketRegime()
        self.use_cache = use_cache
        self.max_workers = max_workers
        
        if self.use_cache:
            try:
                self.cache = MongoCache()
                print("✅ MongoDB cache connected")
            except Exception as e:
                print(f"⚠️ MongoDB cache unavailable: {e}")
                self.use_cache = False
        
    def generate_market_snapshot(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Generate a comprehensive market snapshot with parallel execution (Python 3.13+ GIL-free).
        """
        print(f"📊 Generating Market Snapshot for {len(tickers)} tickers...")
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'macro': self._get_macro_data(),
            'tickers': []
        }
        
        # Parallel execution using threads (GIL-free in Python 3.13+)
        print(f"🚀 Fetching data in parallel (max_workers={self.max_workers}, GIL-free threads)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ticker = {executor.submit(self._get_ticker_data, ticker): ticker for ticker in tickers}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_ticker):
                ticker_data = future.result()
                if ticker_data:
                    snapshot['tickers'].append(ticker_data)
                
                completed += 1
                if completed % 10 == 0:
                    print(f"  Progress: {completed}/{len(tickers)} tickers...")
        
        print(f"✅ Snapshot complete: {len(snapshot['tickers'])} tickers analyzed.")
        return snapshot
    
    def _get_macro_data(self) -> Dict[str, Any]:
        """Get macro market data."""
        regime = self.regime_analyzer.analyze_regime()
        
        return {
            'regime_state': regime['state'].value,
            'vix': regime.get('vix', 0),
            'spy_trend': regime.get('spy_trend', 0),
            'details': regime.get('details', ''),
            'kelly_multipliers': self.regime_analyzer.get_kelly_multipliers(regime['state'])
        }
    
    def _get_ticker_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive data for a single ticker with caching."""
        # Check cache first
        if self.use_cache:
            cached = self.cache.get(ticker)
            if cached:
                return cached
        
        # Create fresh loader instances for thread safety
        loader = YahooFinanceLoader()
        opt_loader = OptionsLoader()
        
        try:
            # 1. Price Data
            data = loader.get_historical_data(ticker, start_date="2024-01-01")
            if data.empty:
                return None
            
            close_prices = data['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]
            
            current_price = float(close_prices.iloc[-1])
            
            # 2. Volume
            volume = int(data['Volume'].iloc[-1]) if 'Volume' in data.columns else 0
            
            # 3. Returns and Volatility
            returns = close_prices.pct_change().dropna()
            rolling_std = returns.rolling(window=20).std().iloc[-1]
            rolling_mean = returns.rolling(window=20).mean().iloc[-1]
            current_return = returns.iloc[-1]
            
            # Ensure float
            if isinstance(rolling_std, pd.Series):
                rolling_std = float(rolling_std.iloc[0])
            else:
                rolling_std = float(rolling_std)
                
            if isinstance(rolling_mean, pd.Series):
                rolling_mean = float(rolling_mean.iloc[0])
            else:
                rolling_mean = float(rolling_mean)
                
            if isinstance(current_return, pd.Series):
                current_return = float(current_return.iloc[0])
            else:
                current_return = float(current_return)
            
            # Z-Score
            z_score = (current_return - rolling_mean) / rolling_std if rolling_std > 0 else 0
            hv = rolling_std * np.sqrt(252)  # Annualized
            
            # 4. Options Data
            expiry = opt_loader.get_nearest_expiration(ticker, min_days=2)
            iv = 0.0
            if expiry:
                iv = opt_loader.get_atm_iv(ticker, expiry)
            
            iv_hv_ratio = iv / hv if hv > 0 else 0
            
            # 5. Fundamentals & Greeks
            try:
                import yfinance as yf
                stock = yf.Ticker(ticker)
                info = stock.info
                
                beta = info.get('beta', 1.0)
                market_cap = info.get('marketCap', 0)
                pe_ratio = info.get('trailingPE') or info.get('forwardPE', 0)
                earnings_date = info.get('earningsDate')
                sector = info.get('sector', 'Unknown')
                industry = info.get('industry', 'Unknown')
                fifty_two_wk_high = info.get('fiftyTwoWeekHigh', 0)
                fifty_two_wk_low = info.get('fiftyTwoWeekLow', 0)
                
                # Calculate distance from 52W high/low
                pct_from_high = ((current_price - fifty_two_wk_high) / fifty_two_wk_high * 100) if fifty_two_wk_high else 0
                pct_from_low = ((current_price - fifty_two_wk_low) / fifty_two_wk_low * 100) if fifty_two_wk_low else 0
                
            except Exception as e:
                beta = 1.0
                market_cap = 0
                pe_ratio = 0
                earnings_date = None
                sector = 'Unknown'
                industry = 'Unknown'
                fifty_two_wk_high = 0
                fifty_two_wk_low = 0
                pct_from_high = 0
                pct_from_low = 0
            
            # 6. Options Greeks & Open Interest
            greeks = {}
            open_interest = 0
            
            if expiry:
                try:
                    chain = opt_loader.get_option_chain(ticker, expiry)
                    calls = chain.get('calls', pd.DataFrame())
                    
                    if not calls.empty:
                        # Find ATM option
                        calls['abs_diff'] = abs(calls['strike'] - current_price)
                        atm = calls.sort_values('abs_diff').iloc[0]
                        
                        # Extract Greeks if available
                        greeks = {
                            'delta': round(float(atm.get('delta', 0.5)), 3) if 'delta' in atm else None,
                            'gamma': round(float(atm.get('gamma', 0)), 4) if 'gamma' in atm else None,
                            'theta': round(float(atm.get('theta', 0)), 4) if 'theta' in atm else None,
                            'vega': round(float(atm.get('vega', 0)), 4) if 'vega' in atm else None
                        }
                        
                        open_interest = int(atm.get('openInterest', 0))
                except Exception as e:
                    pass  # Greeks not always available from yfinance
            
            result = {
                'ticker': ticker,
                'price': round(current_price, 2),
                'volume': volume,
                'z_score': round(z_score, 3),
                'hv': round(hv, 4),
                'iv': round(iv, 4),
                'iv_hv_ratio': round(iv_hv_ratio, 2),
                'beta': round(beta, 2) if beta else 1.0,
                'next_expiry': expiry,
                # Fundamentals
                'market_cap': market_cap,
                'pe_ratio': round(pe_ratio, 2) if pe_ratio else None,
                'sector': sector,
                'industry': industry,
                '52w_high': round(fifty_two_wk_high, 2) if fifty_two_wk_high else None,
                '52w_low': round(fifty_two_wk_low, 2) if fifty_two_wk_low else None,
                'pct_from_52w_high': round(pct_from_high, 2),
                'pct_from_52w_low': round(pct_from_low, 2),
                'earnings_date': str(earnings_date) if earnings_date else None,
                # Options
                'greeks': greeks if greeks else None,
                'open_interest': open_interest
            }
            
            # Cache the result
            if self.use_cache:
                self.cache.set(ticker, result)
            
            return result
            
        except Exception as e:
            print(f"Error aggregating data for {ticker}: {e}")
            return None
    
    def save_snapshot(self, snapshot: Dict[str, Any], filepath: str = "reports/market_snapshot.json"):
        """Save snapshot to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)
        print(f"💾 Snapshot saved to {filepath}")
