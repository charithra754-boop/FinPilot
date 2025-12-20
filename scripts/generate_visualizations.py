#!/usr/bin/env python3
"""
FinPilot - Generate Visualizations for Phase 5
Creates equity curves, regime heatmaps, and performance dashboards.
"""

import sys
sys.path.insert(0, 'src')

import json
from pathlib import Path
from data_handler import DataHandler
from features import FeatureEngineer
from regime_detector import RegimeDetector
from strategy import TradingStrategy
from backtester import Backtester
from metrics import Metrics
from visualizations import StrategyVisualizer

print("=" * 70)
print("  FinPilot | Phase 5: Visualization Generation")
print("=" * 70)

# Load optimized parameters
print("\n[1] Loading Optimized Parameters...")
params_path = Path("models/best_params.json")
if params_path.exists():
    with open(params_path) as f:
        params = json.load(f)
    print(f"    Loaded from: {params_path}")
else:
    params = {
        "duvol_threshold": 0.5,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "feature_window": 20
    }
    print("    Using default parameters")

# Load data
print("\n[2] Loading Historical Data...")
handler = DataHandler()
crypto_df, nasdaq_df = handler.load_and_prepare(
    'BTC_USD Bitfinex Historical Data.csv',
    'Nasdaq 100 Historical Data.csv'
)
print(f"    Period: {crypto_df.index[0].strftime('%Y-%m-%d')} to {crypto_df.index[-1].strftime('%Y-%m-%d')}")
print(f"    Total days: {len(crypto_df)}")

# Generate features
print("\n[3] Generating Features...")
window = params.get('feature_window', 20)
fe = FeatureEngineer(window=window)
features = fe.generate_all_features(crypto_df, nasdaq_df)
print(f"    Features: {features.shape[1]} indicators")

# Detect regimes
print("\n[4] Detecting Market Regimes...")
detector = RegimeDetector(
    duvol_threshold=params.get('duvol_threshold', 0.5)
)
regimes = detector.detect_regimes(features)
regime_counts = regimes.value_counts()
print(f"    Normal: {regime_counts.get('normal', 0)} days")
print(f"    Crash:  {regime_counts.get('crash', 0)} days")  
print(f"    Recovery: {regime_counts.get('recovery', 0)} days")

# Run strategy
print("\n[5] Running Strategy...")
strategy = TradingStrategy(
    rsi_oversold=params.get('rsi_oversold', 30),
    rsi_overbought=params.get('rsi_overbought', 70)
)
signals = strategy.run_strategy(features, regimes)

# Run backtest
print("\n[6] Running Backtest...")
backtester = Backtester(initial_capital=100000, slippage_pct=0.001)
results = backtester.run_backtest(features, signals)

# Get equity curves
equity = backtester.calculate_equity_curve(results)

# Run benchmark
benchmark_results = backtester.run_buy_and_hold(features)
benchmark = backtester.calculate_equity_curve(benchmark_results)

# Calculate metrics
print("\n[7] Calculating Metrics...")
metrics_calc = Metrics()
all_metrics = metrics_calc.calculate_all_metrics(equity)

# Add benchmark metrics
benchmark_metrics = metrics_calc.calculate_all_metrics(benchmark)
all_metrics['benchmark_return'] = benchmark_metrics.get('total_return', 0)
all_metrics['benchmark_sharpe'] = benchmark_metrics.get('sharpe_ratio', 0)
all_metrics['benchmark_drawdown'] = benchmark_metrics.get('max_drawdown', 0)

# Get summary for trades
summary = backtester.generate_summary(results, benchmark_results)
all_metrics['total_trades'] = summary.get('total_trades', 0)

print(f"    Sharpe Ratio: {all_metrics['sharpe_ratio']:.2f}")
print(f"    Max Drawdown: {all_metrics['max_drawdown']*100:.1f}%")
print(f"    Total Return: {all_metrics['total_return']:,.0f}%")

# Generate visualizations
print("\n[8] Generating Visualizations...")
viz = StrategyVisualizer()

# Get prices for regime heatmap
prices = features['price'].copy()

