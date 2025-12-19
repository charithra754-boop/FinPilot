#!/usr/bin/env python3
"""
FinPilot - Run Full Backtest Pipeline
Shows actual performance metrics on real BTC/NASDAQ data
"""

import sys
sys.path.insert(0, 'src')

from data_handler import DataHandler
from features import FeatureEngineer
from regime_detector import RegimeDetector
from strategy import TradingStrategy
from backtester import Backtester
from metrics import Metrics

print("=" * 60)
print("FINPILOT - HYBRID REGIME-SWITCHING MODEL")
print("=" * 60)

# 1. Load Data
print("\n[1] Loading Data...")
handler = DataHandler()
crypto_df, nasdaq_df = handler.load_and_prepare(
    'BTC_USD Bitfinex Historical Data.csv', 
    'Nasdaq 100 Historical Data.csv'
)
print(f"    BTC Data: {crypto_df.shape[0]} days ({crypto_df.index[0].strftime('%Y-%m-%d')} to {crypto_df.index[-1].strftime('%Y-%m-%d')})")
print(f"    NASDAQ Data: {nasdaq_df.shape[0]} days")

# 2. Generate Features
print("\n[2] Generating Features...")
fe = FeatureEngineer(window=20)
features = fe.generate_all_features(crypto_df, nasdaq_df)
print(f"    Features: {features.shape[1]} indicators")
print(f"    Observations: {features.shape[0]} days")

# 3. Detect Regimes
print("\n[3] Detecting Market Regimes...")
detector = RegimeDetector(
    duvol_threshold=0.5,
    nasdaq_drop_threshold=-0.03,
    volatility_ratio_threshold=1.0
)
regimes = detector.detect_regimes(features)
print(f"    Normal periods: {(regimes == 'normal').sum()} days")
print(f"    Crash periods: {(regimes == 'crash').sum()} days")
print(f"    Recovery periods: {(regimes == 'recovery').sum()} days")

# 4. Generate Trading Signals
print("\n[4] Generating Trading Signals...")
strategy = TradingStrategy(
    rsi_oversold=30,
    rsi_overbought=70,
    stop_loss_pct=0.05,
    volatility_target=0.02
)
signals = strategy.run_strategy(features, regimes)
print(f"    Long positions: {(signals['position'] == 'LONG').sum()} days")
print(f"    Cash positions: {(signals['position'] == 'CASH').sum()} days")
print(f"    Total trades: {(signals['signal'].diff() != 0).sum()}")

# 5. Run Backtest
print("\n[5] Running Backtest (0.1% slippage)...")
backtester = Backtester(
    initial_capital=100000,
    slippage_pct=0.001
)
results = backtester.run_backtest(features, signals)
benchmark = backtester.run_buy_and_hold(features)

# 6. Calculate Metrics
print("\n[6] Calculating Performance Metrics...")
metrics_calc = Metrics(risk_free_rate=0.02)
equity = results['portfolio_value']
all_metrics = metrics_calc.calculate_all_metrics(equity)
summary = backtester.generate_summary(results, benchmark)

# Print Results
print("\n" + "=" * 60)
print("BACKTEST RESULTS")
print("=" * 60)

print(f"""
MODEL: Hybrid Regime-Switching Strategy
PERIOD: {features.index[0].strftime('%Y-%m-%d')} to {features.index[-1].strftime('%Y-%m-%d')}
INITIAL CAPITAL: $100,000

┌─────────────────────────────────────────────────────────────┐
│  PERFORMANCE                                                │
├─────────────────────────────────────────────────────────────┤
│  Strategy Return:     {all_metrics['total_return']:>10.2f}%                         │
│  Buy & Hold Return:   {summary['benchmark_return']:>10.2f}%                         │
│  Final Portfolio:     ${equity.iloc[-1]:>15,.2f}                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  RISK METRICS                                               │
├─────────────────────────────────────────────────────────────┤
│  Max Drawdown:        {all_metrics['max_drawdown']:>10.2f}%                         │
│  Volatility:          {all_metrics['volatility']:>10.2f}%                         │
│  CSI:                 {all_metrics['csi']:>10.2f}                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  RISK-ADJUSTED METRICS                                      │
├─────────────────────────────────────────────────────────────┤
│  Sharpe Ratio:        {all_metrics['sharpe_ratio']:>10.2f}                           │
│  Sortino Ratio:       {all_metrics['sortino_ratio']:>10.2f}                           │
│  Calmar Ratio:        {all_metrics['calmar_ratio']:>10.2f}                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  TRADING ACTIVITY                                           │
├─────────────────────────────────────────────────────────────┤
│  Total Trades:        {summary['total_trades']:>10}                           │
│  Transaction Costs:   ${summary['total_transaction_costs']:>15,.2f}                 │
└─────────────────────────────────────────────────────────────┘
""")

print("=" * 60)
print("BACKTEST COMPLETE")
print("=" * 60)
