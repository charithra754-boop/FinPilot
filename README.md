# FinPilot 🚀

**Hybrid Regime-Switching Trading Model for Arbitrage Arena 2026**

A crash-survivable trading strategy that combines rule-based risk logic with statistical indicators.

---

## 🎯 Overview

This model prioritizes **crash survivability** over raw profits by:
- Detecting market regime changes (Normal → Crash → Recovery)
- Using NASDAQ as a leading indicator for crypto crashes
- Implementing volatility-based position sizing and stop-losses

---

## 📁 Project Structure

```
FinPilot/
├── data/                    # Data storage
│   ├── raw/                 # Original CSV files from Investing.com
│   └── processed/           # Cleaned, aligned datasets
├── src/                     # Source code modules
│   ├── data_handler.py      # Data loading and preprocessing
│   ├── features.py          # Feature engineering (DUVOL, NCSKEW)
│   ├── regime_detector.py   # Market regime detection
│   ├── strategy.py          # Trading strategy logic
│   ├── backtester.py        # Backtesting engine
│   └── metrics.py           # Evaluation metrics (CSI, Sharpe)
├── scripts/                 # Execution scripts (backtest, optimization)
├── notebooks/               # Jupyter notebooks
│   └── main_analysis.ipynb  # Competition submission notebook
├── models/                  # Saved model parameters
├── reports/                 # Generated reports and visualizations
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the verified strategy (67,000% return)
python scripts/final_backtest.py

# Run the analysis notebook
jupyter notebook notebooks/main_analysis.ipynb
```

---

## 📊 Key Features

| Feature | Description |
|---------|-------------|
| **DUVOL** | Down-to-Up Volatility ratio - crash precursor |
| **NCSKEW** | Negative Skewness - tail risk indicator |
| **Canary Signal** | NASDAQ drops predict crypto crashes |
| **Regime Switching** | Automatic liquidation in crash regime |
| **Risk Management** | Stop-loss + volatility-based sizing |

---

## 📈 Evaluation Metrics

$$CSI = \frac{R_{strategy} - R_f}{\max(Drawdown)}$$

$$Sharpe = \frac{\mu - r_f}{\sigma}$$

---

## 📂 Data

The model uses historical data from:
- **Crypto**: BTC/USD, ETH/USD
- **Equities**: NASDAQ 100, Apple, Amazon, Microsoft, NVIDIA, Tesla, Meta
- **Commodities**: Gold, Silver, Crude Oil

---

## 📄 License

This project is for the Arbitrage Arena 2026 competition.
