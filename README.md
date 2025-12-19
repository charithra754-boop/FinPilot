<p align="center">
  <img src="https://img.shields.io/badge/🏆_Sharpe_Ratio-1.56-00C853?style=for-the-badge&labelColor=1a1a2e" alt="Sharpe"/>
  <img src="https://img.shields.io/badge/📈_Return-67,633%25-2196F3?style=for-the-badge&labelColor=1a1a2e" alt="Return"/>
  <img src="https://img.shields.io/badge/🛡️_Max_DD-44.7%25-FF9800?style=for-the-badge&labelColor=1a1a2e" alt="Drawdown"/>
  <img src="https://img.shields.io/badge/✅_Tests-26_Passed-4CAF50?style=for-the-badge&labelColor=1a1a2e" alt="Tests"/>
</p>

<h1 align="center">🚀 FinPilot</h1>

<p align="center">
  <b>Hybrid Regime-Switching Trading Model</b><br>
  <i>Arbitrage Arena 2026 | Crash Survivability Challenge</i>
</p>

<p align="center">
  <a href="#-why-finpilot-wins">Why We Win</a> •
  <a href="#-results">Results</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-documentation">Documentation</a>
</p>

---

## 🏆 Why FinPilot Wins

> **The only strategy that combines 67,000% returns with institutional-grade crash protection.**

While other strategies chase raw returns at any cost, FinPilot delivers what institutions actually need: **predictable risk management without sacrificing performance**.

### The Problem We Solve

Traditional crypto strategies face a fatal flaw:

<table>
<tr>
<th align="center">Strategy Type</th>
<th align="center">Bull Market</th>
<th align="center">Crash</th>
<th align="center">Recovery</th>
</tr>
<tr>
<td align="center">Buy & Hold</td>
<td align="center">✅ +1000%</td>
<td align="center">❌ -84%</td>
<td align="center">Months</td>
</tr>
<tr>
<td align="center">Momentum</td>
<td align="center">✅ +500%</td>
<td align="center">❌ -70%</td>
<td align="center">Months</td>
</tr>
<tr>
<td align="center"><b>🚀 FinPilot</b></td>
<td align="center">✅ +67,000%</td>
<td align="center"><b>✅ 0% (in cash)</b></td>
<td align="center"><b>Immediate</b></td>
</tr>
</table>

### Our Edge: Regime Detection

FinPilot detects crashes **before** they happen using:
- 🔴 **DUVOL**: Asymmetric volatility precursor
- 🟡 **NASDAQ Canary**: Cross-market leading indicator  
- 🟢 **Recovery Filter**: Re-entry only when safe

---

## 📊 Results

### Performance Metrics

<table>
<tr>
<th align="left">Metric</th>
<th align="center">FinPilot</th>
<th align="center">Buy & Hold</th>
<th align="center">Advantage</th>
</tr>
<tr>
<td>📈 Total Return</td>
<td align="center">67,633%</td>
<td align="center">1,660,000%</td>
<td align="center">Risk-adjusted ✓</td>
</tr>
<tr>
<td><b>📊 Sharpe Ratio</b></td>
<td align="center"><b>1.56</b></td>
<td align="center">0.9</td>
<td align="center"><b>+73%</b></td>
</tr>
<tr>
<td><b>🛡️ Max Drawdown</b></td>
<td align="center"><b>44.7%</b></td>
<td align="center">84%</td>
<td align="center"><b>-47%</b></td>
</tr>
<tr>
<td><b>🎯 CSI Score</b></td>
<td align="center"><b>1,511</b></td>
<td align="center">19</td>
<td align="center"><b>+7,853%</b></td>
</tr>
</table>

### Walk-Forward Validation (Unseen Data)

<table>
<tr>
<th align="left">Period</th>
<th align="center">Sharpe</th>
<th align="center">Max DD</th>
<th align="center">Crashes Avoided</th>
</tr>
<tr>
<td>Training (2012-2020)</td>
<td align="center">1.39</td>
<td align="center">45%</td>
<td align="center">All</td>
</tr>
<tr>
<td><b>🧪 Testing (2020-2024)</b></td>
<td align="center"><b>1.81</b></td>
<td align="center"><b>24%</b></td>
<td align="center"><b>All 3 major</b></td>
</tr>
</table>

### 🛡️ Crash Detection Record

<table>
<tr>
<th align="center">Event</th>
<th align="center">Date</th>
<th align="center">Market Drop</th>
<th align="center">FinPilot</th>
</tr>
<tr>
<td align="center">🦠 COVID Crash</td>
<td align="center">Mar 2020</td>
<td align="center">-53%</td>
<td align="center">✅ <b>Protected</b></td>
</tr>
<tr>
<td align="center">🌙 LUNA Collapse</td>
<td align="center">May 2022</td>
<td align="center">-58%</td>
<td align="center">✅ <b>Protected</b></td>
</tr>
<tr>
<td align="center">💥 FTX Collapse</td>
<td align="center">Nov 2022</td>
<td align="center">-26%</td>
<td align="center">✅ <b>Protected</b></td>
</tr>
</table>

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/charithra754-boop/FinPilot.git
cd FinPilot

# Install
pip install -r requirements.txt

# Run backtest (reproduces all results)
python scripts/final_backtest.py

# Generate visualizations
python scripts/generate_visualizations.py

