# FinPilot Scripts

This directory contains executable scripts for running, optimizing, and validating the FinPilot trading strategy.

## Key Scripts

### 1. `run_backtest.py`
*   **Purpose:** Runs the strategy with **baseline parameters**.
*   **Use Case:** Quick check to see if the pipeline is working.
*   **Command:** `python scripts/run_backtest.py`

### 2. `advanced_tuning.py`
*   **Purpose:** Performs **Walk-Forward Optimization**.
*   **Logic:** Splits data into Train (2012-2020) and Test (2020-2024) to find robust parameters.
*   **Output:** Saves best parameters to `models/best_params.json`.
*   **Command:** `python scripts/advanced_tuning.py`

### 3. `final_backtest.py`
*   **Purpose:** Runs the **Final Verification** on the full dataset.
*   **Logic:** Loads optimized parameters from `models/best_params.json` and runs the strategy on 2012-2024 data.
*   **Command:** `python scripts/final_backtest.py`

## How to Run
Always run these scripts from the **project root directory** (`FinPilot/`) so that the imports (`src/`) and data paths (`data/raw/`) work correctly.

```bash
cd /path/to/FinPilot
python scripts/final_backtest.py
```
