# FinPilot Competition Presentation

## Arbitrage Arena 2026 | Problem 1: Surviving the Crypto Flash Crash

---

# Slide 1: Title

<div align="center">

# 🚀 FinPilot

### Next-Generation Crypto Trading with Flash Crash Survivability

**Arbitrage Arena 2026 | Problem 1**

| Metric | Value |
|--------|-------|
| Sharpe Ratio | **1.56** |
| Max Drawdown | **44.7%** |
| CSI Score | **1,511** |

</div>

---

# Slide 2: The Problem

## Why Crash Survivability Matters

| Challenge | Impact |
|-----------|--------|
| **Extreme Volatility** | BTC: 10-20x higher than equities |
| **Fat-Tailed Returns** | Crashes occur more frequently than predicted |
| **24/7 Trading** | No circuit breakers to dampen volatility |

### Historical Crashes
- **COVID (Mar 2020)**: -53% in days
- **LUNA (May 2022)**: -58% collapse  
- **FTX (Nov 2022)**: -26% sudden drop

**Goal**: Survive crashes while maintaining competitive returns

---

# Slide 3: Our Approach

## Hybrid Regime-Switching Model

```
┌─────────────────────────────────┐
│      LAYER 1: CRASH DETECTOR    │
│  DUVOL + NCSKEW + NASDAQ Canary │
└─────────────┬───────────────────┘
              ▼
┌─────────────────────────────────┐
│      LAYER 2: TRADING ENGINE    │
│   RSI + MA Crossover + Vol      │
└─────────────────────────────────┘
```

### State Machine
```
NORMAL → (crash signal) → CRASH → RECOVERY → (vol normalized) → NORMAL
```

---

# Slide 4: Key Innovation - Crash Intensity Score

## The Problem with Binary Detection

| Binary Approach | CIS Approach |
|-----------------|--------------|
| Crash OR No Crash | Continuous 0-100 Score |
| Whipsaw trades | Graduated response |
| Delayed reactions | Proportional sizing |

## CIS Formula

$$CIS = 0.25 \cdot DUVOL + 0.20 \cdot NCSKEW + 0.25 \cdot Vol + 0.15 \cdot Canary + 0.15 \cdot Momentum$$

---

# Slide 5: Proportional Position Sizing

## Graduated Response to Risk

| CIS Range | Position | Action |
|-----------|----------|--------|
| 0-20 | 100% | Full exposure |
| 20-50 | 50-100% | Gradual reduction |
| 50-70 | 20-50% | Defensive mode |
| 70-100 | 0-20% | Exit to cash |

**Key Advantage**: Response matches threat level — no binary overreaction

---

# Slide 6: Adaptive Recovery Engine

## Smart Re-Entry Algorithm

```python
recovery_score = (
    price_above_MA × 0.30 +      # Momentum recovering
    volatility_declining × 0.25 + # Market calming
    CIS_declining × 0.25 +        # Risk reducing  
    RSI_normalizing × 0.20        # Not oversold
)
```

### 4-Step Scaling Back In
| Step | Position | Rationale |
|------|----------|-----------|
| 1 | 25% | Test the waters |
| 2 | 50% | Confirm recovery |
| 3 | 75% | Build confidence |
| 4 | 100% | Full exposure |

---

# Slide 7: Data Processing

## Dataset Summary

| Asset | Period | Source |
|-------|--------|--------|
| BTC/USD | 2012-2024 | Bitfinex |
| NASDAQ 100 | 2012-2024 | Investing.com |

### Key Processing Steps
1. Parse non-standard formats (K/M/B suffixes)
2. Align timestamps (inner join)
3. Calculate returns & volatility
4. Forward-fill missing values

**Total**: 3,215 trading days

---

# Slide 8: Feature Engineering

## 12 Technical Indicators

| Category | Features |
|----------|----------|
| **Crash Indicators** | DUVOL, NCSKEW |
| **Momentum** | RSI, MA Crossover |
| **Volatility** | 10d, 30d rolling |
| **Cross-Market** | NASDAQ returns, Canary signal |

### DUVOL Formula
$$DUVOL = \log\left(\frac{\sigma_{down}}{\sigma_{up}}\right)$$

*Measures asymmetry between up/down volatility*

---

# Slide 9: Backtest Results

## Performance Summary (2012-2024)

| Metric | FinPilot | Buy & Hold |
|--------|----------|------------|
| **Total Return** | 67,633% | 1,658,748% |
| **Sharpe Ratio** | **1.56** | 0.9 |
| **Max Drawdown** | **44.7%** | 84% |
| **CSI Score** | **1,511** | 19 |

### Key Insight
Lower absolute return but **73% better Sharpe** and **47% less drawdown**

---

# Slide 10: Crash Detection Record

## All Major Crashes Detected ✅

| Event | Date | Market Drop | FinPilot |
|-------|------|-------------|----------|
| 🦠 COVID | Mar 2020 | -53% | ✅ Protected |
| 🌙 LUNA | May 2022 | -58% | ✅ Protected |
| 💥 FTX | Nov 2022 | -26% | ✅ Protected |

**Result**: Model exited to cash before each crash

---

# Slide 11: Walk-Forward Validation

## Out-of-Sample Testing

| Period | Type | Sharpe | Max DD |
|--------|------|--------|--------|
| 2012-2020 | Training | 1.39 | 45.2% |
| 2020-2024 | **Testing** | **1.81** | **23.9%** |

### Key Finding
**Model performed BETTER on unseen data!**

- All 4 major crashes in test period detected
- No overfitting evidence
- Parameters stable across regimes

---

# Slide 12: Monte Carlo Validation

## 1,000 Scenario Stress Test

| Metric | Strategy | Buy & Hold | Improvement |
|--------|----------|------------|-------------|
| **Survival Rate** | 16.1% | 6.0% | **2.7x better** |
| Median Drawdown | 69.3% | 84.8% | 15.5% less |

### Methodology
- Historical bootstrap with block sampling
- 1,000 synthetic market paths
- Survival = final value ≥ 50% initial

---

# Slide 13: Risk Metrics

## Comprehensive Risk Analysis

| Metric | Value |
|--------|-------|
| VaR (95%) | -3.2% daily |
| CVaR (95%) | -5.1% daily |
| Sortino Ratio | 1.69 |
| Calmar Ratio | 1.53 |

### Position Analysis
- Long: 61.2% of days
- Cash: 38.8% of days
- Total Trades: 265

---

# Slide 14: Competition Differentiators

## Why FinPilot Wins

| Feature | Typical Entry | FinPilot |
|---------|---------------|----------|
| Crash Detection | Binary threshold | **Continuous CIS (0-100)** |
| Position Sizing | Fixed | **Proportional to risk** |
| Recovery | Arbitrary wait | **Adaptive scoring** |
| Validation | Single backtest | **1,000 Monte Carlo** |
| Unit Tests | Minimal | **48 passing** |

---

# Slide 15: Conclusion

## Summary

### ✅ Key Achievements
1. **Crash Intensity Score** - Novel continuous risk metric
2. **Proportional Positioning** - Graduated response to risk
3. **Adaptive Recovery** - ML-inspired re-entry optimization
4. **Statistical Validation** - 2.7x better survival rate

### 📊 Results
- **Sharpe 1.56** outperforms benchmark risk-adjusted
- **CSI 1,511** proves crash survivability
- **Validated** on unseen data with 3 major crashes

---

<div align="center">

# 🛡️ Built to Survive. 📊 Proven by Statistics. 🏆 Designed to Win.

**FinPilot Team | December 2025**

</div>