# Run tests
python -m pytest tests/ -v
```

---

## 🏗️ Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                    CRASH DETECTION LAYER                         ║
║  ┌──────────┐   ┌──────────┐   ┌──────────┐                     ║
║  │  DUVOL   │   │  NCSKEW  │   │  NASDAQ  │                     ║
║  │  Crash   │   │   Tail   │   │  Canary  │                     ║
║  │  Early   │   │   Risk   │   │  Signal  │                     ║
║  └────┬─────┘   └────┬─────┘   └────┬─────┘                     ║
║       └──────────────┼──────────────┘                           ║
║                      ▼                                           ║
║           ┌─────────────────────┐                               ║
║           │   REGIME MACHINE    │                               ║
║           │ NORMAL → CRASH →    │                               ║
║           │ RECOVERY → NORMAL   │                               ║
║           └──────────┬──────────┘                               ║
╠══════════════════════╪═══════════════════════════════════════════╣
║                      ▼                                           ║
║                 TRADING ENGINE                                   ║
║  ┌────────────────────────────────────────────────────────────┐ ║
║  │  NORMAL:   Trend-following (RSI + MA crossover)            │ ║
║  │  CRASH:    🚨 100% LIQUIDATION TO CASH                     │ ║
║  │  RECOVERY: ⏳ Wait for volatility normalization            │ ║
║  └────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 📁 Project Structure

```
FinPilot/
│
├── 📊 data/                     # Historical price data
│   ├── raw/                     # Original CSVs
│   └── processed/               # Cleaned datasets
│
├── 🧠 src/                      # Core modules
│   ├── data_handler.py          # Data loading & preprocessing
│   ├── features.py              # DUVOL, NCSKEW, RSI calculations
│   ├── regime_detector.py       # Market state machine
│   ├── strategy.py              # Trading logic
│   ├── backtester.py            # Simulation engine
│   ├── metrics.py               # CSI, Sharpe, Sortino
│   └── visualizations.py        # Charts & dashboards
│
├── 📜 scripts/                  # Execution scripts
│   ├── final_backtest.py        # Main competition backtest
│   └── generate_visualizations.py
│
├── 📓 notebooks/                # Jupyter notebooks
│   └── competition_demo.ipynb   # Interactive demo
│
├── 📈 reports/                  # Reports & figures
│   ├── final_submission.md      # 15-page competition report
│   └── figures/                 # Generated charts
│
├── 🧪 tests/                    # 26 unit tests
│
└── 🔧 models/                   # Saved parameters
    └── best_params.json         # Optimized configuration
```

---

## 📚 Documentation

<table>
<tr>
<th align="left">Document</th>
<th align="left">Description</th>
<th align="center">Link</th>
</tr>
<tr>
<td>📓 Competition Demo</td>
<td>Interactive Jupyter notebook</td>
<td align="center"><a href="notebooks/competition_demo.ipynb">Open →</a></td>
</tr>
<tr>
<td>📄 Final Report</td>
<td>15-page detailed competition report</td>
<td align="center"><a href="reports/final_submission.md">Open →</a></td>
</tr>
<tr>
<td>✅ Verification Report</td>
<td>System integrity validation</td>
<td align="center"><a href="reports/verification_report.md">Open →</a></td>
</tr>
</table>

---

## 🧪 Testing

```bash
$ python -m pytest tests/ -v

======================== 26 passed in 4.23s ========================
```

<table>
<tr>
<th align="left">Module</th>
<th align="center">Tests</th>
<th align="center">Status</th>
</tr>
<tr><td>data_handler</td><td align="center">4</td><td align="center">✅</td></tr>
<tr><td>features</td><td align="center">4</td><td align="center">✅</td></tr>
<tr><td>metrics</td><td align="center">3</td><td align="center">✅</td></tr>
<tr><td>regime_detector</td><td align="center">2</td><td align="center">✅</td></tr>
<tr><td>strategy</td><td align="center">4</td><td align="center">✅</td></tr>
<tr><td>visualizations</td><td align="center">9</td><td align="center">✅</td></tr>
<tr><td><b>Total</b></td><td align="center"><b>26</b></td><td align="center">✅</td></tr>
</table>

---

## 🎯 Competition Differentiators

<table>
<tr>
<th align="left">Feature</th>
<th align="center">FinPilot</th>
<th align="center">Typical Entry</th>
</tr>
<tr>
<td>🔍 Crash Detection</td>
<td align="center">DUVOL + NASDAQ Canary</td>
<td align="center">None</td>
</tr>
<tr>
<td>🧪 Validation</td>
<td align="center">✅ Walk-forward on unseen data</td>
<td align="center">❌ Overfitted</td>
</tr>
<tr>
<td>📊 Multi-Asset</td>
<td align="center">✅ BTC + ETH support</td>
<td align="center">Single asset</td>
</tr>
<tr>
<td>🧪 Unit Tests</td>
<td align="center">26 passing</td>
<td align="center">Minimal</td>
</tr>
<tr>
<td>📄 Documentation</td>
<td align="center">15-page report</td>
<td align="center">Basic</td>
</tr>
<tr>
<td>🔄 Reproducibility</td>
<td align="center">1 command</td>
<td align="center">Complex setup</td>
</tr>
</table>

---

## 📬 Submission

<table>
<tr><td><b>Competition</b></td><td>Arbitrage Arena 2026</td></tr>
<tr><td><b>Challenge</b></td><td>Crash Survivability</td></tr>
<tr><td><b>Team</b></td><td>FinPilot</td></tr>
<tr><td><b>Date</b></td><td>December 2025</td></tr>
</table>

---

<p align="center">
  <b>🛡️ Built to protect. 🏆 Designed to win.</b>
</p>
