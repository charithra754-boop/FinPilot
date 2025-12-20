# Scripts 📜

Execution and utility scripts for FinPilot.

## Folder Structure

```
scripts/
├── execution/              # Main execution scripts
│   ├── final_backtest.py   # Run full competition backtest
│   └── generate_visualizations.py
│
├── notebook_utils/         # Notebook helper scripts
│   ├── add_cis_notebook.py
│   ├── add_monte_carlo_notebook.py
│   └── update_notebook.py
│
└── README.md
```

## Execution Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `final_backtest.py` | Run complete backtest | `python scripts/execution/final_backtest.py` |
| `generate_visualizations.py` | Generate all charts | `python scripts/execution/generate_visualizations.py` |

## Notebook Utilities

Helper scripts for programmatically updating the Jupyter notebook:

| Script | Purpose |
|--------|---------|
| `add_cis_notebook.py` | Add CIS methodology section |
| `add_monte_carlo_notebook.py` | Add Monte Carlo section |
| `update_notebook.py` | Add stress testing section |
