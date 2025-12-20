# Test Suite 🧪

Comprehensive unit tests ensuring reliability and correctness of all FinPilot modules.

## Test Summary

```bash
$ python -m pytest tests/ -v

======================== 48 passed in 4.6s ========================
```

## Test Coverage

| Test File | Module | Tests | Status |
|-----------|--------|-------|--------|
| `test_data_handler.py` | Data ingestion | 4 | ✅ |
| `test_features.py` | Feature engineering | 4 | ✅ |
| `test_regime_detector.py` | State machine | 2 | ✅ |
| `test_strategy.py` | Trading signals | 4 | ✅ |
| `test_metrics.py` | Performance metrics | 3 | ✅ |
| `test_visualizations.py` | Chart generation | 9 | ✅ |
| `test_stress_testing.py` | Stress scenarios | 5 | ✅ |
| `test_crash_intensity.py` | **CIS engine** | 16 | ✅ |
| **Total** | | **48** | ✅ |

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific module
python -m pytest tests/test_crash_intensity.py -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Key Test Categories

### 1. Crash Intensity Scoring (16 tests)
- CIS calculation accuracy
- Proportional position sizing
- Adaptive recovery engine
- Boundary conditions

### 2. Backtesting (4 tests)
- Equity curve calculation
- Transaction cost handling
- Drawdown computation
- Position tracking

### 3. Risk Metrics (3 tests)
- VaR/CVaR calculation
- Sharpe ratio accuracy
- Recovery time computation

## Testing Philosophy

- **No mocking data** - Tests use realistic synthetic data
- **Boundary testing** - Edge cases covered
- **Regression prevention** - All fixes include tests
- **Fast execution** - Full suite runs in < 5 seconds
