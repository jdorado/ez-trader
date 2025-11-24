import pandas as pd
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.yfinance_loader import YahooFinanceLoader
from src.data.options_loader import OptionsLoader

PORTFOLIO_FILE = "data/portfolio/trades.csv"

def track_portfolio():
    print("--- 📊 Portfolio Tracker ---")
    
    if not os.path.exists(PORTFOLIO_FILE):
        print("No portfolio file found.")
        return

    df = pd.read_csv(PORTFOLIO_FILE)
    if df.empty:
        print("Portfolio is empty.")
        return

    loader = YahooFinanceLoader()
    opt_loader = OptionsLoader()
    
    total_pnl = 0.0
    total_cost = 0.0
    total_value = 0.0
    
    print(f"{'TICKER':<6} {'TYPE':<12} {'STRIKE':<10} {'EXPIRY':<10} {'QTY':<4} {'ENTRY':<8} {'CURR':<8} {'P&L $':<10} {'P&L %':<8}")
    print("-" * 90)
    
    for _, row in df.iterrows():
        ticker = row['Ticker']
        trade_type = row['Type']
        strike = str(row['Strike'])
        expiry = row['Expiry']
        qty = row['Quantity']
        entry_price = row['Price']
        cost = row['Cost']
        
        # Estimate Current Option Price
        current_option_price = entry_price # Default to entry if fetch fails
        
        try:
            # Fetch Option Chain
            chain = opt_loader.get_option_chain(ticker, expiry)
            
            if 'SPREAD' in trade_type:
                # Handle Spread (e.g., 275/280)
                legs = strike.split('/')
                strike_long = float(legs[0])
                strike_short = float(legs[1])
                
                # Determine Option Type for Legs
                is_call = 'CALL' in trade_type
                options = chain['calls'] if is_call else chain['puts']
                
                if not options.empty:
                    long_opt = options[options['strike'] == strike_long]
                    short_opt = options[options['strike'] == strike_short]
                    
                    price_long = long_opt['lastPrice'].values[0] if not long_opt.empty else 0.0
                    price_short = short_opt['lastPrice'].values[0] if not short_opt.empty else 0.0
                    
                    # Debit Spread Value = Long - Short
                    current_option_price = price_long - price_short
                
            else:
                # Single Leg
                strike_val = float(strike)
                is_call = 'CALL' in trade_type
                options = chain['calls'] if is_call else chain['puts']
                
                if not options.empty:
                    opt = options[options['strike'] == strike_val]
                    if not opt.empty:
                        current_option_price = opt['lastPrice'].values[0]
                
        except Exception as e:
            print(f"Warning: Could not fetch price for {ticker} {strike}: {e}")
            
        # Calculate Value
        current_value = current_option_price * qty * 100
        pnl = current_value - cost
        pnl_pct = (pnl / cost) * 100 if cost > 0 else 0.0
        
        total_cost += cost
        total_value += current_value
        total_pnl += pnl
        
        pnl_str = f"${pnl:,.2f}"
        
        print(f"{ticker:<6} {trade_type:<12} {strike:<10} {expiry:<10} {qty:<4} ${entry_price:<7.2f} ${current_option_price:<7.2f} {pnl_str:<10} {pnl_pct:>7.2f}%")

    print("-" * 90)
    print(f"Total Cost:  ${total_cost:,.2f}")
    print(f"Total Value: ${total_value:,.2f}")
    print(f"Total P&L:   ${total_pnl:,.2f} ({(total_pnl/total_cost)*100:.2f}%)")

if __name__ == "__main__":
    track_portfolio()
