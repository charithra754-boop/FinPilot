# Notebooks 📓

Jupyter notebooks for analysis and competition submission.

## Files

| Notebook | Purpose |
|----------|---------|
| `main_analysis.ipynb` | **Competition submission** - Full pipeline demo |

## Running

```bash
cd /home/cherry/FinPilot
jupyter notebook notebooks/main_analysis.ipynb
```

## Notebook Structure

1. **Setup** - Import libraries and modules
2. **Data Loading** - Load and prepare BTC + NASDAQ data
3. **Feature Engineering** - Calculate DUVOL, NCSKEW, Canary
4. **Regime Detection** - Identify Normal/Crash/Recovery periods
5. **Strategy Execution** - Generate trading signals
6. **Backtesting** - Simulate trades with 0.1% slippage
7. **Evaluation** - Calculate CSI, Sharpe, Max Drawdown
8. **Visualization** - Equity curves, drawdowns, regime overlay
9. **Executive Summary** - Competition results

## Tips

- Restart kernel and run all cells before submission
- Check that all visualizations render correctly
- LaTeX formulas should display properly in Markdown cells
