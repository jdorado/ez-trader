# 📋 Trading Memo: 2025-11-24
## Market Regime: NEUTRAL (VIX: 21.12)

---

## Trade 1: AAPL (Apple Inc.)
**Status**: ✅ EXECUTED

### Structure
* **Type**: Bull Call Spread (Debit Spread)
* **Legs**: 
    - BUY $275 CALL
    - SELL $280 CALL
* **Expiry**: 2025-11-28 (4 DTE)
* **Size**: 2 Spreads
* **Entry Price**: $1.97 (Net Debit)
* **Total Cost**: $394.00

### Thesis
Volatility breakout (Z-Score > 1.5) with fair IV/HV ratio (1.02). Spread structure mitigates Vega risk in elevated VIX environment.

### Risk Management
* **Max Loss**: $394.00 (premium paid)
* **Max Gain**: $606.00 (at $280 or above)
* **Breakeven**: $276.97
* **Stop**: -30% or regime change

---

## Trade 2: AA (Alcoa Corp)
**Status**: ✅ EXECUTED

### Structure
* **Type**: Bull Call Spread (Debit Spread)
* **Legs**:
    - BUY $38.5 CALL
    - SELL $40.0 CALL
* **Expiry**: 2025-11-28 (4 DTE)
* **Size**: 7 Spreads
* **Entry Price**: $0.55 (Net Debit)
* **Total Cost**: $385.00

### Thesis
Sector-wide breakout validated by Aluminum futures surge (+3%). However, OTM structure requires spread to mitigate Theta decay in volatile regime.

### Risk Management
* **Max Loss**: ~$315.00 (premium paid)
* **Max Gain**: ~$735.00 (at $40 or above)
* **Breakeven**: ~$38.95
* **Stop**: Cut if AA stock drops below $37.00

### Execution Notes
1. **Limit Order**: Mid-price if Bid/Ask > $0.05
2. **Wait for VWAP pullback** on 15-min chart
3. **Exit**: Take 50% profit at option price $1.10

---

## Trade 3: COIN (Coinbase)
**Status**: ✅ EXECUTED

### Structure
* **Type**: Bull Call Spread (Debit Spread)
* **Legs**:
    - BUY $250 CALL
    - SELL $257.5 CALL
* **Expiry**: 2025-11-28 (4 DTE)
* **Size**: 1 Spread
* **Entry Price**: $3.60 (Net Debit)
* **Total Cost**: $360.00

### Thesis
COIN staging relief rally (+4.6% to ~$251.50) despite Bitcoin weakness. However, buying OTM naked call while BTC is down 20%+ is high risk. Spread structure captures bounce without overpaying for volatility.

### Risk Management
* **Max Loss**: ~$380.00 (premium paid)
* **Max Gain**: ~$370.00 (at $257.50 or above)
* **Breakeven**: ~$254.00
* **Stop**: Close if COIN drops below $248

### Execution Notes
1. **BTC Check**: **ABORT if BTC futures are red**. Only proceed if BTC is flat/green.
2. **Limit Order**: Max $3.80 debit. Do not pay more than $4.00.
3. **Exit**: Take profit at COIN $260. Stop if breaks below $248.

---

## Portfolio Summary
| Ticker | Type | Entry | Size | Cost | Status |
|--------|------|-------|------|------|--------|
| AAPL | Spread 275/280 | $1.97 | 2 | $394 | ✅ Filled |
| AA | Spread 38.5/40 | $0.55 | 7 | $385 | ✅ Filled |
| COIN | Spread 250/257.5 | $3.60 | 1 | $360 | ✅ Filled |

**Total Allocated**: $1,139.00
