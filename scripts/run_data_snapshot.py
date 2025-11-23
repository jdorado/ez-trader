import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env
load_dotenv()

from src.data.universe import UniverseLoader
from src.core.data_aggregator import DataAggregator


def run_data_snapshot():
    """
    Generate comprehensive market snapshot for AI analysis.
    """
    print("=== 📊 Market Data Snapshot Generation ===\n")
    
    # 1. Get Universe
    print("Step 1: Loading Universe...")
    universe = UniverseLoader.get_combined_universe()
    print(f"Universe: {len(universe)} tickers\n")
    
    # 2. Generate Market Snapshot
    print("Step 2: Generating Comprehensive Market Snapshot...")
    aggregator = DataAggregator()
    snapshot = aggregator.generate_market_snapshot(universe)
    aggregator.save_snapshot(snapshot)
    
    # 3. Display Summary
    print("\n" + "="*60)
    print("📊 SNAPSHOT SUMMARY")
    print("="*60)
    
    macro = snapshot['macro']
    print(f"\n🌍 Macro Environment:")
    print(f"  - Regime: {macro['regime_state']}")
    print(f"  - VIX: {macro['vix']:.2f}")
    print(f"  - SPY Trend: {macro['spy_trend']:.2%}")
    print(f"  - Kelly Multipliers: Long={macro['kelly_multipliers']['long']}x, Short={macro['kelly_multipliers']['short']}x")
    
    # Show top candidates by Z-Score
    tickers_df = sorted(snapshot['tickers'], key=lambda x: abs(x.get('z_score', 0)), reverse=True)
    
    print(f"\n🔥 Top 10 Tickers by Z-Score (Volatility Breakouts):")
    print(f"{'Ticker':<8} {'Price':>8} {'Z-Score':>10} {'IV/HV':>8} {'Beta':>6} {'Volume':>12}")
    print("-" * 60)
    
    for ticker in tickers_df[:10]:
        print(f"{ticker['ticker']:<8} ${ticker['price']:>7.2f} {ticker['z_score']:>10.2f} {ticker['iv_hv_ratio']:>8.2f} {ticker['beta']:>6.2f} {ticker['volume']:>12,}")
    
    print("\n" + "="*60)
    print("✅ Snapshot saved to: reports/market_snapshot.json")
    print("\n💡 Next Step: Share this file with your AI assistant for analysis!")
    print("="*60)


if __name__ == "__main__":
    run_data_snapshot()