# 1. Equity Curve
print("    → Equity Curve...")
fig1 = viz.plot_equity_curve(equity, benchmark, all_metrics)
path1 = viz.save_figure(fig1, "equity_curve")
print(f"       Saved: {path1}")

# 2. Regime Heatmap
print("    → Regime Heatmap...")
fig2 = viz.plot_regime_heatmap(regimes, prices)
path2 = viz.save_figure(fig2, "regime_heatmap")
print(f"       Saved: {path2}")

print("    → Performance Dashboard...")
fig3 = viz.plot_performance_dashboard(
    equity, benchmark, regimes, prices, all_metrics
)
path3 = viz.save_figure(fig3, "performance_dashboard")
print(f"       Saved: {path3}")

# 4. Stress Testing Visualizations
print("\n[9] Generating Stress Testing Visualizations...")
from stress_testing import StressTestScenarios

stress_tester = StressTestScenarios(random_seed=42)

# Generate flash crash scenario
print("    → Flash Crash Scenario...")
flash_crash = stress_tester.generate_flash_crash(prices, drop_pct=0.20, duration_days=3)

# Create stress features and run backtest on stress scenario
stress_features = features.copy()
stress_features["price"] = flash_crash.prices
stress_features["returns"] = flash_crash.prices.pct_change()
stress_features["volatility_10d"] = stress_features["returns"].rolling(10).std()
stress_features["volatility_30d"] = stress_features["returns"].rolling(30).std()

stress_regimes = detector.detect_regimes(stress_features)
stress_signals = strategy.run_strategy(stress_features, stress_regimes)
stress_results = backtester.run_backtest(stress_features, stress_signals)
stress_equity = backtester.calculate_equity_curve(stress_results)

# 4a. Stress Performance Chart
print("    → Stress Performance Chart...")
fig4 = viz.plot_stress_performance(
    equity, stress_equity, 
    flash_crash.name,
    flash_crash.stress_start,
    flash_crash.stress_end
)
path4 = viz.save_figure(fig4, "stress_performance")
print(f"       Saved: {path4}")

# 4b. VaR Distribution
print("    → VaR Distribution Chart...")
returns = equity.pct_change().dropna()
fig5 = viz.plot_var_distribution(
    returns,
    var_95=all_metrics['var_95'] / 100,
    var_99=all_metrics['var_99'] / 100,
    cvar_95=all_metrics['cvar_95'] / 100
)
path5 = viz.save_figure(fig5, "var_distribution")
print(f"       Saved: {path5}")

# 4c. Drawdown Recovery
print("    → Drawdown Recovery Chart...")
fig6 = viz.plot_drawdown_recovery(equity)
path6 = viz.save_figure(fig6, "drawdown_recovery")
print(f"       Saved: {path6}")

# 4d. Volatility Regime Performance
print("    → Volatility Regime Performance...")
volatility = features['volatility_30d']
fig7 = viz.plot_volatility_regime_performance(equity, volatility, vol_threshold=0.03)
path7 = viz.save_figure(fig7, "volatility_regimes")
print(f"       Saved: {path7}")

print("\n" + "=" * 70)
print("✅ VISUALIZATION GENERATION COMPLETE!")
print("=" * 70)
print(f"""
Generated files:
  1. {path1} - Equity curve with drawdown
  2. {path2} - Regime timeline heatmap
  3. {path3} - Comprehensive performance dashboard
  4. {path4} - Stress test performance (Flash Crash)
  5. {path5} - VaR distribution with risk metrics
  6. {path6} - Drawdown recovery timeline
  7. {path7} - Volatility regime performance

Key Metrics:
  • Total Return: {all_metrics['total_return']:,.0f}%
  • Sharpe Ratio: {all_metrics['sharpe_ratio']:.2f}
  • Max Drawdown: {all_metrics['max_drawdown']*100:.1f}%
  • VaR 95%: {all_metrics['var_95']:.2f}%
  • VaR 99%: {all_metrics['var_99']:.2f}%
  • CVaR 95%: {all_metrics['cvar_95']:.2f}%
""")
