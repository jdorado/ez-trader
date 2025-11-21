# 🧐 PhD Review: CVNA Trade Evaluation

**To:** Investment Committee
**From:** Quantitative Risk Desk (PhD)
**Date:** 2025-11-21
**Subject:** EVIDENCE-BASED REVIEW of Trade Memo `2025-11-21_CVNA_SELL`

---

## 🚫 Verdict: REJECTED (Data Mismatch)

**Reason:** Signal Verification Failed.

## 📊 Evidence & Data Verification

I ran an independent verification script (`scripts/verify_cvna.py`) to validate the mathematical claims in your memo.

### 1. The "Z-Score" Claim
*   **Memo Claim:** "Volatility Breakout (Z-Score > 1.5)"
*   **Actual Data (Verified):**
    *   **Current Return:** -5.00%
    *   **20-Day Volatility:** 5.02%
    *   **Calculated Z-Score:** **-0.9337**
*   **Conclusion:** The move is less than 1 standard deviation from the mean. This is **noise**, not a breakout.
*   **Status:** ❌ **FALSE**

### 2. Systematic Integrity
*   Since the Z-Score is -0.93, the `VolatilityStrategy` (which requires > 1.5 or > 2.0) **did not** generate this signal.
*   Like the MSTR trade, this appears to be a **manual discretionary trade** dressed up as a quantitative signal.
*   There are no execution logs in `logs/` to prove otherwise.

---

## 📉 Constructive Feedback

**"In God we trust. All others must bring data."**

1.  **Stop Hallucinating Signals:** You cannot claim a "Volatility Breakout" when the Z-Score is < 1.0. That is mathematically incorrect.
2.  **Respect the Math:** If you want to trade CVNA because you "feel" it will drop, label it **"Discretionary / Manual"**. Do not pollute the quantitative system's track record with non-systematic trades.
3.  **System Check:** Your system is working correctly by *not* flagging this. It is filtering out noise. You are trying to override the filter.

**Recommendation:**
**DO NOT EXECUTE.** This trade has no statistical edge based on your own defined parameters.
