# Notebooks 📓

Interactive Jupyter notebooks for analysis.

## Main Analysis

**`main_analysis.ipynb`** - The main analysis notebook.

### Features

- **Interactive visualizations** embedded
- **Complete pipeline** from data loading to backtest
- **Key metrics** and performance analysis

### Sections

| # | Section | Content |
|---|---------|---------|
| 1 | Introduction | Problem statement, model overview |
| 2 | Data Import | Loading BTC & NASDAQ data |
| 3 | Feature Engineering | DUVOL, NCSKEW, RSI, volatility |
| 4 | Regime Classification | Normal/Crash/Recovery detection |
| 5 | Strategy Design | Trading rules, risk management |
| 6 | Backtesting | Simulation with transaction costs |
| 7 | **Crash Intensity Scoring** | 🌟 Novel CIS methodology |
| 8 | **Stress Testing** | Flash crash, VaR, Monte Carlo |
| 9 | Evaluation Metrics | CSI, Sharpe, Max Drawdown |
| 10 | Conclusion | Results summary, future work |

## Running the Notebook

```bash
cd /home/cherry/Projects/FinPilot
jupyter notebook notebooks/main_analysis.ipynb
```

## Generated Figures

The notebook generates and saves figures to `../reports/figures/`:

| Figure | Purpose |
|--------|---------|
| `crash_intensity_heatmap.png` | CIS visualization |
| `monte_carlo_simulation.png` | Statistical validation |
| `stress_performance.png` | Crash scenario comparison |
| `var_distribution.png` | Risk metric visualization |
