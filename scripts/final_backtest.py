#!/usr/bin/env python3
"""
FinPilot - Final Backtest with Optimized Parameters
Uses walk-forward validated parameters on FULL dataset
"""

import sys
sys.path.insert(0, 'src')

import json
from data_handler import DataHandler
from features import FeatureEngineer
from regime_detector import RegimeDetector
from strategy import TradingStrategy
from backtester import Backtester
from metrics import Metrics

print("=" * 70)
print("FINPILOT - FINAL BACKTEST (WALK-FORWARD OPTIMIZED PARAMETERS)")
print("=" * 70)

# Load optimized parameters
with open('models/best_params.json', 'r') as f:
    params = json.load(f)

print("\n📊 OPTIMIZED PARAMETERS:")
print("-" * 40)
print(f"  DUVOL Threshold:    {params['duvol_threshold']}")
print(f"  RSI Oversold:       {params['rsi_oversold']}")
print(f"  RSI Overbought:     {params['rsi_overbought']}")
print(f"  Stop Loss:          {params['stop_loss_pct']*100:.0f}%")
print(f"  NASDAQ Drop:        {params['nasdaq_drop_threshold']*100:.1f}%")
print(f"  Feature Window:     {params.get('feature_window', 20)} days")

# Load FULL dataset
print("\n[1] Loading Full Dataset...")
handler = DataHandler()
crypto_df, nasdaq_df = handler.load_and_prepare(
    'BTC_USD Bitfinex Historical Data.csv', 
    'Nasdaq 100 Historical Data.csv'
)
print(f"    Period: {crypto_df.index[0].strftime('%Y-%m-%d')} to {crypto_df.index[-1].strftime('%Y-%m-%d')}")
print(f"    Total days: {len(crypto_df)}")

# Generate features with optimized window
print("\n[2] Generating Features...")
window = params.get('feature_window', 20)
fe = FeatureEngineer(window=window)
features = fe.generate_all_features(crypto_df, nasdaq_df)
print(f"    Features: {features.shape[1]} indicators")
print(f"    Observations: {features.shape[0]} days")

# Detect regimes
print("\n[3] Detecting Market Regimes...")
detector = RegimeDetector(
    duvol_threshold=params['duvol_threshold'],
    nasdaq_drop_threshold=params['nasdaq_drop_threshold'],
    volatility_ratio_threshold=params.get('volatility_ratio_threshold', 1.0)
)
regimes = detector.detect_regimes(features)
normal = (regimes == 'normal').sum()
crash = (regimes == 'crash').sum()
recovery = (regimes == 'recovery').sum()
print(f"    Normal:   {normal:>5} days ({normal/len(regimes)*100:.1f}%)")
print(f"    Crash:    {crash:>5} days ({crash/len(regimes)*100:.1f}%)")
print(f"    Recovery: {recovery:>5} days ({recovery/len(regimes)*100:.1f}%)")

# Generate signals
print("\n[4] Generating Trading Signals...")
strategy = TradingStrategy(
    rsi_oversold=params['rsi_oversold'],
    rsi_overbought=params['rsi_overbought'],
    stop_loss_pct=params['stop_loss_pct'],
    volatility_target=params.get('volatility_target', 0.02)
)
signals = strategy.run_strategy(features, regimes)
long_days = (signals['position'] == 'LONG').sum()
cash_days = (signals['position'] == 'CASH').sum()
total_trades = (signals['signal'].diff() != 0).sum()
print(f"    Long positions: {long_days} days")
print(f"    Cash positions: {cash_days} days")
print(f"    Total trades:   {total_trades}")

# Run backtest
print("\n[5] Running Backtest (0.1% slippage)...")
backtester = Backtester(initial_capital=100000, slippage_pct=0.001)
results = backtester.run_backtest(features, signals)
benchmark = backtester.run_buy_and_hold(features)

# Calculate metrics
metrics_calc = Metrics(risk_free_rate=0.02)
equity = results['portfolio_value']
all_metrics = metrics_calc.calculate_all_metrics(equity)
summary = backtester.generate_summary(results, benchmark)

# BTC price change
btc_start = features['price'].iloc[0]
btc_end = features['price'].iloc[-1]
btc_return = (btc_end / btc_start - 1) * 100

# Print final results
print("\n" + "=" * 70)
print("🏆 FINAL BACKTEST RESULTS")
print("=" * 70)

print(f"""
┌────────────────────────────────────────────────────────────────────┐
│  MODEL: Hybrid Regime-Switching Strategy                          │
│  PERIOD: {features.index[0].strftime('%Y-%m-%d')} to {features.index[-1].strftime('%Y-%m-%d')} ({len(features)} days)             │
│  INITIAL CAPITAL: $100,000                                         │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  💰 PERFORMANCE                                                    │
├────────────────────────────────────────────────────────────────────┤
│  Strategy Return:       {all_metrics['total_return']:>12,.2f}%                          │
│  Buy & Hold Return:     {summary['benchmark_return']:>12,.2f}%                          │
│  BTC Price Change:      ${btc_start:.2f} → ${btc_end:,.2f}                      │
│  Final Portfolio:       ${equity.iloc[-1]:>15,.2f}                   │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  📉 RISK METRICS                                                   │
├────────────────────────────────────────────────────────────────────┤
│  Max Drawdown:          {all_metrics['max_drawdown']:>12.2f}%                          │
│  Volatility (Annual):   {all_metrics['volatility']:>12.2f}%                          │
│  CSI (Crash Surv.):     {all_metrics['csi']:>12.2f}                            │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  📊 RISK-ADJUSTED METRICS                                          │
├────────────────────────────────────────────────────────────────────┤
│  Sharpe Ratio:          {all_metrics['sharpe_ratio']:>12.2f}                            │
│  Sortino Ratio:         {all_metrics['sortino_ratio']:>12.2f}                            │
│  Calmar Ratio:          {all_metrics['calmar_ratio']:>12.2f}                            │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  🔄 TRADING ACTIVITY                                               │
├────────────────────────────────────────────────────────────────────┤
│  Total Trades:          {summary['total_trades']:>12}                            │
│  Transaction Costs:     ${summary['total_transaction_costs']:>15,.2f}                   │
│  Avg Trade Duration:    {len(features)//max(summary['total_trades'],1):>12} days                          │
└────────────────────────────────────────────────────────────────────┘
""")

print("=" * 70)
print("✅ BACKTEST COMPLETE - READY FOR COMPETITION!")
print("=" * 70)
