# Models 🧠

Saved model parameters and configurations.

## Purpose

Store tuned model parameters after optimization:
- DUVOL thresholds
- RSI overbought/oversold levels
- Stop-loss percentages
- Position sizing parameters

## Planned Files

| File | Description |
|------|-------------|
| `best_params.json` | Optimized strategy parameters |
| `regime_thresholds.json` | Crash detection thresholds |

## Usage

```python
import json

with open('models/best_params.json', 'r') as f:
    params = json.load(f)
    
strategy = TradingStrategy(**params)
```
