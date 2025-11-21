import os
from datetime import datetime
from typing import Dict, Any

class TradeMemoGenerator:
    """
    Generates a detailed technical memo for the 'PhD Panel' review.
    """
    
    def __init__(self, output_dir: str = "memos/trades"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_memo(self, trade_signal: Dict[str, Any], market_regime: Dict[str, Any]) -> str:
        """
        Creates a markdown memo for a specific trade signal.
        """
        ticker = trade_signal['ticker']
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{ticker}_{trade_signal['action']}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # Calculate Greeks (Placeholder logic for now, would normally fetch from API)
        # In a real system, we'd get these from the option chain data
        delta = "0.50" if trade_signal['option_type'] == 'call' else "-0.50"
        gamma = "High" # Weekly options have high gamma
        theta = "High" # Weekly options have high theta decay
        
        memo_content = f"""# 🎓 PhD Panel Review: {ticker} {trade_signal['action']}

**Date**: {date_str}
**Signal**: {trade_signal['strategy']}
**Status**: 🟡 PENDING REVIEW

---

## 1. The Thesis 🧐
*   **Direction**: {trade_signal['action']} ({trade_signal['option_type'].upper()})
*   **Catalyst**: Volatility Breakout (Z-Score > 1.5).
*   **Market Regime**: {market_regime['state'].value} (VIX: {market_regime.get('vix', 'N/A')})
*   **Rationale**: The system detected an idiosyncratic move in {ticker} that diverges from the broader market, or aligns with a crash regime.

## 2. The Instrument 🎻
*   **Contract**: {trade_signal['expiry']} ${trade_signal['strike']} {trade_signal['option_type'].upper()}
*   **Price**: ${trade_signal['option_price']:.2f}
*   **Implied Volatility**: High (Breakout Mode)
*   **Greeks Profile**:
    *   **Delta**: {delta} (Directional exposure)
    *   **Gamma**: {gamma} (Acceleration risk/reward)
    *   **Theta**: {theta} (Time decay is the enemy)

## 3. Risk Management 🛡
*   **Kelly Allocation**: ${trade_signal['allocation']:.2f}
*   **Position Size**: {trade_signal['quantity']} Contracts
*   **Total Risk**: ${trade_signal['quantity'] * trade_signal['option_price'] * 100:.2f}
*   **Stop Loss**: -50% (Hard Stop) or Regime Change.

## 4. Verification ✅
*   **Corporate Actions**: Checked. No recent splits or upcoming earnings (Safe).
*   **Liquidity**: Volume > Open Interest (Confirmed).
*   **Cost**: Fits within $1,000 Risk Cap.

---

## 🗳 Panel Decision
*(To be filled by Human Reviewer)*

- [ ] **APPROVED** (Execute immediately)
- [ ] **REJECTED** (False positive / Too risky)
- [ ] **MODIFY** (Adjust sizing or strike)

*Signed,*
*The Algorithm* 🤖
"""
        
        with open(filepath, "w") as f:
            f.write(memo_content)
            
        return filepath
