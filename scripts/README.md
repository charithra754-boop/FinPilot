# Scripts 📜

Execution and utility scripts for FinPilot.

## Folder Structure

```
scripts/
├── README.md
│
├── execution/                     # Main execution scripts
│   ├── final_backtest.py          # Run full backtest
│   └── generate_visualizations.py # Generate all charts
│
├── advanced_tuning.py             # Parameter optimization
├── multi_asset_analysis.py        # Multi-asset correlation analysis
├── portfolio_backtest.py          # Portfolio-level backtest
└── run_backtest.py                # Quick backtest runner
```

## Execution Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `final_backtest.py` | Run complete backtest | `python scripts/execution/final_backtest.py` |
| `generate_visualizations.py` | Generate all charts | `python scripts/execution/generate_visualizations.py` |

## Utility Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `advanced_tuning.py` | Hyperparameter optimization | `python scripts/advanced_tuning.py` |
| `multi_asset_analysis.py` | Cross-asset correlation analysis | `python scripts/multi_asset_analysis.py` |
| `portfolio_backtest.py` | Multi-asset portfolio simulation | `python scripts/portfolio_backtest.py` |
| `run_backtest.py` | Quick single-asset backtest | `python scripts/run_backtest.py` |
