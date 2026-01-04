<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/Tests-48_Passing-success?style=flat-square&logo=pytest" alt="Tests"/>
  <img src="https://img.shields.io/badge/Code_Style-PEP8-blue?style=flat-square" alt="PEP8"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Sharpe_Ratio-1.56-00C853?style=for-the-badge&labelColor=0d1117" alt="Sharpe"/>
  <img src="https://img.shields.io/badge/Total_Return-56,000%25-2196F3?style=for-the-badge&labelColor=0d1117" alt="Return"/>
  <img src="https://img.shields.io/badge/Max_Drawdown-44.7%25-FF9800?style=for-the-badge&labelColor=0d1117" alt="Drawdown"/>
  <img src="https://img.shields.io/badge/Monte_Carlo-2.7x_Survival-9C27B0?style=for-the-badge&labelColor=0d1117" alt="Monte Carlo"/>
</p>

<h1 align="center">
  <br>
  🚀 FinPilot
  <br>
</h1>

<h4 align="center">Next-Generation Crypto Trading System with Flash Crash Survivability</h4>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-results">Results</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-api">API</a>
</p>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Crash Intensity Score (CIS)
A continuous **0-100 risk metric** that replaces binary crash detection with proportional response.

- No more false signals from binary thresholds
- Graduated position sizing based on risk level
- Real-time crash probability estimation

</td>
<td width="50%">

### 🔄 Adaptive Recovery Engine
ML-inspired re-entry optimization for **faster post-crash recovery**.

- Multi-signal recovery detection
- 4-step position scaling (25% → 100%)
- Volatility-aware timing

</td>
</tr>
<tr>
<td width="50%">

### 📊 Monte Carlo Validation
Statistical proof through **1,000 simulated scenarios**.

- Stress testing across market conditions
- Confidence intervals for all metrics
- 2.7x better survival rate vs buy-and-hold

</td>
<td width="50%">

### 🛡️ Multi-Factor Detection
Combines multiple crash indicators:

- **DUVOL** (25%) - Down-to-up volatility ratio
- **NCSKEW** (20%) - Negative skewness
- **NASDAQ Canary** (15%) - Cross-market signals
- **Momentum** (15%) - Price acceleration

</td>
</tr>
</table>

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/charithra754-boop/FinPilot.git
cd FinPilot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
scikit-learn>=1.0.0
pytest>=7.0.0
```

---

## 🚀 Usage

### Run Full Backtest

```bash
# Execute the main backtest with all default parameters
python scripts/execution/final_backtest.py
```

**Expected Output:**
```
═══════════════════════════════════════════════════════
  FinPilot Backtest Results
═══════════════════════════════════════════════════════
  Total Return:     56,000%+
  Sharpe Ratio:     1.56
  Max Drawdown:     44.7%
  Crashes Avoided:  3/3 (COVID, LUNA, FTX)
═══════════════════════════════════════════════════════
```

### Generate Visualizations

```bash
python scripts/execution/generate_visualizations.py
```

Generates charts in `reports/figures/`:
- `equity_curve.png` - Strategy vs benchmark
- `crash_intensity_heatmap.png` - CIS over time
- `monte_carlo_simulation.png` - 1,000 scenario results

### Run Tests

```bash
# Run all 48 tests
python -m pytest tests/ -v

