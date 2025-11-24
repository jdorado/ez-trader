# 🚀 The 100x Initiative: $10k to $1M

**An Open-Source Quantitative Trading Experiment.**
**Built by AI. Executed by Humans.**

---

## 🎯 The Objective
To grow a **$10,000** starting portfolio into **$1,000,000** within **12 months**.
*   **Implied Return**: ~47% Month-over-Month.
*   **Instrument**: Weekly Options (High Gamma, Defined Risk).
*   **Status**: **LIVE** (Started Nov 20, 2025).

---

## 🧠 The Framework

We do not "invest." We hunt volatility.
Our system is built on a strict quantitative framework designed to survive market crashes and exploit explosive moves.

### 1. Philosophy: "Survive the Macro, Hunt the Micro"
*   **Macro**: We respect the weather. If VIX is high and Rates are spiking, we sit in cash or short the market.
*   **Micro**: We scan the **Nasdaq 100** and **High-Beta** tickers for idiosyncratic volatility breakouts.

### 2. The Strategy: Volatility Breakout
*   **Signal**: Z-Score Breakouts (> 1.5 Std Dev) on Price & Volatility.
*   **Vehicle**: **Weekly ATM Options** (1-2 weeks to expiry).
*   **Edge**: Catching the "Fat Tail" moves that standard distribution models underestimate.

### 3. Risk Management (The Engine)
*   **Kelly Criterion**: Position sizing is mathematically optimized based on win probability and edge.
*   **Hard Cap**: Max **10%** risk per trade. No "YOLO" bets.
*   **Daily Limit**: Maximum **3 tickers** per day to maintain focus and avoid over-diversification.
*   **Regime Filter**:
    *   🟢 **Bullish**: Full Size Longs.
    *   🔴 **Bearish**: Cash or Puts Only.
    *   🛡 **Safety**: Automatic blocks on tickers with recent Splits or upcoming Earnings.

### 4. The "PhD Panel" Review
*   **Rigorous Defense**: Every trade signal generates a detailed **Technical Memo**.
*   **The Panel**: An expert review board (Human + AI) critiques the thesis, Greeks, and risk profile.
*   **Execution**: Only trades that survive this scrutiny are executed.

---

## 🛠 Tech Stack

*   **Core**: Python 3.13
*   **Infrastructure**: Docker & Docker Compose
*   **Data**: `yfinance` (Market Data), `redis` (Caching)
*   **Parallelization**: `concurrent.futures` (Scanning 100+ tickers in < 20s)
*   **Safety**: Custom `CorporateActionChecker` to prevent data artifacts.

---

## 📢 Build in Public

We are documenting every step, every trade, and every line of code.

*   **Daily Diary**: Check the `diary/` folder for daily thoughts and trade logs.
*   **Twitter**: Follow the journey (Link TBD).

---

## ⚠️ Disclaimer
*This is an engineering experiment, not financial advice. Options trading involves significant risk and you can lose your entire investment. Do not copy these trades.*
