---
description: Daily Trading Routine (Macro -> Scan -> Diary -> Execution)
---

# 🔄 Daily Trading Cycle

Follow this checklist every trading day to ensure systematic execution and macro awareness.

## 1. 🌍 Macro & Context
- [ ] **Run Macro Scan**: `python scripts/run_macro_scan.py`
    - Check for **OPEX** (Monthly/Weekly).
    - Check **VIX** (>20 is Volatile).
    - Check **Rates** (TNX).
- [ ] **Check Calendar**: Are there major earnings (NVDA, TSLA) or Fed events today?

## 2. ☀️ Morning Brief
- [ ] **Run Brief**: `python scripts/run_daily.py`
    - Review overnight moves and general market sentiment.

## 3. 🔎 Market Scan
- [ ] **Run Aggressive Scan**: `python scripts/run_aggressive.py`
    - **Note**: If OPEX day, ensure `min_days=2` to avoid 0DTE risk.
    - **Review Memos**: Check `memos/trades/` for new signals.

## 4. 📔 Diary Update
- [ ] **Create/Update Entry**: `diary/YYYY-MM-DD.md`
    - **Format**:
        - **Theme**: One-line summary of the day.
        - **Macro**: Risk Level & Key Drivers.
        - **Signals**: List of generated memos.
        - **Plan**: Explicit "Execution Instructions" table (Ticker, Strike, Price).

## 5. 👮‍♂️ PhD Panel Review
- [ ] **Verify Signals**: Run `python scripts/final_verification.py` (if needed).
- [ ] **Notify User**: Present the Diary and Memos for approval.

## 6. 🚀 Execution (Human-in-the-Loop)
- [ ] **Wait for Confirmation**: Do NOT execute until user says "Executed".
- [ ] **Archive**:
    - Run `python scripts/approve_trades.py` to mark memos as APPROVED.
    - Move memos to `memos/archive/`.
    - Log trades to `data/portfolio/trades.csv` (if automated logging is desired, otherwise Manual).

## 7. 🌙 End of Day
- [ ] **Review P&L**: Update portfolio tracking.
- [ ] **Prepare for Tomorrow**: Note any overnight watches.
