# Tests 🧪

Unit tests for the trading strategy modules.

## Running Tests

```bash
cd /home/cherry/FinPilot
pip install pytest
pytest tests/ -v
```

## Planned Tests

| Test File | Coverage |
|-----------|----------|
| `test_data_handler.py` | CSV parsing, timestamp alignment |
| `test_features.py` | DUVOL, NCSKEW calculations |
| `test_regime_detector.py` | State machine transitions |
| `test_strategy.py` | Signal generation, stop-loss |
| `test_metrics.py` | CSI, Sharpe, drawdown formulas |

## Coverage

Run with coverage report:
```bash
pytest tests/ --cov=src --cov-report=html
```
