# API Reference 🔧

Module documentation for FinPilot source code.

## Core Modules

| Module | Class | Purpose |
|--------|-------|---------|
| `data_handler.py` | `DataHandler` | CSV ingestion, timestamp alignment |
| `features.py` | `FeatureEngineer` | DUVOL, NCSKEW, RSI, volatility |
| `regime_detector.py` | `RegimeDetector` | Normal/Crash/Recovery state machine |
| `strategy.py` | `TradingStrategy` | Signal generation, risk management |
| `backtester.py` | `Backtester` | Historical simulation |
| `metrics.py` | `Metrics` | CSI, Sharpe, VaR, CVaR |

## Novel Modules

| Module | Class | Purpose |
|--------|-------|---------|
| `crash_intensity.py` | `CrashIntensityScorer` | 🌟 Continuous 0-100 risk scoring |
| `crash_intensity.py` | `AdaptiveRecoveryEngine` | Smart re-entry optimization |
| `monte_carlo.py` | `MonteCarloSimulator` | 1,000 scenario validation |
| `stress_testing.py` | `StressTestScenarios` | Flash crash simulation |

## Quick Usage

```python
from crash_intensity import CrashIntensityScorer

scorer = CrashIntensityScorer()
cis = scorer.calculate_crash_intensity(features)
# Returns: 0-100 (higher = more dangerous)
```

## Full Documentation

Each module contains comprehensive docstrings. Use:
```python
help(CrashIntensityScorer)
```