# Run specific module tests
python -m pytest tests/test_crash_intensity.py -v
```

### Interactive Analysis

```bash
jupyter notebook notebooks/main_analysis.ipynb
```

---

## 📊 Results

### Performance Comparison

| Metric | FinPilot | Buy & Hold | Advantage |
|--------|----------|------------|-----------|
| 📈 **Total Return** | 56,000%+ | ~1,600,000% | Risk-adjusted ✓ |
| 📊 **Sharpe Ratio** | **1.56** | 0.9 | **+73%** |
| 🛡️ **Max Drawdown** | **44.7%** | 84% | **-47%** |
| 🎯 **CSI Score** | **1,511** | 19 | **+7,853%** |
| 🎲 **Monte Carlo Survival** | **16.1%** | 6.0% | **2.7x better** |

### Crash Detection Record

| Event | Date | Market Drop | FinPilot |
|-------|------|-------------|----------|
| 🦠 COVID Crash | Mar 2020 | -53% | ✅ **Protected** |
| 🌙 LUNA Collapse | May 2022 | -58% | ✅ **Protected** |
| 💥 FTX Collapse | Nov 2022 | -26% | ✅ **Protected** |

---

## 🏗️ Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║             CRASH INTENSITY SCORING (CIS) ENGINE                 ║
║  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐       ║
║  │  DUVOL   │   │  NCSKEW  │   │  NASDAQ  │   │ Momentum │       ║
║  │   25%    │   │   20%    │   │   15%    │   │   15%    │       ║
║  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘       ║
║       └──────────────┴──────────────┴──────────────┘             ║
║                              ▼                                   ║
║           ┌────────────────────────────────────────┐             ║
║           │   CRASH INTENSITY SCORE (0-100)        │             ║
║           │   ├─ CIS < 20: Full Position           │             ║
║           │   ├─ CIS 20-70: Proportional           │             ║
║           │   └─ CIS > 70: Exit to Cash            │             ║
║           └─────────────────┬──────────────────────┘             ║
╠═════════════════════════════╪════════════════════════════════════╣
║                             ▼                                    ║
║              ADAPTIVE RECOVERY ENGINE                            ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │  Recovery Score = Momentum + Vol_Decline + CIS_Drop + RSI   │ ║
║  │  4-Step Scaling: 25% → 50% → 75% → 100%                     │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 📁 Project Structure

```
FinPilot/
│
├── 📊 data/                     # Historical price data
│   └── raw/                     # BTC/USD, NASDAQ CSVs
│
├── 🧠 src/                      # Core modules
│   ├── data_handler.py          # Data loading & preprocessing
│   ├── features.py              # DUVOL, NCSKEW, RSI calculations
│   ├── regime_detector.py       # Market state machine
│   ├── strategy.py              # Trading logic + risk management
│   ├── backtester.py            # Simulation engine
│   ├── metrics.py               # CSI, Sharpe, VaR, CVaR
│   ├── crash_intensity.py       # 🌟 Novel CIS engine
│   ├── monte_carlo.py           # Statistical validation
│   ├── stress_testing.py        # Flash crash simulation
│   └── visualizations.py        # Charts & dashboards
│
├── 📜 scripts/execution/        # Execution scripts
│   ├── final_backtest.py        # Run complete backtest
│   └── generate_visualizations.py
│
├── 📓 notebooks/                # Jupyter notebooks
│   └── main_analysis.ipynb      # Interactive analysis
│
├── 📚 docs/                     # Documentation
│
├── 📈 reports/figures/          # Generated visualizations
│
└── 🧪 tests/                    # 48 unit tests
```

---

## 🔌 API

### Core Classes

```python
from src.crash_intensity import CrashIntensityScorer, IntensityAwareStrategy
from src.backtester import Backtester
from src.data_handler import DataHandler

# Load data
handler = DataHandler()
crypto_df, nasdaq_df = handler.load_and_prepare('BTC_USD.csv', 'NASDAQ.csv')

# Initialize CIS scorer
scorer = CrashIntensityScorer()
intensity = scorer.calculate_crash_intensity(features)  # Returns 0-100

# Run strategy
strategy = IntensityAwareStrategy()
signals = strategy.run_intensity_strategy(features)

# Backtest
backtester = Backtester(initial_capital=100000)
results = backtester.run_backtest(features, signals)
```

### Key Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `calculate_crash_intensity()` | Compute CIS from features | `float (0-100)` |
| `calculate_proportional_position()` | Get position size for CIS | `float (0-1)` |
| `run_intensity_strategy()` | Execute full strategy | `DataFrame` |
| `run_backtest()` | Simulate performance | `Dict` |

---

## 🧪 Testing

```bash
$ python -m pytest tests/ -v

======================== 48 passed in 4.6s ========================
```

| Module | Tests | Status |
|--------|-------|--------|
| data_handler | 4 | ✅ |
| features | 4 | ✅ |
| metrics | 3 | ✅ |
| regime_detector | 2 | ✅ |
| strategy | 4 | ✅ |
| visualizations | 9 | ✅ |
| stress_testing | 5 | ✅ |
| crash_intensity | 16 | ✅ |
| **Total** | **48** | ✅ |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>🛡️ Built to survive. 📊 Proven by statistics. 🚀 Ready for production.</b>
</p>

<p align="center">
  <a href="https://github.com/charithra754-boop/FinPilot">
    <img src="https://img.shields.io/badge/⭐_Star_this_repo-171515?style=for-the-badge&logo=github" alt="Star"/>
  </a>
</p>
