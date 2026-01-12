# Models 🧠

Saved model parameters and configurations.

## Purpose

Store tuned model parameters after optimization:
- DUVOL thresholds
- RSI overbought/oversold levels
- Stop-loss percentages
- Position sizing parameters

## Files

| File | Description | Status |
|------|-------------|--------|
| `best_params.json` | Optimized strategy parameters | ✅ Present |
| `regime_thresholds.json` | Crash detection thresholds | 📋 Planned |

## Usage

```python
import json

with open('models/best_params.json', 'r') as f:
    params = json.load(f)
    
strategy = TradingStrategy(**params)
```

## Parameters in `best_params.json`

Contains tuned values for:
- Trailing stop percentages
- Drawdown circuit breaker
- Position sizing multipliers
- CIS thresholds
