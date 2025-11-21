import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.macro import MacroContext
from src.utils.logger import logger

def run_macro_scan():
    logger.info("--- 🌍 Running Macro Context Scan ---")
    
    macro = MacroContext()
    context = macro.get_context()
    
    print("\n" + "="*40)
    print(f"📅 DATE: {context['date']}")
    print(f"⚠️ RISK LEVEL: {context['risk_level']}")
    print("-" * 40)
    
    print(f"🔹 Monthly OPEX: {'YES 💥' if context['is_opex'] else 'No'}")
    print(f"🔹 VIX Index:    {context['vix']:.2f}")
    print(f"🔹 10Y Yield:    {context['rates_10y']:.2f}%")
    print(f"🔹 DXY (Dollar): {context['dxy']:.2f}")
    
    print("="*40 + "\n")
    
    if context['is_opex']:
        logger.warning("Today is Monthly OPEX! Expect high volatility and gamma pinning.")
        logger.warning("Recommendation: Avoid holding 0DTE options through close.")

if __name__ == "__main__":
    run_macro_scan()
