# Changelog

All notable changes to FinPilot are documented here.

## [1.0.0] - 2025-12-19

### 🏆 Competition Release

#### Added
- **Phase 5**: Visualization module with equity curves, regime heatmaps, and performance dashboards
- **Phase 6**: Competition package with polished notebook and final submission report
- Comprehensive 15-page competition report
- 26 unit tests with 100% pass rate

#### Performance
- Total Return: 67,633%
- Sharpe Ratio: 1.56
- Max Drawdown: 44.74%
- CSI: 1,511

---

## [0.4.0] - 2025-12-19

### Phase 4: Unit Tests

#### Added
- Unit tests for all core modules
- Test coverage for data handling, features, regime detection, strategy, backtesting, metrics

---

## [0.3.0] - 2025-12-19

### Phase 3: Multi-Asset Support

#### Added
- ETH/USD support alongside BTC
- Portfolio backtesting with volatility-weighted allocation
- 60/40 BTC/ETH default allocation

#### Improved
- Reduced max drawdown to 28% with diversification

---

## [0.2.5] - 2025-12-19

### Phase 2.5: Walk-Forward Validation

#### Added
- Train/test split validation (2012-2020 / 2020-2024)
- Grid search optimization (540 parameter combinations)
- Saved best parameters to `models/best_params.json`

#### Validated
- Out-of-sample Sharpe: 1.81 (better than in-sample 1.39)
- All major crashes detected on unseen data

---

## [0.2.0] - 2025-12-19

### Phase 2: Optimization

#### Added
- Grid search parameter optimization
- DUVOL threshold tuning
- RSI parameter optimization

---

## [0.1.0] - 2025-12-19

### Phase 1: Baseline

#### Added
- Core trading strategy implementation
- Regime detection (DUVOL, NCSKEW, Canary)
- Basic backtesting engine
- Initial metrics calculation
