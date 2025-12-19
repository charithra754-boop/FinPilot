# Source Code 📦

Core Python modules for the trading strategy.

## Modules

| Module | Purpose |
|--------|---------|
| `data_handler.py` | Load and preprocess CSV data from Investing.com |
| `features.py` | Feature engineering (DUVOL, NCSKEW, RSI, MA) |
| `regime_detector.py` | Detect market regimes (Normal/Crash/Recovery) |
| `strategy.py` | Trading strategy with risk management |
| `backtester.py` | Backtest simulation with transaction costs |
| `metrics.py` | Calculate CSI, Sharpe, Max Drawdown |

## Architecture

```
┌─────────────────┐
│  DataHandler    │  Load & clean data
└────────┬────────┘
         ▼
┌─────────────────┐
│ FeatureEngineer │  Calculate indicators
└────────┬────────┘
         ▼
┌─────────────────┐
│ RegimeDetector  │  Detect market state
└────────┬────────┘
         ▼
┌─────────────────┐
│ TradingStrategy │  Generate signals
└────────┬────────┘
         ▼
┌─────────────────┐
│   Backtester    │  Simulate trades
└────────┬────────┘
         ▼
┌─────────────────┐
│    Metrics      │  Evaluate performance
└─────────────────┘
```

## Quick Test

```bash
cd /home/cherry/FinPilot
python src/data_handler.py
```
